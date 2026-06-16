from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Booking, EmergencyType, Ambulance, Driver, Patient


class RegistrationForm(UserCreationForm):
    """
    Extended registration form that also captures role and phone.
    UserCreationForm already has: username, password1, password2
    We add: first_name, last_name, email, phone, role
    """
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(
        choices=[('patient', 'Patient / Requester'), ('driver', 'Driver')],
        # Note: 'admin' role is not self-registerable for security
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'phone', 'role']


class BookingForm(forms.ModelForm):
    """
    Form for patients to create a new booking.
    """
    class Meta:
        model = Booking
        fields = ['pickup_address', 'destination_hospital', 'emergency_type', 'notes']
        widgets = {
            'pickup_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your exact pickup address'}),
            'destination_hospital': forms.TextInput(attrs={'placeholder': 'e.g. Philippine General Hospital'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional information for the driver...'}),
        }


class AssignBookingForm(forms.ModelForm):
    """
    Admin form to assign ambulance and driver to a booking.
    Only shows available ambulances and available drivers.
    """
    class Meta:
        model = Booking
        fields = ['assigned_ambulance', 'assigned_driver', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to only show available units
        self.fields['assigned_ambulance'].queryset = Ambulance.objects.filter(status='available')
        self.fields['assigned_driver'].queryset = Driver.objects.filter(is_available=True)


class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = ['unit_number', 'plate_number', 'ambulance_type', 'status', 'notes']


class DriverStatusForm(forms.Form):
    """Simple form for driver to update their booking status."""
    STATUS_CHOICES = [
        ('en_route', 'En Route to Scene'),
        ('arrived', 'Arrived at Scene'),
        ('transporting', 'Transporting Patient'),
        ('completed', 'Completed'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)