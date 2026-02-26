from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from . models import *
from .forms import *
from  django.core.files.storage import FileSystemStorage
import os
import sys
import json
import uuid
import shutil
import secrets
import string
# from django.db.models import F, FloatField, ExpressionWrapper, Func
from django.views.generic import *
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from django.db.models import Count
import random

def generate_random_password(length=6):
    characters = string.ascii_letters # Only letters as requested
    return ''.join(random.choice(characters) for _ in range(length))

try:
    import razorpay
except Exception:
    razorpay = None



def index(request):
    doc=Register.objects.filter(usertype=2).count()
    print(doc)
    
    return render(request,'index.html',{'doc':doc})

def predict(request):
    return render(request,'predict.html')

def about(request):
    return render(request,'about.html')

def doLogin(request):
    form = LoginForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, f"Username and password are required.", extra_tags='log')
            return render(request, 'login.html', {'form': form})

        # Check if the username exists in the database
        if not Register.objects.filter(username=username).exists():
            messages.error(request, f"This user is not registered. Please sign up first.", extra_tags='reg')
            return render(request, 'login.html', {'form': form})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, f"Invalid password. Please try again.", extra_tags='reg')
            return render(request, 'login.html', {'form': form})

        # Log the user in and set session data
        login(request, user)
        data = Register.objects.get(username=user)
        if data.is_superuser == True:
            data.usertype = 0
            data.save()
        request.session['ut'] = data.usertype
        request.session['uid'] = data.id
        messages.success(request, f"Login Successful! Welcome {data.username}.", extra_tags='log')
        
        if data.usertype == 0:
            return redirect('admin_dashboard')
        elif data.usertype == 1:
            return redirect('user_dashboard')
        elif data.usertype == 2:
            return redirect('doctor_dashboard')
        
        return redirect('/')

    return render(request, 'login.html', {'form': form}) 

def logout(request):
    auth.logout(request)
    return redirect('/') 

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if Register.objects.filter(email=email).exists():
                login_form = LoginForm()  
                messages.success(request, f'User Already Exist', extra_tags='log')
                return render(request, 'login.html', {'form': login_form, 'z': True})
            else:
                try:
                    user = form.save(commit=False)
                    user.password = make_password(form.cleaned_data['password'])
                    user.usertype = 1
                    user.is_approved = True
                    user.save()
                    messages.success(request, f'Your registration has been successful! You can login now.', extra_tags='log')
                    return redirect('/login')
                except Exception as e:
                    form.add_error(None, f'An error occurred while saving the form: {e}')
        else:
            print(form.errors)
        return render(request, 'register.html', {'form': form})
    else:
        form = UserRegisterForm()
        title='User Register'
    return render(request, 'register.html', {'form': form,'title':'title'})


def doctor_register(request):
    print("lkshdkjcabsdjhvbajdshv")
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST, request.FILES)
        print(form.errors)
        print(request.POST['username'])
        if form.is_valid():
            username = form.cleaned_data["username"]
            print(username, "uname")
            if Register.objects.filter(username=username).exists():
                login_form = LoginForm()  
                messages.success(request, 'Invalid username', extra_tags='log_dr')
                return render(request, 'login.html', {'form': login_form, 'z': True})
            email = form.cleaned_data["email"]
            if Register.objects.filter(email=email).exists():
                login_form = LoginForm()  
                return render(request, 'login.html', {'form': login_form, 'z': True})
            else:
                try:
                    user = form.save(commit=False)
                    user.password = make_password(form.cleaned_data['password'])
                    user.usertype = 2
                    user.is_approved = False
                    user.save()
                    form.save_m2m()
                    messages.success(request, 'Your registration has been successful! You can login only after admin approval.', extra_tags='log_dr')
                    return redirect('/login')
                except Exception as e:
                    form.add_error(None, f'An error occurred while saving the form: {e}')
        else:
            # Here, we're passing form.errors to the template when the form is invalid
            print(form.errors)
            messages.error(request, 'There were errors in your form. Please check the details and try again.')
        return render(request, 'doctor_register.html', {'form': form})
    else:
        form = DoctorRegisterForm()
        print(form.errors)
        title = 'Doctor Register'
    return render(request, 'doctor_register.html', {'form': form, 'title': title})

