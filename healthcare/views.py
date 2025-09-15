from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.utils import timezone
from .forms import UserForm, AddressForm, PatientForm, DoctorForm
from .models import Patient, Doctor, Address, Admin, Appointment, Prescription
import logging

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

logger = logging.getLogger(__name__)

def create_demo_users():
    """Create demo users if they don't exist"""
    try:
        # Create demo patient user
        demo_patient_user, created = User.objects.get_or_create(
            username='demo_patient',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'demo.patient@example.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            demo_patient_user.set_password('demo123')
            demo_patient_user.save()
            
            # Create address for demo patient
            demo_address = Address.objects.create(
                line1='123 Demo Street',
                city='Demo City',
                state='Demo State',
                pincode='12345'
            )
            
            # Create patient profile
            Patient.objects.create(
                user=demo_patient_user,
                address=demo_address,
                date_of_birth='1990-01-01',
                phone='555-1234',
                medical_history='Demo medical history for testing purposes'
            )
            logger.info('Demo patient user created successfully')
        
        # Create demo doctor user
        demo_doctor_user, created = User.objects.get_or_create(
            username='demo_doctor',
            defaults={
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'demo.doctor@example.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            demo_doctor_user.set_password('demo123')
            demo_doctor_user.save()
            
            # Create address for demo doctor
            demo_doc_address = Address.objects.create(
                line1='456 Doctor Lane',
                city='Med City',
                state='Health State',
                pincode='67890'
            )
            
            # Create doctor profile
            Doctor.objects.create(
                user=demo_doctor_user,
                address=demo_doc_address,
                specialization='General Medicine',
                license_number='DOC12345',
                experience_years=5,
                phone='555-DOC1'
            )
            logger.info('Demo doctor user created successfully')
            
    except Exception as e:
        logger.error(f'Error creating demo users: {str(e)}')

def signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        address_form = AddressForm(request.POST)
        patient_form = PatientForm(request.POST, request.FILES)
        doctor_form = DoctorForm(request.POST, request.FILES)
        
        user_type = request.POST.get('user_type')
        
        # Validate all forms
        forms_valid = user_form.is_valid() and address_form.is_valid()
        
        if forms_valid:
            if user_type == 'patient':
                forms_valid = forms_valid and patient_form.is_valid()
            elif user_type == 'doctor':
                forms_valid = forms_valid and doctor_form.is_valid()
        
        if forms_valid:
            try:
                # Create user
                user = User.objects.create_user(
                    username=user_form.cleaned_data['username'],
                    email=user_form.cleaned_data['email'],
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                    password=user_form.cleaned_data['password']
                )
                
                # Create address
                address = Address.objects.create(
                    line1=address_form.cleaned_data['line1'],
                    city=address_form.cleaned_data['city'],
                    state=address_form.cleaned_data['state'],
                    pincode=address_form.cleaned_data['pincode']
                )
                
                # Create patient or doctor
                if user_type == 'patient':
                    patient = Patient.objects.create(
                        user=user,
                        address=address,
                        profile_picture=patient_form.cleaned_data.get('profile_picture'),
                        date_of_birth=patient_form.cleaned_data.get('date_of_birth'),
                        phone=patient_form.cleaned_data.get('phone', ''),
                        medical_history=patient_form.cleaned_data.get('medical_history', '')
                    )
                    messages.success(request, 'Patient account created successfully!')
                    # Log in the user and redirect to patient dashboard
                    login(request, user)
                    return redirect('healthcare:patient_dashboard')
                    
                elif user_type == 'doctor':
                    doctor = Doctor.objects.create(
                        user=user,
                        address=address,
                        profile_picture=doctor_form.cleaned_data.get('profile_picture'),
                        specialization=doctor_form.cleaned_data.get('specialization'),
                        license_number=doctor_form.cleaned_data.get('license_number'),
                        experience_years=doctor_form.cleaned_data.get('experience_years', 0),
                        phone=doctor_form.cleaned_data.get('phone', '')
                    )
                    messages.success(request, 'Doctor account created successfully!')
                    # Log in the user and redirect to doctor dashboard
                    login(request, user)
                    return redirect('healthcare:doctor_dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Show form errors
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'User {field}: {error}')
            if not address_form.is_valid():
                for field, errors in address_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Address {field}: {error}')
            if user_type == 'patient' and not patient_form.is_valid():
                for field, errors in patient_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Patient {field}: {error}')
            elif user_type == 'doctor' and not doctor_form.is_valid():
                for field, errors in doctor_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Doctor {field}: {error}')
    else:
        user_form = UserForm()
        address_form = AddressForm()
        patient_form = PatientForm()
        doctor_form = DoctorForm()
    
    return render(request, 'healthcare/signup.html', {
        'user_form': user_form,
        'address_form': address_form,
        'patient_form': patient_form,
        'doctor_form': doctor_form
    })

def home(request):
    return render(request, 'healthcare/home.html')

def login_view(request):
    logger.info(f'=== LOGIN DEBUG ===')
    logger.info(f'Login view called with method: {request.method}')
    logger.info(f'Request headers: {dict(request.headers)}')
    
    if request.method == 'POST':
        logger.info(f'POST data received: {dict(request.POST)}')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        logger.info(f'Username: {username}')
        logger.info(f'Password: {password}')
        
        if username and password:
            logger.info(f'Attempting authentication for username: {username}')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logger.info(f'Authentication SUCCESSFUL for user: {username}')
                login(request, user)
                logger.info(f'User {username} logged in successfully')
                
                # Check user type and redirect accordingly
                try:
                    # Check if user is admin
                    if user.is_staff or user.is_superuser:
                        logger.info(f'User {username} is admin, redirecting to admin dashboard')
                        return redirect('healthcare:admin_dashboard')
                    
                    # Check if user is patient
                    try:
                        patient = Patient.objects.get(user=user)
                        logger.info(f'User {username} is patient, redirecting to patient dashboard')
                        return redirect('healthcare:patient_dashboard')
                    except Patient.DoesNotExist:
                        pass
                    
                    # Check if user is doctor
                    try:
                        doctor = Doctor.objects.get(user=user)
                        logger.info(f'User {username} is doctor, redirecting to doctor dashboard')
                        return redirect('healthcare:doctor_dashboard')
                    except Doctor.DoesNotExist:
                        pass
                    
                    # If no profile found, redirect to signup
                    logger.warning(f'No profile found for user {username}, redirecting to signup')
                    messages.warning(request, 'Profile not found. Please complete your profile.')
                    return redirect('healthcare:signup')
                    
                except Exception as e:
                    logger.error(f'Error determining user type for {username}: {str(e)}')
                    return redirect('healthcare:dashboard')
            else:
                logger.warning(f'Authentication FAILED for username: {username}')
                messages.error(request, 'Invalid username or password.')
        else:
            logger.warning(f'Missing username or password in POST data')
            messages.error(request, 'Please provide both username and password.')
    else:
        logger.info('Login view called with GET method')
    
    return render(request, 'healthcare/login_enhanced.html')

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                logger.info(f'Admin user {username} logged in successfully')
                messages.success(request, 'Welcome Admin!')
                return redirect('healthcare:admin_dashboard')
            else:
                logger.warning(f'Non-admin user {username} attempted admin login')
                messages.error(request, 'Admin access required.')
        else:
            logger.warning(f'Failed admin login attempt for username: {username}')
            messages.error(request, 'Invalid username or password.')
    return render(request, 'healthcare/admin_login.html')

def demo_login_view(request, user_type):
    """Demo login view that simulates login without actual authentication"""
    create_demo_users()  # Ensure demo users exist
    
    if user_type == 'patient':
        username = 'demo_patient'
        redirect_url = 'healthcare:patient_dashboard'
        user_type_name = 'Patient'
    elif user_type == 'doctor':
        username = 'demo_doctor'
        redirect_url = 'healthcare:doctor_dashboard'
        user_type_name = 'Doctor'
    else:
        messages.error(request, 'Invalid demo user type.')
        return redirect('healthcare:login')
    
    try:
        # Get the demo user
        user = User.objects.get(username=username)
        
        # Use Django's login function to authenticate the user
        login(request, user)
        
        # Set demo session flag
        request.session['is_demo_user'] = True
        request.session['demo_user_type'] = user_type
        
        logger.info(f'Demo {user_type} login successful for user: {username}')
        messages.success(request, f'Demo {user_type_name} mode activated! This is a demonstration account.')
        
        return redirect(redirect_url)
        
    except User.DoesNotExist:
        logger.error(f'Demo user {username} not found')
        messages.error(request, 'Demo user not found. Please contact administrator.')
        return redirect('healthcare:login')
    except Exception as e:
        logger.error(f'Error in demo login: {str(e)}')
        messages.error(request, 'Demo login failed. Please try again.')
        return redirect('healthcare:login')

def logout_view(request):
    # Check if it was a demo session
    is_demo = request.session.get('is_demo_user', False)
    user_type = request.session.get('demo_user_type', '')
    
    logout(request)
    
    if is_demo:
        messages.success(request, f'Demo {user_type.capitalize()} session ended successfully.')
    else:
        messages.success(request, 'You have been successfully logged out.')
        
    return redirect('healthcare:home')

@login_required
def dashboard(request):
    user = request.user
    
    # Check if user is admin
    if user.is_staff or user.is_superuser:
        return redirect('healthcare:admin_dashboard')
    
    # Check for Patient
    try:
        patient = Patient.objects.get(user=user)
        return redirect('healthcare:patient_dashboard')
    except Patient.DoesNotExist:
        logger.error(f'Patient profile not found for user: {user.username}')
        pass
    
    # Check for Doctor
    try:
        doctor = Doctor.objects.get(user=user)
        return redirect('healthcare:doctor_dashboard')
    except Doctor.DoesNotExist:
        logger.error(f'Doctor profile not found for user: {user.username}')
        messages.error(request, 'User profile not found.')
        return redirect('healthcare:signup')

# Admin Dashboard Views
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    
    # Get all patients and doctors for admin dashboard
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    
    # Get today's appointments count
    from django.utils import timezone
    from .models import Appointment
    today = timezone.now().date()
    todays_appointments_count = Appointment.objects.filter(appointment_date=today).count()
    
    return render(request, 'healthcare/admin_dashboard_enhanced.html', {
        'user': request.user,
        'user_type': 'Admin',
        'patients': patients,
        'doctors': doctors,
        'todays_appointments_count': todays_appointments_count
    })

@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
        # Get upcoming appointments for this patient
        from .models import Appointment
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now().date()
        ).order_by('appointment_date', 'appointment_time')[:10]
        
        return render(request, 'healthcare/patient_dashboard.html', {
            'user': request.user,
            'user_type': 'Patient',
            'patient': patient,
            'upcoming_appointments': upcoming_appointments
        })
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('healthcare:signup')

@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        from .models import Appointment
        
        # Get filter type from request parameter
        filter_type = request.GET.get('filter', 'all')  # Changed default from 'upcoming' to 'all'
        
        today = timezone.now().date()  # Initialize today variable

        # Get appointments based on filter type
        if filter_type == 'all':
            # Show all appointments (past and future)
            appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', 'appointment_time')
            filter_name = "All Appointments"
        elif filter_type == 'today':
            # Show only today's appointments
            appointments = Appointment.objects.filter(doctor=doctor, appointment_date=today).order_by('appointment_time')
            filter_name = "Today's Appointments"
        else:
            # Show upcoming appointments (future dates)
            appointments = Appointment.objects.filter(doctor=doctor, appointment_date__gte=today).order_by('appointment_date', 'appointment_time')
            filter_name = "Upcoming Appointments"
        
        return render(request, 'healthcare/doctor_dashboard.html', {
            'user': request.user,
            'user_type': 'Doctor',
            'doctor': doctor,
            'appointments': appointments,
            'current_filter': filter_type,
            'filter_name': filter_name,
            'current_date': timezone.now().date()
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:signup')

@login_required
def admin_manage_users(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/manage_users.html')

@login_required
def admin_view_analytics(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/view_analytics.html')

@login_required
def admin_appointments(request):
    """View for admin to view all appointments"""
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    
    from .models import Appointment
    # Get filter type from request parameter
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()

    # Get appointments based on filter type
    if filter_type == 'all':
        appointments = Appointment.objects.all().order_by('-appointment_date', 'appointment_time')
        filter_name = "All Appointments"
    elif filter_type == 'today':
        appointments = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
        filter_name = "Today's Appointments"
    else:
        appointments = Appointment.objects.filter(appointment_date__gte=today).order_by('appointment_date', 'appointment_time')
        filter_name = "Upcoming Appointments"
    
    return render(request, 'healthcare/admin/appointments.html', {
        'appointments': appointments,
        'current_filter': filter_type,
        'filter_name': filter_name,
        'current_date': today
    })

@login_required
def admin_reports(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    # Gather context data for all report tabs

    # User reports data
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()

    # Get recent user registrations (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).order_by('-date_joined')

    # Appointment reports data
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()

    # Get appointments by doctor
    from django.db.models import Count
    appointments_by_doctor = Appointment.objects.values('doctor__user__first_name', 'doctor__user__last_name').annotate(
        total=Count('id')
    ).order_by('-total')

    # Recent appointments
    recent_appointments = Appointment.objects.all().order_by('-created_at')[:50]

    # Financial reports data
    # Mock revenue calculation (e.g., $100 per completed appointment)
    avg_revenue_per_appointment = 100
    total_revenue = completed_appointments * avg_revenue_per_appointment

    # Monthly revenue (mock)
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_appointments = Appointment.objects.filter(
        appointment_date__year=current_year,
        appointment_date__month=current_month,
        status='completed'
    ).count()
    monthly_revenue = monthly_appointments * avg_revenue_per_appointment

    # System reports data
    total_prescriptions = Prescription.objects.count()

    # Active users (users who logged in recently)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()

    # System uptime (mock - in real system would get from server)
    system_uptime = "99.9%"  # Mock value

    context = {
        # User reports
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'recent_users': recent_users,

        # Appointment reports
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'appointments_by_doctor': appointments_by_doctor,
        'recent_appointments': recent_appointments,

        # Financial reports
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'avg_revenue_per_appointment': avg_revenue_per_appointment,

        # System reports
        'total_prescriptions': total_prescriptions,
        'active_users': active_users,
        'system_uptime': system_uptime,
    }

    return render(request, 'healthcare/admin/reports.html', context)

@login_required
def user_reports(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    # Get user statistics
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()

    # Get recent user registrations (last 30 days)
    from django.utils import timezone
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).order_by('-date_joined')

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'recent_users': recent_users,
    }
    return render(request, 'healthcare/admin/user_reports.html', context)

@login_required
def appointment_reports(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    # Get appointment statistics
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()

    # Get appointments by doctor
    from django.db.models import Count
    appointments_by_doctor = Appointment.objects.values('doctor__user__first_name', 'doctor__user__last_name').annotate(
        total=Count('id')
    ).order_by('-total')

    # Recent appointments
    recent_appointments = Appointment.objects.all().order_by('-created_at')[:50]

    context = {
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'appointments_by_doctor': appointments_by_doctor,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'healthcare/admin/appointment_reports.html', context)

@login_required
def financial_reports(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    # Since there are no financial models, we'll use appointment data as proxy
    # Assuming each appointment generates revenue
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()

    # Mock revenue calculation (e.g., $100 per completed appointment)
    avg_revenue_per_appointment = 100
    total_revenue = completed_appointments * avg_revenue_per_appointment

    # Monthly revenue (mock)
    from django.utils import timezone
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_appointments = Appointment.objects.filter(
        appointment_date__year=current_year,
        appointment_date__month=current_month,
        status='completed'
    ).count()
    monthly_revenue = monthly_appointments * avg_revenue_per_appointment

    context = {
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'avg_revenue_per_appointment': avg_revenue_per_appointment,
    }
    return render(request, 'healthcare/admin/financial_reports.html', context)

@login_required
def system_reports(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    # System health metrics
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    total_prescriptions = Prescription.objects.count()

    # Active users (users who logged in recently)
    from django.utils import timezone
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()

    # System uptime (mock - in real system would get from server)
    system_uptime = "99.9%"  # Mock value

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'total_prescriptions': total_prescriptions,
        'active_users': active_users,
        'system_uptime': system_uptime,
    }
    return render(request, 'healthcare/admin/system_reports.html', context)

@login_required
def download_pdf(request, report_type):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(72, height - 72, f"{report_type.capitalize()} Report")

    y = height - 100
    line_height = 14

    if report_type == 'user':
        total_users = User.objects.count()
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        total_admins = User.objects.filter(is_staff=True).count()

        p.setFont("Helvetica", 12)
        p.drawString(72, y, f"Total Users: {total_users}")
        y -= line_height
        p.drawString(72, y, f"Total Patients: {total_patients}")
        y -= line_height
        p.drawString(72, y, f"Total Doctors: {total_doctors}")
        y -= line_height
        p.drawString(72, y, f"Total Admins: {total_admins}")
        y -= line_height

    elif report_type == 'appointment':
        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()

        p.setFont("Helvetica", 12)
        p.drawString(72, y, f"Total Appointments: {total_appointments}")
        y -= line_height
        p.drawString(72, y, f"Pending Appointments: {pending_appointments}")
        y -= line_height
        p.drawString(72, y, f"Confirmed Appointments: {confirmed_appointments}")
        y -= line_height
        p.drawString(72, y, f"Completed Appointments: {completed_appointments}")
        y -= line_height
        p.drawString(72, y, f"Cancelled Appointments: {cancelled_appointments}")
        y -= line_height

    elif report_type == 'financial':
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        avg_revenue_per_appointment = 100
        total_revenue = completed_appointments * avg_revenue_per_appointment

        from django.utils import timezone
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_appointments = Appointment.objects.filter(
            appointment_date__year=current_year,
            appointment_date__month=current_month,
            status='completed'
        ).count()
        monthly_revenue = monthly_appointments * avg_revenue_per_appointment

        p.setFont("Helvetica", 12)
        p.drawString(72, y, f"Total Appointments: {total_appointments}")
        y -= line_height
        p.drawString(72, y, f"Completed Appointments: {completed_appointments}")
        y -= line_height
        p.drawString(72, y, f"Total Revenue: ${total_revenue}")
        y -= line_height
        p.drawString(72, y, f"Monthly Revenue: ${monthly_revenue}")
        y -= line_height
        p.drawString(72, y, f"Avg Revenue per Appointment: ${avg_revenue_per_appointment}")
        y -= line_height

    elif report_type == 'system':
        total_users = User.objects.count()
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        total_appointments = Appointment.objects.count()
        total_prescriptions = Prescription.objects.count()

        from django.utils import timezone
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
        system_uptime = "99.9%"

        p.setFont("Helvetica", 12)
        p.drawString(72, y, f"Total Users: {total_users}")
        y -= line_height
        p.drawString(72, y, f"Total Patients: {total_patients}")
        y -= line_height
        p.drawString(72, y, f"Total Doctors: {total_doctors}")
        y -= line_height
        p.drawString(72, y, f"Total Appointments: {total_appointments}")
        y -= line_height
        p.drawString(72, y, f"Total Prescriptions: {total_prescriptions}")
        y -= line_height
        p.drawString(72, y, f"Active Users (last 30 days): {active_users}")
        y -= line_height
        p.drawString(72, y, f"System Uptime: {system_uptime}")
        y -= line_height

    else:
        p.drawString(72, y, "Invalid report type specified.")
        y -= line_height

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def admin_settings(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/settings.html')

@login_required
def admin_backup(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/backup.html')

@login_required
def admin_export_data(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/export_data.html')

@login_required
def admin_update_profile(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/update_profile.html')

@login_required
def admin_change_password(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('healthcare:dashboard')
    return render(request, 'healthcare/admin/change_password.html')

# Doctor Dashboard Action Views
@login_required
def add_patient(request):
    """View for adding a new patient"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        address_form = AddressForm(request.POST)
        patient_form = PatientForm(request.POST, request.FILES)
        
        # Validate all forms
        forms_valid = user_form.is_valid() and address_form.is_valid() and patient_form.is_valid()
        
        if forms_valid:
            try:
                # Create user
                user = User.objects.create_user(
                    username=user_form.cleaned_data['username'],
                    email=user_form.cleaned_data['email'],
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                    password=user_form.cleaned_data['password']
                )
                
                # Create address
                address = Address.objects.create(
                    line1=address_form.cleaned_data['line1'],
                    city=address_form.cleaned_data['city'],
                    state=address_form.cleaned_data['state'],
                    pincode=address_form.cleaned_data['pincode']
                )
                
                # Create patient with the address
                patient = Patient.objects.create(
                    user=user,
                    address=address,
                    profile_picture=patient_form.cleaned_data.get('profile_picture'),
                    date_of_birth=patient_form.cleaned_data.get('date_of_birth'),
                    phone=patient_form.cleaned_data.get('phone', ''),
                    medical_history=patient_form.cleaned_data.get('medical_history', '')
                )
                
                messages.success(request, 'Patient added successfully!')
                return redirect('healthcare:admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error adding patient: {str(e)}')
        else:
            # Show form errors
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'User {field}: {error}')
            if not address_form.is_valid():
                for field, errors in address_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Address {field}: {error}')
            if not patient_form.is_valid():
                for field, errors in patient_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Patient {field}: {error}')
    else:
        user_form = UserForm()
        address_form = AddressForm()
        patient_form = PatientForm()
    
    return render(request, 'healthcare/add_patient.html', {
        'form': user_form,
        'address_form': address_form,
        'patient_form': patient_form,
        'user_type': 'Admin'
    })

@login_required
def add_doctor(request):
    """View for adding a new doctor"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        address_form = AddressForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)

        # Validate all forms
        forms_valid = user_form.is_valid() and address_form.is_valid() and doctor_form.is_valid()

        if forms_valid:
            try:
                # Create user
                user = User.objects.create_user(
                    username=user_form.cleaned_data['username'],
                    email=user_form.cleaned_data['email'],
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                    password=user_form.cleaned_data['password']
                )

                # Create address
                address = Address.objects.create(
                    line1=address_form.cleaned_data['line1'],
                    city=address_form.cleaned_data['city'],
                    state=address_form.cleaned_data['state'],
                    pincode=address_form.cleaned_data['pincode']
                )

                # Create doctor
                doctor = Doctor.objects.create(
                    user=user,
                    address=address,
                    profile_picture=doctor_form.cleaned_data.get('profile_picture'),
                    specialization=doctor_form.cleaned_data.get('specialization'),
                    license_number=doctor_form.cleaned_data.get('license_number'),
                    experience_years=doctor_form.cleaned_data.get('experience_years', 0),
                    phone=doctor_form.cleaned_data.get('phone', '')
                )

                messages.success(request, 'Doctor added successfully!')
                return redirect('healthcare:admin_dashboard')

            except Exception as e:
                messages.error(request, f'Error adding doctor: {str(e)}')
        else:
            # Show form errors
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'User {field}: {error}')
            if not address_form.is_valid():
                for field, errors in address_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Address {field}: {error}')
            if not doctor_form.is_valid():
                for field, errors in doctor_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Doctor {field}: {error}')
    else:
        user_form = UserForm()
        address_form = AddressForm()
        doctor_form = DoctorForm()

    return render(request, 'healthcare/add_doctor.html', {
        'user_form': user_form,
        'address_form': address_form,
        'doctor_form': doctor_form,
        'user_type': 'Admin'
    })

@login_required
@csrf_protect
def book_appointment(request):
    """View for booking an appointment - handles both patient and doctor access"""
    from .forms import AppointmentForm
    from .models import Appointment, Patient, Doctor

    user = request.user
    context = {}

    # Determine user type and set appropriate context
    try:
        patient = Patient.objects.get(user=user)
        context.update({
            'patient': patient,
            'user_type': 'Patient'
        })
    except Patient.DoesNotExist:
        try:
            doctor = Doctor.objects.get(user=user)
            context.update({
                'doctor': doctor,
                'user_type': 'Doctor'
            })
        except Doctor.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('healthcare:dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                # For patients, use their own profile; for doctors, they need to select a patient
                if 'patient' in context:
                    appointment = Appointment(
                        patient=patient,
                        doctor=form.cleaned_data['doctor'],
                        appointment_date=form.cleaned_data['appointment_date'],
                        appointment_time=form.cleaned_data['appointment_time'],
                        reason=form.cleaned_data['reason'],
                        status='pending'
                    )
                    appointment.save()
                    messages.success(request, 'Appointment booked successfully! It is pending confirmation.')
                    return redirect('healthcare:patient_dashboard')

                elif 'doctor' in context:
                    # For doctors booking appointments, we need to handle patient selection
                    # This would require additional form fields for patient selection
                    messages.info(request, 'Doctor appointment booking requires patient selection functionality.')
                    return redirect('healthcare:doctor_dashboard')

            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AppointmentForm()

    context['form'] = form
    return render(request, 'healthcare/book_appointment.html', context)

@login_required
def view_reports(request):
    """View for viewing medical reports"""
    user = request.user

    # Check if user is a doctor
    try:
        doctor = Doctor.objects.get(user=user)
        # Doctor's reports: appointments, prescriptions, patients
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')[:20]
        prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')[:20]
        patients_count = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()

        return render(request, 'healthcare/view_reports.html', {
            'user_type': 'Doctor',
            'doctor': doctor,
            'appointments': appointments,
            'prescriptions': prescriptions,
            'patients_count': patients_count,
        })
    except Doctor.DoesNotExist:
        pass

    # Check if user is a patient
    try:
        patient = Patient.objects.get(user=user)
        # Patient's reports: appointments, prescriptions, medical history
        appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')[:20]
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')[:20]

        return render(request, 'healthcare/view_reports.html', {
            'user_type': 'Patient',
            'patient': patient,
            'appointments': appointments,
            'prescriptions': prescriptions,
        })
    except Patient.DoesNotExist:
        pass

    # If neither doctor nor patient, redirect
    messages.error(request, 'User profile not found.')
    return redirect('healthcare:dashboard')

@login_required
def start_consultation(request):
    """View for starting a consultation"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        return render(request, 'healthcare/start_consultation.html', {
            'doctor': doctor,
            'user_type': 'Doctor'
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def show_appointments(request):
    """View for showing appointments with filtering options"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        from .models import Appointment
        
        # Get filter type from request parameter
        filter_type = request.GET.get('filter', 'all')  # Changed default from 'upcoming' to 'all'
        today = timezone.now().date()

        # Get appointments based on filter type
        if filter_type == 'all':
            appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', 'appointment_time')
            filter_name = "All Appointments"
        elif filter_type == 'today':
            appointments = Appointment.objects.filter(doctor=doctor, appointment_date=today).order_by('appointment_time')
            filter_name = "Today's Appointments"
        else:
            appointments = Appointment.objects.filter(doctor=doctor, appointment_date__gte=today).order_by('appointment_date', 'appointment_time')
            filter_name = "Upcoming Appointments"
        
        return render(request, 'healthcare/show_appointments.html', {
            'doctor': doctor,
            'user_type': 'Doctor',
            'appointments': appointments,
            'current_filter': filter_type,
            'filter_name': filter_name,
            'current_date': today
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def my_patients(request):
    """View for showing doctor's patients"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        from .models import Appointment, Patient
        
        # Get unique patients who have appointments with this doctor
        patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient', flat=True).distinct()
        patients = Patient.objects.filter(id__in=patient_ids)
        
        return render(request, 'healthcare/my_patients.html', {
            'doctor': doctor,
            'user_type': 'Doctor',
            'patients': patients
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def schedule(request):
    """View for doctor's schedule management"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        return render(request, 'healthcare/schedule.html', {
            'doctor': doctor,
            'user_type': 'Doctor'
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def manage_schedule(request):
    """View to manage doctor's weekly schedule"""
    from .forms import DoctorScheduleForm
    from .models import DoctorSchedule
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)
        if form.is_valid():
            day_of_week = form.cleaned_data['day_of_week']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            is_available = form.cleaned_data['is_available']

            # Update or create schedule for the day
            schedule_obj, created = DoctorSchedule.objects.update_or_create(
                doctor=doctor,
                day_of_week=day_of_week,
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_available': is_available
                }
            )
            messages.success(request, f'Schedule for {day_of_week.capitalize()} saved successfully.')
            return redirect('healthcare:manage_schedule')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Prepare initial data for the form for each day
        schedules = DoctorSchedule.objects.filter(doctor=doctor)
        schedule_forms = []
        days = [choice[0] for choice in DoctorSchedule.DAYS_OF_WEEK]
        for day in days:
            schedule = schedules.filter(day_of_week=day).first()
            if schedule:
                form = DoctorScheduleForm(instance=schedule, prefix=day)
            else:
                form = DoctorScheduleForm(prefix=day, initial={'day_of_week': day, 'is_available': True})
            schedule_forms.append(form)

        return render(request, 'healthcare/manage_schedule.html', {
            'doctor': doctor,
            'schedule_forms': schedule_forms,
            'user_type': 'Doctor'
        })

@login_required
def request_time_off(request):
    """View to request time off"""
    from .forms import TimeOffRequestForm
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        form = TimeOffRequestForm(request.POST)
        if form.is_valid():
            time_off_request = form.save(commit=False)
            time_off_request.doctor = doctor
            time_off_request.save()
            messages.success(request, 'Time off request submitted successfully.')
            return redirect('healthcare:request_time_off')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TimeOffRequestForm()

    # Show existing requests
    existing_requests = doctor.time_off_requests.all().order_by('-created_at')

    return render(request, 'healthcare/request_time_off.html', {
        'doctor': doctor,
        'form': form,
        'existing_requests': existing_requests,
        'user_type': 'Doctor'
    })

from django.db.models import Q
from .forms import PrescriptionForm

@login_required
def prescriptions(request):
    """Main prescriptions page with navigation to create and history"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        return render(request, 'healthcare/prescriptions.html', {
            'doctor': doctor,
            'user_type': 'Doctor'
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def create_prescription(request):
    """View to create a new prescription"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST, doctor=doctor)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = doctor
            prescription.save()
            messages.success(request, 'Prescription created successfully! You can view it in the prescription history.')
            return redirect('healthcare:prescription_history')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PrescriptionForm(doctor=doctor)

    return render(request, 'healthcare/create_prescription.html', {
        'form': form,
        'doctor': doctor,
        'user_type': 'Doctor'
    })

@login_required
def prescription_history(request):
    """View to display prescription history with search and filter"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    query = request.GET.get('q', '')
    prescriptions = doctor.prescriptions.all()

    if query:
        prescriptions = prescriptions.filter(
            Q(patient__user__first_name__icontains=query) |
            Q(patient__user__last_name__icontains=query) |
            Q(medication_name__icontains=query)
        )

    return render(request, 'healthcare/prescription_history.html', {
        'prescriptions': prescriptions,
        'doctor': doctor,
        'user_type': 'Doctor',
        'query': query
    })

@login_required
def doctor_settings(request):
    """View for doctor settings"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        return render(request, 'healthcare/doctor_settings.html', {
            'doctor': doctor,
            'user_type': 'Doctor'
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

@login_required
def doctor_update_profile(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        user = request.user
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        from .forms import DoctorProfileUpdateForm
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=doctor, user=user)
        if form.is_valid():
            doctor = form.save(commit=False)
            # Update User model fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            doctor.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('healthcare:doctor_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import DoctorProfileUpdateForm
        form = DoctorProfileUpdateForm(instance=doctor, user=user)

    return render(request, 'healthcare/doctor_update_profile.html', {
        'form': form,
        'doctor': doctor,
        'user_type': 'Doctor'
    })

@login_required
def doctor_change_password(request):
    try:
        user = request.user
    except Exception:
        messages.error(request, 'User not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        from .forms import DoctorChangePasswordForm
        form = DoctorChangePasswordForm(request.POST, user=user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully. Please log in again.')
            from django.contrib.auth import logout
            logout(request)
            return redirect('healthcare:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import DoctorChangePasswordForm
        form = DoctorChangePasswordForm(user=user)

    return render(request, 'healthcare/doctor_change_password.html', {
        'form': form,
        'user_type': 'Doctor'
    })

@login_required
def doctor_notification_settings(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        from .models import DoctorSettings
        settings, created = DoctorSettings.objects.get_or_create(doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        from .forms import DoctorNotificationSettingsForm
        form = DoctorNotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification settings updated successfully.')
            return redirect('healthcare:doctor_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import DoctorNotificationSettingsForm
        form = DoctorNotificationSettingsForm(instance=settings)

    return render(request, 'healthcare/doctor_notification_settings.html', {
        'form': form,
        'doctor': doctor,
        'user_type': 'Doctor'
    })

@login_required
def doctor_practice_settings(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        from .models import DoctorSettings
        settings, created = DoctorSettings.objects.get_or_create(doctor=doctor)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('healthcare:dashboard')

    if request.method == 'POST':
        from .forms import DoctorPracticeSettingsForm
        form = DoctorPracticeSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Practice settings updated successfully.')
            return redirect('healthcare:doctor_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import DoctorPracticeSettingsForm
        form = DoctorPracticeSettingsForm(instance=settings)

    return render(request, 'healthcare/doctor_practice_settings.html', {
        'form': form,
        'doctor': doctor,
        'user_type': 'Doctor'
    })

@login_required
def view_patient(request, id):
    """View for displaying individual patient details"""
    # Check if user is admin or doctor
    try:
        Doctor.objects.get(user=request.user)
        is_doctor = True
    except Doctor.DoesNotExist:
        is_doctor = False

    if not (request.user.is_staff or is_doctor):
        messages.error(request, 'Access denied.')
        return redirect('healthcare:dashboard')

    try:
        patient = Patient.objects.get(id=id)
        return render(request, 'healthcare/patient_detail.html', {
            'patient': patient,
            'user_type': 'Admin' if request.user.is_staff else 'Doctor'
        })
    except Patient.DoesNotExist:
        messages.error(request, 'Patient not found.')
        return redirect('healthcare:dashboard')

@login_required
def view_doctor(request, id):
    """View for displaying individual doctor details"""
    # Check if user is admin or doctor
    try:
        Doctor.objects.get(user=request.user)
        is_doctor = True
    except Doctor.DoesNotExist:
        is_doctor = False

    if not (request.user.is_staff or is_doctor):
        messages.error(request, 'Access denied.')
        return redirect('healthcare:dashboard')

    try:
        doctor = Doctor.objects.get(id=id)
        return render(request, 'healthcare/doctor_detail.html', {
            'doctor': doctor,
            'user_type': 'Admin' if request.user.is_staff else 'Doctor'
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor not found.')
        return redirect('healthcare:dashboard')

@login_required
def debug_user_info(request):
    """Debug view to show user information and help troubleshoot issues"""
    user = request.user
    context = {
        'user': user,
        'is_authenticated': user.is_authenticated,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'groups': list(user.groups.all()),
        'permissions': list(user.user_permissions.all()),
    }
    
    # Check for Patient profile
    try:
        patient = Patient.objects.get(user=user)
        context['patient_profile'] = patient
        context['user_type'] = 'Patient'
    except Patient.DoesNotExist:
        context['patient_profile'] = None
    
    # Check for Doctor profile
    try:
        doctor = Doctor.objects.get(user=user)
        context['doctor_profile'] = doctor
        context['user_type'] = 'Doctor'
    except Doctor.DoesNotExist:
        context['doctor_profile'] = None
    
    # Check for Admin profile
    try:
        admin_profile = Admin.objects.get(user=user)
        context['admin_profile'] = admin_profile
        context['user_type'] = 'Admin'
    except Admin.DoesNotExist:
        context['admin_profile'] = None
    
    return render(request, 'healthcare/debug_user_info.html', context)

@login_required
def test_csrf(request):
    """Test view to verify CSRF token functionality"""
    if request.method == 'POST':
        messages.success(request, 'CSRF token verification successful! Form submitted correctly.')
        return redirect('healthcare:test_csrf')

    return render(request, 'healthcare/test_csrf.html')
