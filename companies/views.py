from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from companies.forms import CompanySignUpForm, JobPostForm, CompanyProfileForm, UpdateEmailForm, UserPasswordChangeForm
from admin_dashboard.models import Company, Application, Job, Category
from django.db import IntegrityError
from django.db.models import Count
from admin_dashboard.models import Company

# Company Signup View
def company_signup(request):
    #consume any existing messages before rendering the page
    storage=messages.get_messages(request)
    for _ in storage:
        pass

    if request.method == 'POST':
        form = CompanySignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Company account created successfully!')
            return redirect('companies:company_dashboard')
    else:
        form = CompanySignUpForm()

    context = {
        'form': form,
        'page_title': 'Company Sign Up',
    }
    return render(request, 'registration/company_signup.html', context)

# Company Login View
def company_login(request):
    storage=messages.get_messages(request)
    for _ in storage:
        pass

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome back, {username}!')
                return redirect('companies:company_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        storage=messages.get_messages(request)
        for _ in storage:
            pass
        form = AuthenticationForm()

    context = {
        'form': form,
        'page_title': 'Company Login',
    }
    return render(request, 'registration/company_login.html', context)

# Company Logout_view
def company_logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    storage=messages.get_messages(request)
    for _ in storage:
        pass
    return redirect('home')

@login_required(login_url='companies:company_login')
def company_dashboard(request):
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request, 'Please complete your company profile.')
        return redirect('companies:profile_settings')
    
    #Dynamic counts from the database
    total_jobs=Job.objects.filter(company=company).count()
    active_jobs=Job.objects.filter(company=company, status='active').count()

    #assuming applications have a 'job' foreign key and a 'status' field
    pending_applications=Application.objects.filter(
        job__company=company,
        status='pending'
    ).count()

    context = {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'pending_applications': pending_applications,
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard/dashboard.html', context)

# Placeholder views for the new pages
@login_required(login_url='companies:company_login')
def post_job(request):
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request,"Company profile not found.")
        return redirect('companies:company_dashboard')
    
    #Add the check for admin approval
    if not company.is_approved:
        messages.warning(request,"Your company account is not yet approved by admin.")
        return redirect('companies:company_dashboard')
    
    if request.method=='POST':
        form=JobPostForm(request.POST)
        if form.is_valid():
            try:
                new_job=form.save(commit=False)
                new_job.company=company
                new_job.status='active' 
                new_job.save()

                if new_job.category:
                    new_job.category.job_count +=1
                    new_job.category.save()

                messages.success(request,"Your job has been posted successfully.")
                return redirect('companies:my_jobs')
            
            except IntegrityError:
                messages.error(request,"An error occured while saving the job.")

    else:
        form=JobPostForm()

    context={
        'form':form,
        'company':company,
        'active_page':'post_job',
    }
    return render(request, 'dashboard/post_job.html', context)

#Manage job section
@login_required(login_url='companies:company_login')
def my_jobs(request):
    try:
        company=request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request,"Company profile not found.")
        return redirect('companies:company_dashboard')
    
    #get all jobs for the company and annotate with the count of applications
    all_jobs=Job.objects.filter(
        company=company
    ).annotate(
        application_count=Count('application')
    ).order_by('-posted_at')

    context={
        'company':company,
        'all_jobs':all_jobs,
        'active_page':'my_jobs'
    }
    return render(request, 'dashboard/my_jobs.html', context)

#Manage candidate section
@login_required(login_url='companies:company_login')
def manage_candidates(request):
    try:
        company=request.user.company_profile
    except:
        messages.error(request,"Company profile not found.")
        return redirect('companies:company_dashboard')
    
    #Fetch all applications for all jobs posted by the company
    all_applications=Application.objects.filter(
        job__company=company 
    ).order_by('-applied_at')

    context={
        'company':company,
        'all_applications':all_applications,
        'active_page':'manage_candidates'
    }
    return render(request,'dashboard/manage_candidate.html', context)


#Company Profile Settings Section
@login_required(login_url='companies:company_login')
def profile_settings(request):
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        # Create a new Company profile if one does not exist for the user
        company = Company.objects.create(user=request.user)

    if request.method == 'POST':
        # Determine which form was submitted based on the button value
        if 'profile_submit' in request.POST:
            form = CompanyProfileForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your company profile has been updated successfully!')
                return redirect('companies:profile_settings')
            else:
                messages.error(request, 'Please correct the errors in the profile form.')
        elif 'social_submit' in request.POST:
            form=CompanyProfileForm(request.POST, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request,'Your social media links have been updated successfully!')
                return redirect('companies:profile_settings')
            else:
                messages.error(request,'Please correct the errors in the social media form.')
        elif 'email_submit' in request.POST:
            update_email_form = UpdateEmailForm(request.POST, instance=request.user)
            if update_email_form.is_valid():
                update_email_form.save()
                messages.success(request, 'Your email has been updated successfully!')
                return redirect('companies:profile_settings')
            else:
                messages.error(request, 'Please correct the errors in the email form.')
        elif 'password_submit' in request.POST:
            change_password_form = UserPasswordChangeForm(user=request.user, data=request.POST)
            if change_password_form.is_valid():
                user = change_password_form.save()
                update_session_auth_hash(request, user)  # Important to update the session
                messages.success(request, 'Your password has been updated successfully!')
                
                # Clear the session data after a successful password change
                if 'otp' in request.session:
                    del request.session['otp']
                if 'otp_verified' in request.session:
                    del request.session['otp_verified']
                    
                return redirect('companies:profile_settings')
            else:
                messages.error(request, 'Please correct the errors in the password form.')
        else:
            messages.error(request, 'Invalid form submission.')
            
    # These forms are created for the GET request and for the POST request if validation fails
    form = CompanyProfileForm(instance=company)
    update_email_form = UpdateEmailForm(instance=request.user)
    change_password_form = UserPasswordChangeForm(user=request.user)

    context = {
        'company': company,
        'form': form,
        'update_email_form': update_email_form,
        'change_password_form': change_password_form,
        'active_page': 'profile_settings',
    }
    return render(request, 'dashboard/profile_settings.html', context)