def forgotpswd(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Register.objects.get(email=email)
            otp = generate_random_password(6).upper()
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            
            # Send OTP email
            subject = 'Password Reset request - Brain Tumour Hub'
            message = f"Hello {user.username},\n\nYour 6-letter OTP for password reset is: {otp}\n\nDo not share this OTP with anyone.\n\nRegards,\nBrain Tumour Hub Team"
            email_from = settings.EMAIL_HOST_USER
            recepient_list = [user.email]  
            send_mail(subject, message, email_from, recepient_list, fail_silently=True)
            
            messages.success(request, f'OTP sent successfully to {email}.', extra_tags='success')
            return redirect('/reset_password')
        except Register.DoesNotExist:
            messages.error(request, 'This email is not registered with an account.', extra_tags='error')
            return render(request, "forgotpswd.html")
            
    return render(request, 'forgotpswd.html', {'user': request.user})

def reset_password(request):
    # Ensure they came from the forgotpswd flow
    if 'reset_email' not in request.session or 'reset_otp' not in request.session:
        messages.error(request, 'Session expired. Please request a new OTP.', extra_tags='error')
        return redirect('/forgotpswd/')
        
    if request.method == "POST":
        otp = request.POST.get('otp', '').upper()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        saved_otp = request.session.get('reset_otp')
        reset_email = request.session.get('reset_email')
        
        if otp != saved_otp:
            messages.error(request, 'Invalid OTP or expired. Please try again.', extra_tags='error')
            return render(request, "reset_password.html")
            
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.', extra_tags='error')
            return render(request, "reset_password.html")
            
        try:
            user = Register.objects.get(email=reset_email)
            user.password = make_password(new_password)
            user.save()
            
            # Clear session variables
            del request.session['reset_otp']
            del request.session['reset_email']
            
            messages.success(request, 'Password reset successful! You can now login with your new password.', extra_tags='success')
            return redirect('/login')
        except Register.DoesNotExist:
            messages.error(request, 'User no longer exists.', extra_tags='error')
            return redirect('/forgotpswd/')
            
    return render(request, "reset_password.html")

def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if the email is already in use by another user
            if Register.objects.filter(email=email).exclude(id=request.user.id).exists():
                form.add_error('email', 'Email already exists')
            else:
                try:
                    user = form.save(commit=False)
                    if form.cleaned_data.get('password'):
                        user.password = make_password(form.cleaned_data['password'])
                    user.save()

                    # Update the session with the new user data
                    update_session_auth_hash(request, user)

                    messages.success(request, 'Profile updated successfully.',extra_tags='log')
                    return redirect('/profile')
                except Exception as e:
                    form.add_error(None, f'An error occurred while updating the profile: {e}')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags='log')
    else:
        initial_data = {
            'username': request.user.username,
            'email': request.user.email,
            'place': request.user.place,
            'phone': request.user.phone,
            'image': request.user.image
        }
        form = ProfileForm(initial=initial_data, instance=request.user)
    
    return render(request, 'update_form.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        print("POST request received.")
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            print("Form is valid.")
            try:
                user = form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in after password change
                messages.success(request, 'Your password has been changed successfully.', extra_tags='log')
                return redirect('/login')
            except Exception as e:
                print(f"Error saving form: {e}")
                messages.error(request, 'An error occurred. Please try again.', extra_tags='log')
        else:
            # Debugging: print form errors
            print("Form is not valid.")
            print(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the error below.', extra_tags='log')
    else:
        print("GET request received.")
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'password_change_form.html', {'form': form})




@login_required
def check_mri(request):
    """View to handle brain scan image upload and prediction"""
    form = ImageUploadForm()
    
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the uploaded image
                uploaded_image = form.cleaned_data['image']
                
                # Save the image temporarily
                fs = FileSystemStorage()
                filename = fs.save(uploaded_image.name, uploaded_image)
                file_path = fs.path(filename)
                
                # Get model path and train directory
                model_path = os.path.join(settings.BASE_DIR, 'models', 'brain_tumor_model.h5')
                train_dir = os.path.join(settings.BASE_DIR, 'archive', 'Training')
                
                # Add BASE_DIR to path for importing predict module
                if str(settings.BASE_DIR) not in sys.path:
                    sys.path.insert(0, str(settings.BASE_DIR))
                
                # Import prediction function
                try:
                    # Try direct import from the package
                    import predict
                    predict_from_upload = predict.predict_from_upload
                except ImportError:
                    # Fallback to absolute file location import
                    import importlib.util
                    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    predict_module_path = os.path.join(current_dir, 'predict.py')
                    if os.path.exists(predict_module_path):
                        spec = importlib.util.spec_from_file_location("predict", predict_module_path)
                        predict_module = importlib.util.module_from_spec(spec)
                        sys.modules["predict"] = predict_module
                        spec.loader.exec_module(predict_module)
                        predict_from_upload = predict_module.predict_from_upload
                    else:
                        messages.error(request, f'Prediction module not found at {predict_module_path}. Please ensure the model files are properly configured.')
                        return render(request, 'predict.html', {'form': form})
                
                # Make prediction
                result = predict_from_upload(
                    model_path=model_path,
                    image_path=file_path,
                    train_dir=train_dir if os.path.exists(train_dir) else None
                )
                
                # Check for errors
                if 'error' in result:
                    messages.error(request, f"Prediction error: {result['error']}")
                    # Clean up temporary file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return render(request, 'predict.html', {'form': form})
                
                # Get prediction details
                predicted_class = result.get('predicted_class', 'Unknown')
                confidence = result.get('confidence', 0.0)
                all_probabilities = result.get('all_probabilities', {})
                
                # Save prediction result to database
                # First, move the uploaded file to the predictions directory
                predictions_dir = os.path.join(settings.MEDIA_ROOT, 'predictions')
                os.makedirs(predictions_dir, exist_ok=True)
                
                # Create a unique filename
                unique_filename = f"{uuid.uuid4()}_{filename}"
                predictions_path = os.path.join(predictions_dir, unique_filename)
                
                # Copy file to predictions directory
                shutil.copy2(file_path, predictions_path)
                
                # Delete temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Save to database
                prediction_result = PredictionResult.objects.create(
                    user=request.user,
                    uploaded_image=f'predictions/{unique_filename}',
                    predicted_class=predicted_class,
                    confidence=confidence,
                    all_probabilities=all_probabilities
                )
                
                # Redirect to results page
                messages.success(request, 'Image uploaded and analyzed successfully!')
                return redirect('prediction_result', prediction_id=prediction_result.id)
                
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                # Clean up temporary file if it exists
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    
    return render(request, 'predict.html', {'form': form})


@login_required
def prediction_result(request, prediction_id):
    """View to display prediction result"""
    prediction = get_object_or_404(PredictionResult, id=prediction_id, user=request.user)
    
    # Format confidence as percentage
    confidence_percent = prediction.confidence * 100
    
    # Get class display name (title case)
    class_display = prediction.predicted_class.title()
    
    # Convert all probabilities to percentages (0-1 to 0-100)
    all_probabilities_percent = {}
    if prediction.all_probabilities:
        for class_name, prob in prediction.all_probabilities.items():
            all_probabilities_percent[class_name] = prob * 100
    
    context = {
        'prediction': prediction,
        'confidence_percent': confidence_percent,
        'class_display': class_display,
        'all_probabilities_percent': all_probabilities_percent,
    }

    class_to_specialization = {
        'glioma': ['Neuro-Oncology', 'Neurosurgery'],
        'meningioma': ['Neuro-Oncology', 'Neurosurgery'],
        'pituitary': ['Neuro-Oncology', 'Neurosurgery'],
        'notumor': ['Neurology', 'Neuro-Oncology'],
    }
    target_specs = class_to_specialization.get(prediction.predicted_class.lower(), ['Neurology'])
    recommended_doctors = Register.objects.filter(
        usertype=2,
        is_active=True,
        is_approved=True,
        specialization__in=target_specs
    )
    context['recommended_doctors'] = recommended_doctors
    
    return render(request, 'prediction_result.html', context)


@login_required
def prediction_history(request):
    """View to display user's prediction history"""
    predictions = PredictionResult.objects.filter(user=request.user).order_by('-uploaded_at')
    
    context = {
        'predictions': predictions,
    }
    
    return render(request, 'prediction_history.html', context)


@login_required
def delete_prediction(request, prediction_id):
    """View to delete a prediction and its associated image"""
    prediction = get_object_or_404(PredictionResult, id=prediction_id, user=request.user)
    
    # Delete the associated image file if it exists
    if prediction.uploaded_image:
        image_path = prediction.uploaded_image.path
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                # Log error but continue with database deletion
                print(f"Error deleting image file: {e}")
    
    # Delete the prediction record
    prediction.delete()
    
    messages.success(request, 'Prediction deleted successfully.')
    return redirect('prediction_history')


def _send_email(subject, message, recipients):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
    except Exception:
        pass


def user_dashboard(request):
    if request.session.get('ut') != 1:
        return HttpResponseForbidden("Not authorized.")
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    queries = DoctorQuery.objects.filter(patient=request.user).order_by('-created_at')[:10]
    predictions_count = PredictionResult.objects.filter(user=request.user).count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    pending_queries = DoctorQuery.objects.filter(patient=request.user, answer__isnull=True).count()
    # Mark notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'user_dashboard.html', {
        'appointments': appointments,
        'notifications': notifications,
        'queries': queries,
        'predictions_count': predictions_count,
        'unread_notifications': unread_notifications,
        'pending_queries': pending_queries,
    })


