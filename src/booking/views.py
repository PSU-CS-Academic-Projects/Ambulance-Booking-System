from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField
from datetime import timedelta, date

from .models import (
    UserProfile, Booking, Ambulance, Driver, Patient,
    EmergencyType, BookingStatusLog
)
from .forms import (
    RegistrationForm, BookingForm, AssignBookingForm,
    AmbulanceForm, DriverStatusForm
)


# ─────────────────────────────────────────────
# DECORATORS — Role-based access control
# ─────────────────────────────────────────────

def role_required(role):
    """
    Custom decorator that checks if the logged-in user has the required role.
    Usage: @role_required('admin')
    If user doesn't have the role, redirect to /forbidden/
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                if request.user.profile.role == role or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
            except UserProfile.DoesNotExist:
                pass
            return redirect('forbidden')
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator


def log_status_change(booking, new_status, updated_by, notes=''):
    """
    Helper: every time a booking status changes, create a log entry.
    Call this function whenever you update booking.status.
    """
    BookingStatusLog.objects.create(
        booking=booking,
        status=new_status,
        updated_by=updated_by,
        notes=notes,
    )


# ─────────────────────────────────────────────
# AUTHENTICATION VIEWS
# ─────────────────────────────────────────────

def register_view(request):
    """
    Registration page.
    GET: show the blank form.
    POST: validate and save the new user + profile.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to DB yet
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()  # Now save

            role = form.cleaned_data['role']
            phone = form.cleaned_data.get('phone', '')

            # Create the UserProfile
            profile = UserProfile.objects.create(user=user, role=role, phone=phone)

            # Create role-specific profile
            if role == 'patient':
                Patient.objects.create(user=user)
            elif role == 'driver':
                Driver.objects.create(
                    user=user,
                    license_number='PENDING',
                    contact_number=phone or 'PENDING'
                )

            login(request, user)  # Log them in immediately
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def dashboard_redirect(request):
    """
    After login, redirect each role to their own dashboard.
    This is the LOGIN_REDIRECT_URL target.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_superuser:
        return redirect('admin_dashboard')

    try:
        role = request.user.profile.role
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'driver':
            return redirect('driver_dashboard')
        else:
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('patient_dashboard')


def forbidden_view(request):
    """403 Forbidden page."""
    return render(request, 'registration/forbidden.html', status=403)


# ─────────────────────────────────────────────
# PATIENT VIEWS
# ─────────────────────────────────────────────

@login_required
@role_required('patient')
def patient_dashboard(request):
    """
    Patient's home screen.
    Shows their active booking (if any) and recent history.
    """
    active_bookings = Booking.objects.filter(
        patient=request.user
    ).exclude(status__in=['completed', 'cancelled'])

    recent_bookings = Booking.objects.filter(
        patient=request.user,
        status__in=['completed', 'cancelled']
    )[:5]

    return render(request, 'booking/patient/dashboard.html', {
        'active_bookings': active_bookings,
        'recent_bookings': recent_bookings,
    })


@login_required
@role_required('patient')
def new_booking(request):
    """
    Patient submits a new ambulance request.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.patient = request.user
            booking.status = 'pending'
            booking.save()

            # Log the initial status
            log_status_change(booking, 'pending', request.user, 'Booking created by patient')

            messages.success(request, 'Your ambulance request has been submitted! Please wait for dispatch.')
            return redirect('booking_detail_patient', pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, 'booking/patient/new_booking.html', {'form': form})


@login_required
@role_required('patient')
def booking_detail_patient(request, pk):
    """
    Patient views their booking status and details.
    Auto-refreshes via JavaScript every 30 seconds.
    """
    booking = get_object_or_404(Booking, pk=pk, patient=request.user)
    status_logs = booking.status_logs.all()

    return render(request, 'booking/patient/booking_detail.html', {
        'booking': booking,
        'status_logs': status_logs,
    })


@login_required
@role_required('patient')
def booking_history(request):
    """All past bookings for the current patient."""
    bookings = Booking.objects.filter(patient=request.user)
    return render(request, 'booking/patient/booking_history.html', {'bookings': bookings})


@login_required
def booking_status_json(request, pk):
    """
    Returns the current booking status as JSON.
    Called by JavaScript fetch() every 30 seconds — no page reload needed.
    """
    booking = get_object_or_404(Booking, pk=pk, patient=request.user)
    return JsonResponse({
        'status': booking.status,
        'status_display': booking.get_status_display(),
        'ambulance': str(booking.assigned_ambulance) if booking.assigned_ambulance else None,
        'driver': str(booking.assigned_driver) if booking.assigned_driver else None,
    })


# ─────────────────────────────────────────────
# ADMIN VIEWS
# ─────────────────────────────────────────────

@login_required
@role_required('admin')
def admin_dashboard(request):
    """
    Admin's main dashboard with stat cards and recent bookings.
    """
    today = date.today()

    # Stat cards
    active_count = Booking.objects.exclude(status__in=['completed', 'cancelled']).count()
    today_count = Booking.objects.filter(requested_time__date=today).count()
    available_ambulances = Ambulance.objects.filter(status='available').count()

    # Average response time (dispatched → completed), in minutes
    completed = Booking.objects.filter(
        status='completed',
        dispatched_time__isnull=False,
        completed_time__isnull=False
    )
    avg_response = None
    if completed.exists():
        total_mins = sum(
            (b.completed_time - b.dispatched_time).total_seconds() / 60
            for b in completed
        )
        avg_response = round(total_mins / completed.count(), 1)

    recent_bookings = Booking.objects.all()[:10]

    return render(request, 'booking/admin/dashboard.html', {
        'active_count': active_count,
        'today_count': today_count,
        'available_ambulances': available_ambulances,
        'avg_response': avg_response,
        'recent_bookings': recent_bookings,
    })


