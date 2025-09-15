from django import forms
from django.contrib.auth.models import User
from .models import Patient, Doctor, Address

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
    
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match!"
            )
        
        return cleaned_data

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('line1', 'city', 'state', 'pincode')

class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    phone = forms.CharField(max_length=20, required=False)
    medical_history = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    class Meta:
        model = Patient
        fields = ('profile_picture', 'date_of_birth', 'phone', 'medical_history')

class DoctorForm(forms.ModelForm):
    specialization = forms.CharField(max_length=100, required=False)
    license_number = forms.CharField(max_length=50, required=False)
    experience_years = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        initial=0
    )
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = Doctor
        fields = ('profile_picture', 'specialization', 'license_number', 'experience_years', 'phone')

class AppointmentForm(forms.Form):
    from .models import Doctor
    
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        empty_label="Select a Doctor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select a date for your appointment"
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Select a time for your appointment"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Brief reason for the appointment'}),
        required=False,
        help_text="Optional: Describe the reason for your visit"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        
        if doctor and appointment_date and appointment_time:
            # Check if the doctor already has an appointment at this time
            from .models import Appointment
            conflicting_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exists()
            
            if conflicting_appointment:
                raise forms.ValidationError(
                    "This doctor already has an appointment scheduled at the selected time. Please choose a different time."
                )
        
        return cleaned_data

class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        from .models import DoctorSchedule
        model = DoctorSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        from .models import TimeOffRequest
        model = TimeOffRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class PrescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        if self.doctor:
            # Only show patients who have appointments with this doctor
            from .models import Appointment
            patient_ids = Appointment.objects.filter(doctor=self.doctor).values_list('patient', flat=True).distinct()
            from .models import Patient
            self.fields['patient'].queryset = Patient.objects.filter(id__in=patient_ids)

    class Meta:
        from .models import Prescription
        model = Prescription
        fields = ['patient', 'medication_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medication_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Amoxicillin 500mg'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 tablet'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Twice daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days'}),
            'instructions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Additional instructions for the patient'}),
        }
        labels = {
            'medication_name': 'Medication Name',
            'dosage': 'Dosage',
            'frequency': 'Frequency',
            'duration': 'Duration',
            'instructions': 'Instructions',
        }

# Doctor Settings Forms
class DoctorProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell patients about your expertise and approach...'}),
        required=False
    )

    class Meta:
        model = Doctor
        fields = ['profile_picture', 'specialization', 'license_number', 'experience_years', 'phone', 'bio']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Cardiology, Pediatrics'}),
            'license_number': forms.TextInput(attrs={'class': 'form-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 123-4567'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

class DoctorChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label="New Password",
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label="Confirm New Password"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

class DoctorNotificationSettingsForm(forms.ModelForm):
    class Meta:
        from .models import DoctorSettings
        model = DoctorSettings
        fields = ['email_notifications', 'sms_notifications', 'appointment_reminders']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email_notifications': 'Email Notifications',
            'sms_notifications': 'SMS Notifications',
            'appointment_reminders': 'Appointment Reminders',
        }

class DoctorPracticeSettingsForm(forms.ModelForm):
    class Meta:
        from .models import DoctorSettings
        model = DoctorSettings
        fields = ['working_hours_start', 'working_hours_end', 'break_duration', 'max_patients_per_day', 'consultation_notes_auto_save']
        widgets = {
            'working_hours_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'working_hours_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'max_patients_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'consultation_notes_auto_save': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'working_hours_start': 'Working Hours Start',
            'working_hours_end': 'Working Hours End',
            'break_duration': 'Break Duration (minutes)',
            'max_patients_per_day': 'Maximum Patients Per Day',
            'consultation_notes_auto_save': 'Auto-save Consultation Notes',
        }
