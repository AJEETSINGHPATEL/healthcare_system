from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.state} - {self.pincode}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    @property
    def full_name(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Admin: {self.user.first_name} {self.user.last_name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']

    def __str__(self):
        return f"{self.patient.full_name} with {self.doctor.full_name} on {self.appointment_date} at {self.appointment_time}"

    @property
    def formatted_date(self):
        return self.appointment_date.strftime('%b %d, %Y')

    @property
    def formatted_time(self):
        return self.appointment_time.strftime('%I:%M %p')

class DoctorSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_day_of_week_display()}"

class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} - {self.medication_name}"

class DoctorSettings(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    appointment_reminders = models.BooleanField(default=True)
    consultation_notes_auto_save = models.BooleanField(default=True)
    working_hours_start = models.TimeField(default='09:00:00')
    working_hours_end = models.TimeField(default='17:00:00')
    break_duration = models.IntegerField(default=15)  # minutes
    max_patients_per_day = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.doctor.full_name}"

class TimeOffRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_off_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.doctor.full_name} - {self.start_date} to {self.end_date}"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
