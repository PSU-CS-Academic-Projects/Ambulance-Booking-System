from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ── Authentication ──────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ── Dashboard (role-based redirect) ─────────────────────
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # ── Patient Pages ────────────────────────────────────────
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/booking/new/', views.new_booking, name='new_booking'),
    path('patient/booking/<int:pk>/', views.booking_detail_patient, name='booking_detail_patient'),
    path('patient/booking/history/', views.booking_history, name='booking_history'),
    path('patient/booking/<int:pk>/status/', views.booking_status_json, name='booking_status_json'),

    # ── Admin Pages ──────────────────────────────────────────
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/bookings/', views.admin_bookings_list, name='admin_bookings_list'),
    path('admin-panel/bookings/<int:pk>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('admin-panel/fleet/', views.admin_fleet, name='admin_fleet'),
    path('admin-panel/fleet/add/', views.admin_ambulance_add, name='admin_ambulance_add'),
    path('admin-panel/fleet/<int:pk>/edit/', views.admin_ambulance_edit, name='admin_ambulance_edit'),
    path('admin-panel/drivers/', views.admin_drivers, name='admin_drivers'),
    path('admin-panel/patients/', views.admin_patients, name='admin_patients'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),

    # ── Driver Pages ─────────────────────────────────────────
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/booking/<int:pk>/update/', views.driver_update_status, name='driver_update_status'),

    # ── Error pages ──────────────────────────────────────────
    path('forbidden/', views.forbidden_view, name='forbidden'),
]