def doctor_dashboard(request):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-created_at')
    availabilities = DoctorAvailability.objects.filter(doctor=request.user).order_by('date')
    queries = DoctorQuery.objects.filter(doctor=request.user).order_by('-created_at')[:10]
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:8]
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='requested').count()
    unique_patients = appointments.values('patient').distinct().count()
    pending_queries = DoctorQuery.objects.filter(doctor=request.user, answer__isnull=True).count()
    # Mark notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'doctor_dashboard.html', {
        'appointments': appointments,
        'availabilities': availabilities,
        'queries': queries,
        'notifications': notifications,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'unique_patients': unique_patients,
        'pending_queries': pending_queries,
    })


def doctor_profile_edit(request):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    profile, _ = DoctorProfile.objects.get_or_create(doctor=request.user)
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=profile)
    return render(request, 'doctor_profile_edit.html', {'form': form})


def doctor_availability_list(request):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    availabilities = DoctorAvailability.objects.filter(doctor=request.user)
    return render(request, 'doctor_availability_list.html', {'availabilities': availabilities})


def doctor_availability_add(request):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = request.user
            availability.save()
            messages.success(request, 'Availability added.')
            return redirect('doctor_availability_list')
    else:
        form = DoctorAvailabilityForm()
    return render(request, 'doctor_availability_add.html', {'form': form})


