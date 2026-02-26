from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Register(AbstractUser):
    usertype = models.IntegerField(default=0)
    phone = models.IntegerField(default=0)
    name = models.CharField(max_length=200, default='', null=True)
    place = models.CharField(max_length=200,  default='', null=True)
    reject_reason = models.TextField(default='', null=True)
    image = models.FileField(null=True,upload_to='uploads/')
    is_approved = models.BooleanField(default=False)
    experience = models.CharField(max_length=200, default='')
    qualification = models.CharField(max_length=50,default='')
    specialization = models.CharField(max_length=50,default='')
    location = models.CharField(max_length=200,  default='', null=True)
    lat = models.FloatField(max_length=200, null=True)
    long = models.FloatField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    

class PredictionResult(models.Model):
    """Model to store uploaded brain scan images and their prediction results"""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='predictions')
    uploaded_image = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=50)
    confidence = models.FloatField()
    all_probabilities = models.JSONField(default=dict, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.predicted_class} ({self.confidence:.2%})"


class DoctorProfile(models.Model):
    doctor = models.OneToOneField(Register, on_delete=models.CASCADE, related_name='doctor_profile')
    bio = models.TextField(default='', blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    consultation_mode = models.CharField(max_length=50, default='Online')
    clinic_address = models.CharField(max_length=255, default='', blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"DoctorProfile({self.doctor.username})"


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_minutes = models.PositiveIntegerField(default=30)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    mode = models.CharField(max_length=50, default='Online')
    notes = models.CharField(max_length=255, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor.username} {self.date} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rescheduled', 'Rescheduled'),
    ]
    patient = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='doctor_appointments')
    availability = models.ForeignKey(DoctorAvailability, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    predicted_class = models.CharField(max_length=50, default='', blank=True)
    prediction_result = models.ForeignKey(PredictionResult, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Appointment({self.patient.username} -> {self.doctor.username})"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, default='', blank=True)
    razorpay_payment_id = models.CharField(max_length=100, default='', blank=True)
    razorpay_signature = models.CharField(max_length=200, default='', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment({self.appointment_id}, {self.status})"


class Feedback(models.Model):
    SECTION_CHOICES = [
        ('doctor', 'Doctor'),
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('platform', 'Platform'),
    ]
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='feedbacks')
    doctor = models.ForeignKey(Register, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctor_feedbacks')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='platform')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback({self.user.username}, {self.section}, {self.rating})"


class Notification(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100, default='Notification')
    message = models.TextField(default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification({self.user.username})"


class ChatMessage(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"ChatMessage({self.sender.username})"


class Document(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='uploaded_documents')
    file = models.FileField(upload_to='documents/')
    description = models.CharField(max_length=255, default='', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document({self.appointment_id})"


class TreatmentPlan(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='treatment_plan')
    plan_text = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TreatmentPlan({self.appointment_id})"


class PatientMedicalHistory(models.Model):
    patient = models.OneToOneField(Register, on_delete=models.CASCADE, related_name='medical_history')
    summary = models.TextField(default='', blank=True)
    allergies = models.TextField(default='', blank=True)
    medications = models.TextField(default='', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MedicalHistory({self.patient.username})"


class DoctorQuery(models.Model):
    patient = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='queries')
    doctor = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='doctor_queries')
    question = models.TextField()
    answer = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"DoctorQuery({self.patient.username} -> {self.doctor.username})"

