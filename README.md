# MediResponse: Ambulance Booking System

### Subject
SYSTEM INTEGRATION ARCHITECTURE

### Academic Year
2025-2026

### Members
- Kimly Mark M. Bron
- Francis Aying
- Mark Aaron Figueroa

### Instructor
Divine Caabay

---

## Project Description

**MediResponse** is a comprehensive ambulance booking and dispatch management system designed to streamline emergency medical services. The platform connects patients, ambulance drivers, and administrators in a real-time environment to ensure efficient emergency response.

The system enables patients to request ambulances through an intuitive web interface, dispatchers to manage bookings and assignments, and drivers to receive and track their assignments. It provides real-time status tracking, comprehensive reporting, and fleet management capabilities.

---

## Features

- **User Authentication**
  - Role-based access control (Patient, Driver, Admin)
  - Secure login and registration system
  - User profile management

- **Patient Features**
  - Submit ambulance requests with emergency type selection
  - Real-time booking status tracking
  - Booking history and past records
  - View assigned ambulance details and driver information
  - Emergency address management

- **Admin/Dispatcher Features**
  - Dashboard with key metrics (active dispatches, available units, response times)
  - Comprehensive booking management and filtering
  - Ambulance fleet management and status tracking
  - Driver management and assignment
  - Patient records database
  - Reporting and analytics

- **Driver Features**
  - View active dispatch assignments
  - Update booking status (en route, arrived, transporting, completed)
  - Real-time status notifications
  - Booking completion confirmation

- **System Features**
  - Real-time dashboard updates
  - Status tracking and logging
  - Booking history and status transitions
  - Emergency type categorization
  - Fleet availability monitoring
  - Responsive design (mobile-friendly)

---

## Technologies Used

- **Backend**: Python 3.13
- **Framework**: Django
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap (Custom CSS styling)
- **Font**: Inter (Google Fonts)
- **Server**: Django Development Server / Gunicorn

---

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd MediResponse
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Load Initial Data**
   ```bash
   python manage.py loaddata booking/fixtures/initial_data.json
   ```

6. **Create Superuser (Admin Account)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to create your admin account.

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Application: `http://127.0.0.1:8000`
   - Login with your superuser credentials

---

## Project Structure

```
MediResponse/
├── booking/                    # Main Django app
│   ├── migrations/            # Database migrations
│   ├── fixtures/              # Initial data
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin interface
│   └── tests.py               # Unit tests
├── mediresponse/              # Project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL router
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── booking/               # App templates
│   │   ├── admin/            # Admin templates
│   │   ├── driver/           # Driver templates
│   │   └── patient/          # Patient templates
│   └── registration/          # Auth templates
├── static/                    # Static files
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript
├── db.sqlite3                # SQLite database
├── manage.py                 # Django management script
└── README.md                 # This file
```

---

## Database Models

### Core Models
- **User** (Django built-in): Authentication user accounts
- **UserProfile**: Extended user information with role designation
- **Patient**: Patient-specific information
- **Driver**: Driver credentials and contact information
- **Ambulance**: Fleet vehicle tracking and status
- **Booking**: Ambulance booking requests
- **BookingStatusLog**: Audit trail for booking status changes
- **EmergencyType**: Categorization of emergencies

---

## User Roles & Permissions

### Patient
- Create new ambulance bookings
- View active bookings and tracking
- Access booking history
- Cannot access admin or driver functions

### Driver
- View assigned bookings/dispatches
- Update booking status
- Mark bookings as completed
- Cannot access admin functions or other drivers' bookings

### Admin/Dispatcher
- Full access to all bookings
- Fleet management
- Driver management
- Patient records
- Generate reports
- System analytics and metrics

---

## Default Credentials

After running `python manage.py createsuperuser`, use your created credentials to login.

**Sample Test Users** (after loading fixtures):
- Emergency Types are pre-loaded
- Ambulances are pre-loaded
- Additional users can be created through the registration page

---

## Screenshots

For screenshots: [Google Drive - Screenshots](https://drive.google.com/drive/folders/1X6VY88WUBp38PGaif_kYOk9tyYemx-Nz?usp=sharing)

---

## Live Demo

Currently deployed locally. For production deployment, configure:
- Web server (Nginx, Apache)
- Production database (PostgreSQL recommended)
- Environment variables (.env file)
- Static file serving
- HTTPS/SSL certificates

---

## Video Demonstration

For a complete walkthrough of the system features and functionality, see:
[Google Drive - Video Demo](https://drive.google.com/drive/folders/1iCnqd9yiJNMbcfYuJ07K9yx_hRKzU93u?usp=sharing)

---

## Future Improvements

- **SMS/Email Notifications**: Automated updates to patients and drivers
- **GPS Integration**: Real-time ambulance location tracking on maps
- **Payment Gateway**: Online payment processing for ambulance services
- **Advanced Analytics**: Predictive analytics for demand forecasting
- **Mobile Apps**: Native iOS and Android applications
- **AI-Powered Dispatch**: Machine learning for optimal ambulance assignment
- **Multi-language Support**: Localization for different languages
- **Accessibility Features**: Enhanced accessibility for users with disabilities
- **Enhanced Security**: Two-factor authentication, encryption
- **Performance Optimization**: Caching, database optimization
- **Integration APIs**: Third-party service integrations
- **Call Center Integration**: Phone-based booking system
- **Insurance Integration**: Insurance verification and claims processing

---

## Troubleshooting

### Admin Dashboard Shows "Forbidden"
- Ensure your admin user has a UserProfile with role='admin'
- Run: `python fix_admin_profile.py`

### Dashboard Appears Dark/Unstyled
- Clear browser cache (Ctrl+Shift+R on Windows/Linux, Cmd+Shift+R on Mac)
- Ensure static files are loaded correctly
- Check CSS file is present: `static/css/style.css`

### No Data in Admin Dashboard
- Load initial data: `python manage.py loaddata booking/fixtures/initial_data.json`
- Create test bookings through the patient interface

### Database Errors
- Run migrations: `python manage.py migrate`
- Check database file exists: `db.sqlite3`

---

## Support & Contact

For issues, bugs, or feature requests, please refer to the project documentation or contact the development team.

---

## License

This project is developed as part of academic coursework at Palawan State University.

---
