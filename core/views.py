from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Patient, Doctor, Staff, Appointment, Billing, Inventory, Prescription
from .forms import UserRegistrationForm, PatientForm, DoctorForm, StaffForm, AppointmentForm, PrescriptionForm, InventoryForm, BillingForm
from datetime import datetime
from django.contrib import messages
from django.db import transaction

# Home page
def home(request):
    return render(request, 'home.html')

# Registration views
def register(request, role):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if role == 'patient':
            profile_form = PatientForm(request.POST)
        elif role == 'doctor':
            profile_form = DoctorForm(request.POST)
        elif role == 'staff':
            profile_form = StaffForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        if role == 'patient':
            profile_form = PatientForm()
        elif role == 'doctor':
            profile_form = DoctorForm()
        elif role == 'staff':
            profile_form = StaffForm()
        
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'role': role})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to appropriate dashboard based on user role
                if hasattr(user, 'patient'):
                    return redirect('patient_dashboard')
                elif hasattr(user, 'doctor'):
                    return redirect('doctor_dashboard')
                elif hasattr(user, 'staff'):
                    return redirect('staff_dashboard')
            else:
                # Handle invalid login details
                return render(request, 'login.html', {'form': form, 'invalid_creds': True})
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# Patient dashboard
@login_required
def patient_dashboard(request):
    if hasattr(request.user, 'patient'):
        patient = request.user.patient
        # Fetch appointments, prescriptions, and bills for the patient
        appointments = Appointment.objects.filter(patient=patient)
        prescriptions = Prescription.objects.filter(patient=patient)
        bills = Billing.objects.filter(patient=patient)

        # Allow patient to delete prescriptions
        if request.method == 'POST':
            prescription_id = request.POST.get('prescription_id')
            prescription = get_object_or_404(Prescription, id=prescription_id)
            if prescription.patient == patient:
                prescription.delete()
                return redirect('patient_dashboard')

        return render(request, 'patient_dashboard.html', {'appointments': appointments, 'prescriptions': prescriptions, 'bills': bills})
    return redirect('home')

# Doctor dashboard
@login_required
def doctor_dashboard(request):
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
        appointments = Appointment.objects.filter(doctor=doctor)
        return render(request, 'doctor_dashboard.html', {'appointments': appointments})
    return redirect('home')

# Staff dashboard
@login_required
def staff_dashboard(request):
    if hasattr(request.user, 'staff'):
        staff_member = request.user.staff
        # Fetch relevant data
        inventories = Inventory.objects.all()
        prescriptions = Prescription.objects.all()  # Staff can view all prescriptions
        patients = Patient.objects.filter(staff=staff_member)
        bills = Billing.objects.filter(patient__in=patients)
        doctors = Doctor.objects.all()
        staff = Staff.objects.all()

        # Handle delete bill request
        if request.method == 'POST':
            bill_id = request.POST.get('bill_id')
            bill = get_object_or_404(Billing, id=bill_id)
            if bill.patient in patients:
                bill.delete()
                return redirect('staff_dashboard')

        return render(request, 'staff_dashboard.html', {
            'prescriptions': prescriptions,
            'inventories': inventories,
            'doctors': doctors,
            'staff': staff,
            'patients': patients,
            'bills': bills
        })
    return redirect('home')

# Book appointment view
@login_required
def book_appointment(request):
    if hasattr(request.user, 'patient'):
        if request.method == 'POST':
            form = AppointmentForm(request.POST)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.patient = request.user.patient
                appointment.save()
                return redirect('patient_dashboard')
        else:
            form = AppointmentForm()
        return render(request, 'book_appointment.html', {'form': form})
    return redirect('home')

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the logged-in user is either the patient or the doctor of the appointment
    if request.user == appointment.patient.user or (request.user == appointment.doctor.user and appointment.status == 'Completed'):
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
    elif hasattr(request.user, 'staff'):
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this appointment.')

    # Redirect based on the user's role
    if hasattr(request.user, 'patient'):
        return redirect('patient_dashboard')
    elif hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')
    elif hasattr(request.user, 'staff'):
        return redirect('staff_dashboard')
    else:
        return redirect('home')


