from django.contrib import admin
from .models import Patient, Staff, Appointment, Billing, Inventory,Doctor

admin.site.register(Patient)
admin.site.register(Staff)
admin.site.register(Appointment)
admin.site.register(Billing)
admin.site.register(Inventory)
admin.site.register(Doctor)