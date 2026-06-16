from django.contrib import admin
from .models import (
    UserProfile, EmergencyType, Ambulance, Driver,
    Patient, Booking, BookingStatusLog
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(EmergencyType)
class EmergencyTypeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'plate_number', 'ambulance_type', 'status']
    list_filter = ['status', 'ambulance_type']
    list_editable = ['status']
    search_fields = ['unit_number', 'plate_number']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'contact_number', 'assigned_ambulance', 'is_available']
    list_filter = ['is_available']
    list_editable = ['is_available']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'emergency_contact_name', 'emergency_contact_number']
    search_fields = ['user__username', 'user__first_name']

class BookingStatusLogInline(admin.TabularInline):
    model = BookingStatusLog
    extra = 0
    readonly_fields = ['timestamp', 'updated_by', 'status', 'notes']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'patient', 'emergency_type', 'status',
                    'assigned_ambulance', 'assigned_driver', 'requested_time']
    list_filter = ['status', 'emergency_type']
    list_editable = ['status']
    search_fields = ['patient__username', 'pickup_address']
    inlines = [BookingStatusLogInline]
    readonly_fields = ['requested_time']

@admin.register(BookingStatusLog)
class BookingStatusLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'status', 'timestamp', 'updated_by']
    readonly_fields = ['timestamp']