def doctor_availability_delete(request, availability_id):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    availability = get_object_or_404(DoctorAvailability, id=availability_id, doctor=request.user)
    availability.delete()
    messages.success(request, 'Availability removed.')
    return redirect('doctor_availability_list')


def book_appointment(request, doctor_id, prediction_id=None):
    if request.session.get('ut') != 1:
        return HttpResponseForbidden("Not authorized.")
    doctor = get_object_or_404(Register, id=doctor_id, usertype=2, is_active=True, is_approved=True)
    prediction = None
    predicted_class = ''
    if prediction_id:
        prediction = get_object_or_404(PredictionResult, id=prediction_id, user=request.user)
        predicted_class = prediction.predicted_class
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doctor
            appointment.predicted_class = predicted_class
            appointment.prediction_result = prediction
            appointment.save()
            Notification.objects.create(
                user=doctor,
                title='New Appointment Request',
                message=f'New appointment request from {request.user.username}.'
            )
            _send_email(
                'New Appointment Request',
                f'You have a new appointment request from {request.user.username}.',
                [doctor.email]
            )
            messages.success(request, 'Appointment requested.')
            return redirect('user_dashboard')
    else:
        form = AppointmentRequestForm()
    return render(request, 'appointment_request.html', {
        'form': form,
        'doctor': doctor,
        'prediction': prediction,
    })


def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user not in [appointment.patient, appointment.doctor]:
        return HttpResponseForbidden("Not authorized.")
    messages_qs = ChatMessage.objects.filter(appointment=appointment)
    documents = Document.objects.filter(appointment=appointment)
    treatment_plan = getattr(appointment, 'treatment_plan', None)
    return render(request, 'appointment_detail.html', {
        'appointment': appointment,
        'messages_qs': messages_qs,
        'documents': documents,
        'treatment_plan': treatment_plan,
    })


def appointment_update_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    if status not in dict(Appointment.STATUS_CHOICES):
        messages.error(request, 'Invalid status.')
        return redirect('doctor_dashboard')
    appointment.status = status
    appointment.save()
    Notification.objects.create(
        user=appointment.patient,
        title='Appointment Update',
        message=f'Your appointment is now {status}.'
    )
    _send_email(
        'Appointment Update',
        f'Your appointment with {appointment.doctor.username} is now {status}.',
        [appointment.patient.email]
    )
    messages.success(request, 'Appointment updated.')
    return redirect('doctor_dashboard')


