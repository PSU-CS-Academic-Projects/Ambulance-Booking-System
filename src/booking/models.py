from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extends Django's built-in User model.
    Django's User already has: username, password, email, first_name, last_name.
    We add: role (admin/patient/driver) and phone number.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('patient', 'Patient'),
        ('driver', 'Driver'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,   # If the user is deleted, delete the profile too
        related_name='profile'      # Access via: user.profile
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class EmergencyType(models.Model):
    """
    Types of emergencies: Cardiac Arrest, Accident, Stroke, etc.
    Admin can add more through the admin panel.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Ambulance(models.Model):
    """
    Each ambulance unit in the fleet.
    """
    TYPE_CHOICES = [
        ('BLS', 'Basic Life Support'),
        ('ALS', 'Advanced Life Support'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_call', 'On Call'),
        ('en_route', 'En Route'),
        ('maintenance', 'Maintenance'),
    ]

    unit_number = models.CharField(max_length=20, unique=True)
    plate_number = models.CharField(max_length=20, unique=True)
    ambulance_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='BLS')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.unit_number} — {self.plate_number} ({self.get_status_display()})"


class Driver(models.Model):
    """
    A driver is a User with role='driver', plus extra info.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=20)
    assigned_ambulance = models.OneToOneField(
        Ambulance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_driver'
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Driver: {self.user.get_full_name() or self.user.username}"


class Patient(models.Model):
    """
    A patient is a User with role='patient', plus medical info.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class Booking(models.Model):
    """
    The core model — one booking = one ambulance request.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('en_route', 'En Route'),
        ('arrived', 'Arrived at Scene'),
        ('transporting', 'Transporting'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Who is requesting
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Location details
    pickup_address = models.TextField()
    destination_hospital = models.CharField(max_length=200)

    # Emergency info
    emergency_type = models.ForeignKey(
        EmergencyType,
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Assignment (set by admin)
    assigned_ambulance = models.ForeignKey(
        Ambulance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )

    # Timestamps
    requested_time = models.DateTimeField(default=timezone.now)
    dispatched_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_time']  # Newest first

    def __str__(self):
        return f"Booking #{self.pk} — {self.patient.username} ({self.status})"

    def response_time_minutes(self):
        """Calculate how long from dispatch to completion."""
        if self.dispatched_time and self.completed_time:
            delta = self.completed_time - self.dispatched_time
            return round(delta.total_seconds() / 60, 1)
        return None


class BookingStatusLog(models.Model):
    """
    Records every status change for a booking.
    This gives us a full history/timeline.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Booking #{self.booking.pk} → {self.status} at {self.timestamp}"