from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect, get_object_or_404
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
        return render(request, 'register.html', {'form': form})
    else:
        form = DoctorRegisterForm()
        print(form.errors)
        title = 'Doctor Register'
    return render(request, 'register.html', {'form': form, 'title': title})

def forgotpswd(request):
    return render(request, 'forgotpswd.html', {'user': request.user})

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def generate_random_password(length=6):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def reset_password(request):
    if request.method == "POST":

                user = Register.objects.get(username=request.POST['username'])
                print("USERSS",user)
                new_password = generate_random_password()
                user.password = make_password(new_password)
                print('Nesw Passworddddddddd',new_password)
                user.save()
                subject = 'password'
                message = "your password is " + str(new_password)
                email_from = settings.EMAIL_HOST_USER
                recepient_list = [user.email]  
                send_mail(subject,message,email_from,recepient_list)
                messages.success(request, f'New Password is send to your registered email. Use it for login and change your password in your profile section. ', extra_tags='log')
               
    else:
        return render(request,"forgotpswd.html")
    return redirect('/login')

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
                # BASE_DIR is brain_tumour/brain_tumour, parent is brain_tumour/
                project_root = os.path.dirname(settings.BASE_DIR)
                model_path = os.path.join(project_root, 'models', 'brain_tumor_model.h5')
                train_dir = os.path.join(project_root, 'archive', 'Training')
                
                # Add project root to path for importing predict module
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                # Import prediction function
                try:
                    from brain_tumour.predict import predict_from_upload
                except ImportError:
                    # Try alternative path
                    predict_module_path = os.path.join(project_root, 'predict.py')
                    if os.path.exists(predict_module_path):
                        import importlib.util
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