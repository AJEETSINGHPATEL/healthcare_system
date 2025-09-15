from django.contrib import admin
from .models import Patient, Doctor, Address, Admin

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'date_of_birth']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'specialization', 'license_number']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'specialization']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['line1', 'city', 'state', 'pincode']
    search_fields = ['line1', 'city', 'state', 'pincode']

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
