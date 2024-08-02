# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, Doctor, Staff, Appointment, Billing, Inventory, Prescription

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1','password2']

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['dob', 'address', 'phone']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialty', 'phone']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['role', 'phone']


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BillingForm(forms.ModelForm):
    billing_amount = forms.DecimalField(label='Billing Amount', min_value=0)

    class Meta:
        model = Billing
        fields = ['billing_amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['item_name', 'quantity', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine', 'dosage', 'duration']