@login_required
def manage_appointments(request):
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
        appointments = Appointment.objects.filter(doctor=doctor)

        if request.method == 'POST':
            appointment_id = request.POST.get('appointment_id')
            appointment = get_object_or_404(Appointment, id=appointment_id)
            action = request.POST.get('action')

            if action == 'Cancel':
                appointment.status = 'Canceled'
                messages.success(request, 'Appointment canceled successfully.')
            elif action == 'Reschedule':
                new_date_str = request.POST.get('new_date')
                if new_date_str:
                    try:
                        new_date = datetime.fromisoformat(new_date_str)
                        appointment.date = new_date
                        appointment.status = 'Rescheduled'
                        messages.success(request, 'Appointment rescheduled successfully.')
                    except ValueError:
                        messages.error(request, 'Invalid date format.')
            elif action == 'Accept':
                appointment.status = 'Accepted'
                messages.success(request, 'Appointment accepted successfully.')
            elif action == 'Complete':
                appointment.status = 'Completed'
                messages.success(request, 'Appointment marked as completed successfully.')

            appointment.save()
            return redirect('manage_appointments')

        return render(request, 'doctor_dashboard.html', {'appointments': appointments})
    return redirect('home')


# Add inventory view
@login_required
def add_inventory(request):
    if hasattr(request.user, 'staff'):
        if request.method == 'POST':
            form = InventoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('staff_dashboard')  # Redirect to staff dashboard
        else:
            form = InventoryForm()
        return render(request, 'add_inventory.html', {'form': form})
    return redirect('home')

# Update inventory view
@login_required
def update_inventory(request, id):
    if hasattr(request.user, 'staff'):
        inventory = get_object_or_404(Inventory, id=id)
        if request.method == 'POST':
            form = InventoryForm(request.POST, instance=inventory)
            if form.is_valid():
                form.save()
                return redirect('staff_dashboard')  # Redirect to staff dashboard
        else:
            form = InventoryForm(instance=inventory)
        return render(request, 'update_inventory.html', {'form': form})
    return redirect('home')

login_required
def view_prescriptions(request):
    if hasattr(request.user, 'patient'):
        prescriptions = Prescription.objects.filter(patient=request.user.patient)
    elif hasattr(request.user, 'staff'):
        prescriptions = Prescription.objects.all()
    else:
        return redirect('home')

    return render(request, 'view_prescriptions.html', {'prescriptions': prescriptions})


def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)

    # Check if the logged-in user is authorized to delete the prescription
    if request.user == prescription.patient.user:
        prescription.delete()
        messages.success(request, 'Prescription deleted successfully.')
    elif hasattr(request.user, 'doctor'):
        if request.user == prescription.doctor.user:
            prescription.delete()
            messages.success(request, 'Prescription deleted successfully.')
    elif hasattr(request.user, 'staff'):
        # Staff can delete any prescription, but it should not reflect for doctors or patients
        prescription.delete()
        messages.success(request, 'Prescription deleted successfully.')

    # Redirect to appropriate dashboard based on the user's role
    if hasattr(request.user, 'patient'):
        return redirect('view_prescriptions')
    elif hasattr(request.user, 'staff'):
        return redirect('view_prescriptions_and_bills')
    elif hasattr(request.user, 'doctor'):
        return redirect('manage_prescriptions', patient_id=prescription.patient.id)
    else:
        return redirect('home')
    