def send_chat_message(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user not in [appointment.patient, appointment.doctor]:
        return HttpResponseForbidden("Not authorized.")
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(appointment=appointment, sender=request.user, message=message_text)
    return redirect('appointment_detail', appointment_id=appointment.id)


def upload_document(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user not in [appointment.patient, appointment.doctor]:
        return HttpResponseForbidden("Not authorized.")
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.appointment = appointment
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, 'Document uploaded.')
    return redirect('appointment_detail', appointment_id=appointment.id)


def update_treatment_plan(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    plan, _ = TreatmentPlan.objects.get_or_create(appointment=appointment)
    if request.method == 'POST':
        form = TreatmentPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                user=appointment.patient,
                title='Treatment Plan Updated',
                message='Your treatment plan has been updated.'
            )
            messages.success(request, 'Treatment plan updated.')
    return redirect('appointment_detail', appointment_id=appointment.id)


def create_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if razorpay is None:
        messages.error(request, 'Razorpay not installed.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    amount = Decimal('0.00')
    if appointment.availability:
        amount = appointment.availability.fee
    elif hasattr(appointment.doctor, 'doctor_profile'):
        amount = appointment.doctor.doctor_profile.consultation_fee
    amount = amount if amount > 0 else Decimal('500.00')
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({
        'amount': int(amount * 100),
        'currency': 'INR',
        'payment_capture': 1
    })
    payment, _ = Payment.objects.get_or_create(appointment=appointment)
    payment.amount = amount
    payment.razorpay_order_id = order.get('id', '')
    payment.status = 'created'
    payment.save()
    return render(request, 'payment_checkout.html', {
        'appointment': appointment,
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount_paise': int(amount * 100),
        'order_id': payment.razorpay_order_id,
    })


def payment_success(request):
    if request.method != 'POST':
        return redirect('/')
    appointment_id = request.POST.get('appointment_id')
    payment_id = request.POST.get('razorpay_payment_id')
    order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    payment = get_object_or_404(Payment, appointment=appointment)
    payment.razorpay_payment_id = payment_id or ''
    payment.razorpay_order_id = order_id or payment.razorpay_order_id
    payment.razorpay_signature = signature or ''
    if razorpay is not None:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })
            payment.status = 'paid'
        except Exception:
            payment.status = 'failed'
    else:
        payment.status = 'paid'
    payment.save()
    if payment.status == 'paid':
        Notification.objects.create(
            user=appointment.doctor,
            title='Payment Received',
            message=f'Payment received for appointment from {appointment.patient.username}.'
        )
        _send_email(
            'Payment Confirmation',
            f'Payment received for appointment with {appointment.doctor.username}.',
            [appointment.patient.email]
        )
    return render(request, 'payment_success.html', {'appointment': appointment, 'payment': payment})


def submit_feedback(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.doctor = appointment.doctor
            feedback.appointment = appointment
            feedback.save()
            messages.success(request, 'Feedback submitted.')
    return redirect('appointment_detail', appointment_id=appointment.id)


def user_queries(request):
    if request.session.get('ut') != 1:
        return HttpResponseForbidden("Not authorized.")
    if request.method == 'POST':
        form = DoctorQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.patient = request.user
            query.save()
            messages.success(request, 'Query sent.')
            return redirect('user_queries')
    else:
        form = DoctorQueryForm()
        form.fields['doctor'].queryset = Register.objects.filter(usertype=2, is_active=True, is_approved=True)
    
    doctors = Register.objects.filter(usertype=2, is_active=True, is_approved=True)
    queries = DoctorQuery.objects.filter(patient=request.user)
    return render(request, 'user_queries.html', {'form': form, 'queries': queries, 'doctors': doctors})


def doctor_queries(request):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    queries = DoctorQuery.objects.filter(doctor=request.user)
    return render(request, 'doctor_queries.html', {'queries': queries})


def answer_query(request, query_id):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    query = get_object_or_404(DoctorQuery, id=query_id, doctor=request.user)
    if request.method == 'POST':
        form = DoctorAnswerForm(request.POST, instance=query)
        if form.is_valid():
            q = form.save(commit=False)
            q.answered_at = timezone.now()
            q.save()
            Notification.objects.create(
                user=query.patient,
                title='Query Answered',
                message='Your doctor has replied to your query.'
            )
            messages.success(request, 'Answer sent.')
            return redirect('doctor_queries')
    else:
        form = DoctorAnswerForm(instance=query)
    return render(request, 'doctor_answer_query.html', {'form': form, 'query': query})


def medical_history_edit(request):
    if request.session.get('ut') != 1:
        return HttpResponseForbidden("Not authorized.")
    history, _ = PatientMedicalHistory.objects.get_or_create(patient=request.user)
    if request.method == 'POST':
        form = PatientMedicalHistoryForm(request.POST, instance=history)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medical history updated.')
            return redirect('user_dashboard')
    else:
        form = PatientMedicalHistoryForm(instance=history)
    return render(request, 'medical_history_edit.html', {'form': form})


def medical_history_view(request, patient_id):
    if request.session.get('ut') != 2:
        return HttpResponseForbidden("Not authorized.")
    patient = get_object_or_404(Register, id=patient_id, usertype=1)
    history = getattr(patient, 'medical_history', None)
    return render(request, 'medical_history_view.html', {'patient': patient, 'history': history})


def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def user_queries_post(request):
    """Handle standalone query form POST from user_queries page."""
    return user_queries(request)
