from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from user_app.models import *
from django.urls import *
from django.http import HttpResponseForbidden
from django.views.generic import *
# Create your views here.
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from user_app.models import Register
from user_app.forms import RejectReasonForm
from django.urls import reverse





def doctor_approval_list(request):     
    if not request.user.is_staff:         
        return HttpResponseForbidden("You are not authorized to view this page.")      

    doctors = Register.objects.filter(usertype=2, is_approved=False)          

    if request.method == 'POST':         
        doctor_id = request.POST.get('doctor_id')         
        action = request.POST.get('action')                  

        doctor = get_object_or_404(Register, pk=doctor_id, usertype=2, is_approved=False)                  

        if action == 'approve':             
            doctor.is_active = True             
            doctor.is_approved = True             
            doctor.save()                          

            # send_mail(                 
            #     'Doctor Approval Notification',                 
            #     f'Dear {doctor.username},\n\nYour account has been approved and activated. You can now log in and access the platform.\n\nThank you!',                 
            #     settings.DEFAULT_FROM_EMAIL,                 
            #     [doctor.email],                 
            #     fail_silently=False,             
            # )         
        elif action == 'reject':             
            return redirect(reverse('reject_reason', args=[doctor.id]))  # Redirect to reject reason page

        return redirect(reverse('doctor_approval_list'))  # Redirect back to the doctor approval list

    return render(request, 'doctor_approval_list.html', {'doctors': doctors})


def reject_reason(request, id):     
    if request.method == "POST":    
        form=RejectReasonForm(request.POST)   
        if form.is_valid():  
            doctor = get_object_or_404(Register, pk=id, usertype=2, is_approved=False)         
            reject_reason = request.POST['reject_reason']         
            # send_mail(                 
            #     'Doctor Application Rejected',                 
            #     f'Dear {doctor.username},\n\nWe regret to inform you that your application has been rejected. For more details, please contact support.\n\nReason for the rejection is {reject_reason}.\n\nThank you!',                 
            #     settings.DEFAULT_FROM_EMAIL,                 
            #     [doctor.email],                 
            #     fail_silently=False,             
            # )         
            doctor.delete()         
            return redirect(reverse('doctor_approval_list'))  # Redirect to doctor approval list
    else:
        form=RejectReasonForm()  
    return render(request,'reject_reason.html',{'form':form})  # Render the reject reason page

class MyModelListView(ListView):
    model = Register
    template_name = 'model_list.html'   
    context_object_name = 'mymodels'


    def get_queryset(self):
        usertype = self.kwargs.get('usertype')
        print(f"Fetching users with usertype: {usertype}")  # Debug log
        return Register.objects.filter(usertype=usertype, is_active=True)
    
    
    