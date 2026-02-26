from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from user_app.models import Register, Appointment, Feedback, Payment, Notification, PredictionResult
from user_app.forms import RejectReasonForm, DoctorRegisterForm, ProfileForm
from django.urls import reverse
from decimal import Decimal
import datetime


def _admin_required(request):
    return request.user.is_authenticated and request.user.is_staff


def admin_dashboard(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    stats = {
        'total_doctors': Register.objects.filter(usertype=2).count(),
        'pending_doctors': Register.objects.filter(usertype=2, is_approved=False).count(),
        'total_users': Register.objects.filter(usertype=1).count(),
        'total_predictions': PredictionResult.objects.count(),
        'total_feedbacks': Feedback.objects.count(),
        'total_appointments': Appointment.objects.count(),
    }
    
    recent_doctors = Register.objects.filter(usertype=2).order_by('-date_joined')[:5]
    recent_feedbacks = Feedback.objects.select_related('user').order_by('-created_at')[:5]
    pending_doctor_list = Register.objects.filter(usertype=2, is_approved=False).order_by('-date_joined')[:5]
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]
    
    context = {
        'recent_doctors': recent_doctors,
        'recent_feedbacks': recent_feedbacks,
        'pending_doctor_list': pending_doctor_list,
        'recent_appointments': recent_appointments,
    }
    context.update(stats)
    
    return render(request, 'admin_dashboard.html', context)


def doctor_approval_list(request):
    if not _admin_required(request):
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
            Notification.objects.create(
                user=doctor,
                title='Account Approved!',
                message='Congratulations! Your doctor account has been approved. You can now log in.'
            )
            try:
                send_mail(
                    'Doctor Approval Notification',
                    f'Dear Dr. {doctor.name or doctor.username},\n\nYour account has been approved. You can now log in and access the platform.\n\nThank you,\nBrain Tumour Hub',
                    settings.DEFAULT_FROM_EMAIL,
                    [doctor.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, f'Dr. {doctor.username} approved successfully.')
        elif action == 'reject':
            return redirect(reverse('reject_reason', args=[doctor.id]))
        return redirect(reverse('doctor_approval_list'))
    return render(request, 'doctor_approval_list.html', {'doctors': doctors})


def reject_reason(request, id):
    if request.method == "POST":
        form = RejectReasonForm(request.POST)
        if form.is_valid():
            doctor = get_object_or_404(Register, pk=id, usertype=2, is_approved=False)
            reason_text = request.POST.get('reject_reason', '')
            try:
                send_mail(
                    'Doctor Application Rejected',
                    f'Dear {doctor.name or doctor.username},\n\nWe regret to inform you that your application has been rejected.\n\nReason: {reason_text}\n\nThank you,\nBrain Tumour Hub',
                    settings.DEFAULT_FROM_EMAIL,
                    [doctor.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            doctor.delete()
            messages.success(request, 'Doctor application rejected and removed.')
            return redirect(reverse('doctor_approval_list'))
    else:
        form = RejectReasonForm()
    return render(request, 'reject_reason.html', {'form': form})


class MyModelListView(ListView):
    model = Register
    template_name = 'model_list.html'
    context_object_name = 'mymodels'

    def get_queryset(self):
        usertype = self.kwargs.get('usertype')
        return Register.objects.filter(usertype=usertype, is_active=True)


def admin_doctor_create(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.password = make_password(form.cleaned_data['password'])
            doctor.usertype = 2
            doctor.is_approved = True
            doctor.is_active = True
            doctor.save()
            messages.success(request, f'Doctor account for {doctor.username} created successfully.')
            return redirect('admin_doctor_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorRegisterForm()
    return render(request, 'admin_doctor_create.html', {'form': form})


def admin_doctor_list(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    doctors = Register.objects.filter(usertype=2).order_by('-date_joined')
    return render(request, 'admin_doctor_list.html', {'doctors': doctors})


def admin_user_list(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    users = Register.objects.filter(usertype=1).order_by('-date_joined')
    return render(request, 'admin_user_list.html', {'users': users})


def admin_toggle_active(request, user_id):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    user = get_object_or_404(Register, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} {status}.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def admin_delete_user(request, user_id):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    user = get_object_or_404(Register, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def admin_edit_user(request, user_id):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    user = get_object_or_404(Register, id=user_id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated.')
            if user.usertype == 2:
                return redirect('admin_doctor_list')
            return redirect('admin_user_list')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'admin_doctor_create.html', {'form': form, 'editing': True, 'edit_user': user})


def admin_feedback_list(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")
    feedbacks = Feedback.objects.select_related('user', 'doctor').order_by('-created_at')
    return render(request, 'admin_feedback_list.html', {'feedbacks': feedbacks})


def admin_reports(request):
    if not _admin_required(request):
        return HttpResponseForbidden("You are not authorized.")

    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Current month stats
    month_qs = Appointment.objects.filter(created_at__year=current_year, created_at__month=current_month)
    monthly_stats = {
        'total': month_qs.count(),
        'completed': month_qs.filter(status='completed').count(),
        'pending': month_qs.filter(status__in=['requested', 'confirmed']).count(),
        'revenue': Payment.objects.filter(
            status='paid',
            created_at__year=current_year,
            created_at__month=current_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
    }

    # Monthly breakdown for last 6 months
    monthly_data = []
    max_total = 1
    for i in range(5, -1, -1):
        d = now - datetime.timedelta(days=i * 30)
        y, m = d.year, d.month
        qs = Appointment.objects.filter(created_at__year=y, created_at__month=m)
        total = qs.count()
        completed = qs.filter(status='completed').count()
        revenue = Payment.objects.filter(
            status='paid', created_at__year=y, created_at__month=m
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        month_name = datetime.date(y, m, 1).strftime('%b %Y')
        if total > max_total:
            max_total = total
        monthly_data.append({'month': month_name, 'total': total, 'completed': completed, 'revenue': revenue})
    for row in monthly_data:
        row['pct'] = int((row['total'] / max_total) * 100) if max_total else 0

    # Top doctors
    top_raw = Appointment.objects.values(
        'doctor__name', 'doctor__username'
    ).annotate(count=Count('id')).order_by('-count')[:8]
    top_max = top_raw[0]['count'] if top_raw else 1
    top_doctors = []
    for d in top_raw:
        d['pct'] = int((d['count'] / top_max) * 100) if top_max else 0
        top_doctors.append(d)

    # Status breakdown
    status_raw = Appointment.objects.values('status').annotate(count=Count('id'))
    total_all = Appointment.objects.count() or 1
    status_breakdown = [{'status': s['status'], 'count': s['count'], 'pct': int((s['count'] / total_all) * 100)} for s in status_raw]

    return render(request, 'admin_reports.html', {
        'monthly_stats': monthly_stats,
        'monthly_data': monthly_data,
        'top_doctors': top_doctors,
        'status_breakdown': status_breakdown,
    })
