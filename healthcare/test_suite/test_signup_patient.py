import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_signup_patient():
    client = Client()
    url = reverse('healthcare:signup')
    data = {
        'user_type': 'patient',
        'username': 'testpatient',
        'email': 'patient@example.com',
        'first_name': 'Test',
        'last_name': 'Patient',
        'password': 'testpassword123',
        'line1': '123 Main St',
        'city': 'Testville',
        'state': 'TS',
        'pincode': '12345',
        'date_of_birth': '1990-01-01',
        'phone': '1234567890',
        'medical_history': 'None',
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect on success
