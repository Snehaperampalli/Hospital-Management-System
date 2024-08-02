from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    medical_history = models.TextField()

    def __str__(self):
        return f"{self.user.username} - Patient"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} - Doctor ({self.specialty})"

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='staff', null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} - Staff ({self.role})"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=50, default='Scheduled', choices=[
        ('Accepted', 'Accepted'),
        ('Scheduled', 'Scheduled'),
        ('Rescheduled', 'Rescheduled'),
        ('Canceled', 'Canceled'),
        ('Completed', 'Completed'),
    ])

    def __str__(self):
        return f"{self.patient.user.username} - {self.doctor.user.username} on {self.date}"

class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"Billing for {self.patient.user.username} on {self.date}"

class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.item_name} - {self.quantity} items"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions',null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    medicine = models.CharField(max_length=255, default='')
    dosage = models.CharField(max_length=100, default='')
    duration = models.CharField(max_length=50, default='')
    created_at = models.DateTimeField(auto_now_add=True,null=True) 

    def __str__(self):
        return f"Prescription for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"