@login_required
@role_required('admin')
def admin_bookings_list(request):
    """
    All bookings with optional filters by status and date.
    """
    bookings = Booking.objects.all()

    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_filter:
        bookings = bookings.filter(requested_time__date=date_filter)

    status_choices = Booking.STATUS_CHOICES

    return render(request, 'booking/admin/bookings_list.html', {
        'bookings': bookings,
        'status_choices': status_choices,
        'status_filter': status_filter,
        'date_filter': date_filter,
    })


@login_required
@role_required('admin')
def admin_booking_detail(request, pk):
    """
    Admin views a booking and can assign ambulance/driver.
    """
    booking = get_object_or_404(Booking, pk=pk)
    status_logs = booking.status_logs.all()

    if request.method == 'POST':
        form = AssignBookingForm(request.POST, instance=booking)
        if form.is_valid():
            old_status = booking.status
            updated = form.save(commit=False)

            # Set dispatched time when status changes to dispatched
            if updated.status == 'dispatched' and old_status != 'dispatched':
                updated.dispatched_time = timezone.now()

                # Mark ambulance and driver as on_call
                if updated.assigned_ambulance:
                    updated.assigned_ambulance.status = 'on_call'
                    updated.assigned_ambulance.save()
                if updated.assigned_driver:
                    updated.assigned_driver.is_available = False
                    updated.assigned_driver.save()

            updated.save()

            if updated.status != old_status:
                log_status_change(booking, updated.status, request.user,
                                  f'Updated by admin: {request.user.username}')

            messages.success(request, 'Booking updated successfully.')
            return redirect('admin_booking_detail', pk=pk)
    else:
        form = AssignBookingForm(instance=booking)

    return render(request, 'booking/admin/booking_detail.html', {
        'booking': booking,
        'form': form,
        'status_logs': status_logs,
    })


@login_required
@role_required('admin')
def admin_fleet(request):
    """List all ambulance units."""
    ambulances = Ambulance.objects.all()
    return render(request, 'booking/admin/fleet.html', {'ambulances': ambulances})


@login_required
@role_required('admin')
def admin_ambulance_add(request):
    """Add a new ambulance unit."""
    if request.method == 'POST':
        form = AmbulanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance unit added.')
            return redirect('admin_fleet')
    else:
        form = AmbulanceForm()
    return render(request, 'booking/admin/ambulance_form.html', {'form': form, 'action': 'Add'})


@login_required
@role_required('admin')
def admin_ambulance_edit(request, pk):
    """Edit an existing ambulance unit."""
    ambulance = get_object_or_404(Ambulance, pk=pk)
    if request.method == 'POST':
        form = AmbulanceForm(request.POST, instance=ambulance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ambulance unit updated.')
            return redirect('admin_fleet')
    else:
        form = AmbulanceForm(instance=ambulance)
    return render(request, 'booking/admin/ambulance_form.html', {'form': form, 'action': 'Edit'})


@login_required
@role_required('admin')
def admin_drivers(request):
    """List all drivers."""
    drivers = Driver.objects.select_related('user', 'assigned_ambulance').all()
    return render(request, 'booking/admin/drivers.html', {'drivers': drivers})


@login_required
@role_required('admin')
def admin_patients(request):
    """List all patients."""
    patients = Patient.objects.select_related('user').all()
    return render(request, 'booking/admin/patients.html', {'patients': patients})


@login_required
@role_required('admin')
def admin_reports(request):
    """Basic reports page — bookings per day for the last 7 days."""
    today = date.today()
    report_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Booking.objects.filter(requested_time__date=day).count()
        completed = Booking.objects.filter(requested_time__date=day, status='completed').count()
        report_data.append({
            'date': day.strftime('%b %d'),
            'total': count,
            'completed': completed,
        })

    return render(request, 'booking/admin/reports.html', {'report_data': report_data})


# ─────────────────────────────────────────────
# DRIVER VIEWS
# ─────────────────────────────────────────────

@login_required
@role_required('driver')
def driver_dashboard(request):
    """
    Driver sees their currently assigned booking.
    """
    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        messages.error(request, 'Driver profile not found. Contact admin.')
        return redirect('forbidden')

    # Get the most recent active booking assigned to this driver
    active_booking = Booking.objects.filter(
        assigned_driver=driver
    ).exclude(status__in=['completed', 'cancelled']).first()

    form = DriverStatusForm()

    return render(request, 'booking/driver/dashboard.html', {
        'driver': driver,
        'active_booking': active_booking,
        'form': form,
    })


@login_required
@role_required('driver')
def driver_update_status(request, pk):
    """
    Driver updates the booking status (En Route, Arrived, etc.)
    """
    booking = get_object_or_404(Booking, pk=pk)

    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        return redirect('forbidden')

    # Security check: this driver must be the assigned one
    if booking.assigned_driver != driver:
        return redirect('forbidden')

    if request.method == 'POST':
        form = DriverStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            old_status = booking.status

            booking.status = new_status

            # If completed, record completion time and free up ambulance/driver
            if new_status == 'completed':
                booking.completed_time = timezone.now()
                if booking.assigned_ambulance:
                    booking.assigned_ambulance.status = 'available'
                    booking.assigned_ambulance.save()
                driver.is_available = True
                driver.save()

            booking.save()

            if new_status != old_status:
                log_status_change(booking, new_status, request.user,
                                  f'Updated by driver: {request.user.username}')

            messages.success(request, f'Status updated to: {booking.get_status_display()}')

    return redirect('driver_dashboard')