#Action section for manage job section
#delete a particular job
@login_required(login_url='companies:company_login')
def delete_job(request, job_id):

    job=get_object_or_404(Job, pk=job_id, company=request.user.company_profile)

    if request.method=='POST':

        if job.category:
            job.category.job_count -=1
            job.category.save()
        job.delete()
        messages.success(request,f'Job "{job.title}" has been deleted successfully.')
        return redirect('companies:my_jobs')
    
    messages.error(request,"Invalid request. Please confirm deletion via a POST method")
    return redirect('companies:my_jobs')


#Edit job in manage job section
@login_required(login_url='companies:company_login')
def edit_job(request,job_id):
    try:
        company=request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request,"Company profile not found.")
        return redirect('companies:company_dashboard')
    
    job=get_object_or_404(Job, pk=job_id, company=company)

    if request.method=='POST':
        form=JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request,f'Job "{job.title}" has been updated successfully!')
            return redirect('companies:my_jobs')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form=JobPostForm(instance=job)

    context={
        'form':form,
        'job':job,
        'company':company,
        'active_page':'my_jobs',
    }
    return render(request,'dashboard/edit_job.html',context)

#manage applicants
@login_required(login_url='companies:company_login')
def manage_applicants(request, job_id):
    job=get_object_or_404(Job, pk=job_id, company__user=request.user)
    applicants=Application.objects.filter(job=job)

    context={
        'job':job,
        'applicants':applicants,
        'active_page':'my_jobs',
    }
    return render(request,'dashboard/manage_applicants.html',context)

@login_required(login_url='companies:company_login')
def toggle_job_status(request, job_id):
    if request.method=='POST':
        job=get_object_or_404(Job, pk=job_id, company__user=request.user)

        if job.status=='active':
            job.status='paused'
            messages.success(request, f'Job "{job.title}" has been paused.')
        else:
            job.status='active'
            messages.success(request,f'Job "{job.title}" has been activated.')

        job.save()

    return redirect('companies:my_jobs')

#Email update for company profile
@login_required(login_url='company:company_login')
def update_email(request):
    if request.method=='POST':
        update_email_form=UpdateEmailForm(request.POST, instance=request.user)
        if update_email_form.is_valid():
            update_email_form.save()
            messages.success(request,'Your email has been updated successfully!')
        else:
            messages.error(request,'Please correct the errors in the email form.')
    return redirect('companies:profile_settings')

#Send otp for change password
@login_required(login_url='companies:company_login')
def send_otp(request):
    if request.method=='POST':
        otp=random.randint(100000,999999)
        request.session['otp']=otp
        request.session['otp_verified']=False

        email=request.user.email
        if email:
            subject='Password Change OTP'
            html_message=render_to_string('dashboard/otp_email.html', {'otp':otp})
            plain_message=strip_tags(html_message)
            from_email=settings.EMAIL_HOST_USER
            to_list=[email]

            send_mail(subject,plain_message, from_email, to_list, html_message=html_message)
            messages.info(request,'An OTP has been sent to your registered email address.')
        else:
            messages.error(request,'No email address found for your account.')

    return redirect('companies:profile_settings')

#OTP verification
@login_required(login_url='companies:company_login')
def verify_otp(request):
    if request.methos=='POST':
        user_otp=request.POST.get('otp')
        stored_otp=request.session.get('otp')

        if user_otp and stored_otp and user_otp==str(stored_otp):
            request.session['otp_verified']=True
            messages.success(request,'OTP verified successfully. You can now change your password.')
        else:
            messages.error(request,'Invalid OTP.Please try again.')
            request.session['otp_verified']=False

    return redirect('companies:profile_settings')

#Password change section
@login_required(login_url='companies:company_login')
def change_password(request):
    if not request.session.get('otp_verified'):
        messages.error(request,'Please verify your OTP before changing your password.')
        return redirect('companies:profile_settings')
    
    if request.method=='POST':
        change_password_form=UserPasswordChangeForm(user=request.user, data=request.POST)
        if change_password_form.is_valid():
            user=change_password_form.save()
            update_session_auth_hash(request,user)
            messages.success(request,'Your password has been updated successfully!')

            #clear the session data after a successful password change
            if 'otp' in request.session:
                del request.session['otp']
            if 'otp_verified' in request.session:
                del request.session['otp_verified']

            return redirect('companies:profile_settings')
        else:
            messages.error(request,'Please correct the errors in the password form.')
            return redirect('companies:profile_settings')
        
    return redirect('companies:profile_settings')
            


