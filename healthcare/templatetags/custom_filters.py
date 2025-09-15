from django import template
from datetime import datetime

register = template.Library()

@register.filter
def age(birth_date):
    """Calculate age from birth date."""
    if birth_date:
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return None

@register.filter
def filter_status(queryset, status):
    """Filter appointments by status."""
    if hasattr(queryset, 'filter'):
        return queryset.filter(status=status)
    return []

@register.filter
def has_patient_profile(user):
    """Check if user has a patient profile."""
    try:
        from healthcare.models import Patient
        Patient.objects.get(user=user)
        return True
    except Patient.DoesNotExist:
        return False

@register.filter
def has_doctor_profile(user):
    """Check if user has a doctor profile."""
    try:
        from healthcare.models import Doctor
        Doctor.objects.get(user=user)
        return True
    except Doctor.DoesNotExist:
        return False

@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg."""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Add arg to value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0