@login_required
def generate_bill(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    doctor = prescription.doctor

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            billing_amount = form.cleaned_data['billing_amount']

            # Save the billing information
            bill = Billing(patient=prescription.patient, doctor=doctor, amount=billing_amount,
                           date=datetime.now(), description=f"Bill generated for {prescription.patient.user.get_full_name()} by Dr. {doctor.user.get_full_name()}")
            bill.save()

            return redirect('view_prescriptions_and_bills')  # Redirect to view all prescriptions and bills after successful bill generation
    else:
        form = BillingForm()

    return render(request, 'generate_bill.html', {'form': form})

@login_required
def view_prescriptions_and_bills(request):
    if hasattr(request.user, 'staff'):
        prescriptions = Prescription.objects.all()
        bills = Billing.objects.all()
    else:
        return redirect('home')

    return render(request, 'view_prescriptions_and_bills.html', {'prescriptions': prescriptions, 'bills': bills})

@login_required
def delete_bill(request, bill_id):
    bill = get_object_or_404(Billing, id=bill_id)

    # Check if the logged-in user is staff or the patient associated with the bill
    if hasattr(request.user, 'staff') or request.user == bill.patient.user:
        bill.delete()

    # Redirect based on the user's role
    if hasattr(request.user, 'staff'):
        return redirect('view_prescriptions_and_bills')
    else:
        return redirect('patient_dashboard')

@login_required
def manage_prescriptions(request, patient_id):
    if hasattr(request.user, 'doctor'):
        patient = get_object_or_404(Patient, id=patient_id)
        prescriptions = Prescription.objects.filter(patient=patient, doctor=request.user.doctor)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            prescription_id = request.POST.get('prescription_id')
            
            if action == 'create':
                form = PrescriptionForm(request.POST)
                if form.is_valid():
                    prescription = form.save(commit=False)
                    prescription.doctor = request.user.doctor
                    prescription.patient = patient
                    prescription.save()
                    messages.success(request, 'Prescription created successfully.')
            elif action == 'update':
                prescription = get_object_or_404(Prescription, id=prescription_id)
                form = PrescriptionForm(request.POST, instance=prescription)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Prescription updated successfully.')
            elif action == 'delete':
                prescription = get_object_or_404(Prescription, id=prescription_id)
                prescription.delete()
                messages.success(request, 'Prescription deleted successfully.')
            
            return redirect('manage_prescriptions', patient_id=patient.id)
        else:
            form = PrescriptionForm()
        
        return render(request, 'manage_prescriptions.html', {
            'form': form,
            'prescriptions': prescriptions,
            'patient': patient
        })
    return redirect('home')

@login_required
def update_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prescription updated successfully.')
            return redirect('manage_prescriptions', patient_id=prescription.patient.id)
    else:
        form = PrescriptionForm(instance=prescription)
    
    return render(request, 'update_prescription.html', {'form': form, 'prescription': prescription})

@login_required
def delete_inventory(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    
    if request.method == 'POST':
        inventory.delete()
        messages.success(request, 'Inventory item deleted successfully.')
        return redirect('staff_dashboard')  # Redirect back to staff dashboard after deletion
    return redirect('staff_dashboard') 


@login_required
def add_doctor(request):
    if hasattr(request.user, 'staff'):
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            doctor_form = DoctorForm(request.POST)
            if user_form.is_valid() and doctor_form.is_valid():
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password1'])  # Set the password
                    user.save()
                    doctor = doctor_form.save(commit=False)
                    doctor.user = user
                    doctor.save()
                return redirect('staff_dashboard')  # Redirect to staff dashboard after adding doctor
        else:
            user_form = UserRegistrationForm()
            doctor_form = DoctorForm()
        return render(request, 'add_doctor.html', {'user_form': user_form, 'doctor_form': doctor_form})
    return redirect('home')

def add_staff(request):
    if hasattr(request.user, 'staff'):
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            staff_form = StaffForm(request.POST)
            if user_form.is_valid() and staff_form.is_valid():
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password1'])  # Set the password
                    user.save()
                    staff_member = staff_form.save(commit=False)
                    staff_member.user = user
                    staff_member.save()
                return redirect('staff_dashboard')  # Redirect to staff dashboard after adding staff member
        else:
            user_form = UserRegistrationForm()
            staff_form = StaffForm()
        return render(request, 'add_staff.html', {'user_form': user_form, 'staff_form': staff_form})
    return redirect('home')
    
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.delete()
        return redirect('staff_dashboard')  # Redirect to the staff dashboard or any appropriate URL
    return render(request, 'doctor_delete', {'doctor': doctor})

def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        staff.delete()
        return redirect('staff_dashboard')  # Redirect to the staff dashboard or any appropriate URL
    return render(request, 'staff_delete', {'staff': staff})