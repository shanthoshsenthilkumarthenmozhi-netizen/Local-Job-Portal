from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from admin_dashboard.models import Company, Job, Category, JobSeeker, Application, SiteSetting, Feedback, Notification
from admin_dashboard.forms import CompanyForm, JobForm, NotificationForm
from django.db.models import Q
from django.core.paginator import Paginator
from admin_dashboard.forms import SiteSettingForm
# Create your views here.


def admin_login_view(request):
    if request.method == "POST":
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user=form.get_user()
            auth_login(request,user)
            return redirect('admin_dashboard')
    else:
        form=AuthenticationForm()
    return render(request, 'admin_login.html',{'form':form})

@login_required(login_url='admin_login')
def admin_dashboard_view(request):
    total_companies=120
    total_users=850
    total_jobs_posted=345
    total_applications=1230

    context={
        'current_page':'dashboard',
        'total_companies':total_companies,
        'total_users':total_users,
        'total_jobs_posted':total_jobs_posted,
        'total_applications':total_applications,
    }
    return render(request,'admin_panel.html')


def logout_view(request):
    auth_logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def post_job_selection_view(request):
    return render(request,'post_job_selection.html')

@login_required(login_url='admin_login')
def register_company_view(request):
    if request.method=='POST':
        company_name=request.POST.get('company_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        website=request.POST.get('website')
        location_address=request.POST.get('location_address')

        #basic validation
        if not all([company_name, username, password, email, location_address]):
            messages.error(request,"Please fill in all required fields")
            return render(request,'register_company.html', {
                'company_name':company_name, 'username':username,'email':email, 'website':website, 'location_address':location_address
            })
        
        #for checking username or email is already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username (Company ID) already exists. Please choose a different one")
            return render(request,'register_company.html',{ 'company_name':company_name, 'username':username, 'email':email, 'website':website, 'location_address':location_address })
        
        try:
            company_user=User.objects.create_user(username=username, email=email, password=password)
            company_user.first_name=company_name
            company_user.save()

            #Create the Company profile linked to this user
            company=Company.objects.create(
                name=company_name,
                email=email,
                website=website,
                address=location_address,
                is_approved=True #Admin is registering, so assume approved
            )

            messages.success(request,f"Company '{company_name}' registered successfully! You can now post a job for them.")
            #Redirect to post job form, passing the company ID
            return redirect('post_job_form', company_id=company.id)
        
        except Exception as e:
            messages.error(request, f"An error occured during registration:{e}")
            return render(request, 'register_company.html', {
                'company_name': company_name, 'username':username, 'email':email, 'website':website, 'location_address':location_address
            })
    return render(request,'register_company.html')

@login_required(login_url='admin_login')
def company_login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(request, username=username, password=password)

        if user is not None:
            try:
                company=Company.objects.get(user__email=user.email)
                messages.success(request, f"Successfully logged in as '{company.company_name}'. Now you can post the job")
                return redirect('post_job_form', company_id=company.id)
            except Company.DoesNotExist:
                messages.error(request, "User is not associated with a registered company.")
        else:
            messages.error(request,"Invalid Username or Password.")
        
        return render(request, 'company_login.html',{'username':username})
    return render(request, 'company_login.html')

@login_required(login_url='admin_login')
def post_job_form_view(request, company_id):
    try:
        company=Company.objects.get(id=company_id)
    except Company.DoesNotExists:
        messages.error(request,"Company not found.")
        return redirect('post_job_selection')
    
    categories =Category.objects.all().order_by('name')

    if request.method=='POST':
        category_id=request.POST.get('category')
        title=request.POST.get('title')
        vacancy=request.POST.get('vacancy')
        location=request.POST.get('location')
        job_type=request.POST.get('job_type')
        salary=request.POST.get('salary')
        description=request.POST.get('description')

        #basic validation
        if not all([category_id, title, vacancy, location, job_type, description]):
            messages.error(request, "Please fill in all required fields.")
            context={'company':company, 'categories':categories, 'form_data':request.POST}
            return render(request, 'post_job_form.html', context)
        
        try:
            selected_category=Category.objects.get(id=category_id)

        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            context={'company':company, 'categories':categories, 'form_data':request.POST}
            return render(request, 'post_job_form.html',context)
        
        try:
            job=Job.objects.create(
                company=company,
                category=selected_category,
                title=title,
                vacancy=int(vacancy),
                location=location,
                job_type=job_type,
                description=description,
                status='active',
                salary=salary,
            )
            messages.success(request, f"Job '{job.title}' for '{company.company_name}'posted successfully!")
            return redirect('admin_dashboard')
        except ValueError:
            messages.error(request, "Invalid number format for Vacancy.")
            context={'company':company, 'categories':categories, 'form_data':request.POST}
            return render(request, 'post_job_form.html', context)
        except Exception as e:
            messages.error(request, f"An error occurred while posting the job: {e}")
            context={'company':company,'categories':categories,'form_data':request.POST}
            return render(request,'post_job_form.html',context)
        
    context={
            'company':company,
            'categories':categories,
        }
    return render(request, 'post_job_form.html',context)

# Manage Companies Section
@login_required
def company_list(request):
    companies=Company.objects.all().order_by('company_name')
    context={
        'companies':companies,
        'current_page':'manage_companies'
    }
    return render(request, 'company_list.html', context)

@login_required
def company_create(request):
    if request.method=='POST':
        form=CompanyForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Company registered successfully!')
            return redirect('company_list')
        else:
            form=CompanyForm()
        context={
            'form':form,
            'form_title':'Register New Company',
            'current_page':'manage_companies'
        }
        return render(request,'register_company.html',context)
    
@login_required
def company_detail(request, pk):
    company=get_object_or_404(Company,pk=pk)
    context={
        'company':company,
        'current_page':'manage_companies'
    }
    return render(request,'company_list.html',context)


@login_required
def company_update(request,pk):
        company=get_object_or_404(Company,pk=pk)
        if request.method=='POST':
            form=CompanyForm(request.POST,request.FILES, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request,'Company updated successfully!')
                return redirect('company_detail', pk=company.pk)
        else:
            form=CompanyForm(instance=company)
        context={
            'form':form,
            'company':company,
            'form_title':f'Edit Company:{company.company_name}',
            'submit_button_text':'Update Company',
                'current_page':'manage_companies'
            }
        return render(request,'company_edit.html',context)
        
@login_required
def company_delete(request,pk):
    company=get_object_or_404(Company, pk=pk)
    if request.method=='POST':
        company.delete()
        messages.success(request,'Company deleted successfully!')
        return redirect('company_list')
    context={
        'company':company,
        'current_page':'manage_companies'
    }
    return render(request,'company_confirm_delete.html',context)

# Company Toggle Status view
@login_required
def company_toggle_status(request,pk):
    company=get_object_or_404(Company,pk=pk)
    company.is_active=not company.is_active
    company.save()
    status_message="activated" if company.is_active else "deactivated"
    messages.info(request,f"Company '{company.company_name}' has been {status_message}.")
    return redirect('company_list')

@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-posted_at')

    # Search and filter logic

    query=request.GET.get('q')
    company_filter=request.GET.get('company')
    category_filter=request.GET.get('category')
    job_type_filter=request.GET.get('job_type')
    status_filter=request.GET.get('status')

    if query:
        jobs=jobs.filter(
            Q(title__icontains=query) |
            Q(category__name__icontains=query) |
            Q(location__icontains=query) |
            Q(company__company_name__icontains=query)
        ).distinct()

    if company_filter:
        jobs=jobs.filter(company__id=company_filter)
    if category_filter:
        jobs=jobs.filter(category__id=category_filter)
    if job_type_filter:
        jobs=jobs.filter(job_type=job_type_filter)
    if status_filter:
        if status_filter == 'active':
            jobs=jobs.filter(is_active=True)
        elif status_filter == 'inactive':
            jobs=jobs.filter(is_active=False)
    # End search and filter logic

    #paginatotion
    paginator= Paginator(jobs,10)
    page_number= request.GET.get('page')
    page_obj=paginator.get_page(page_number)


    # for filter dropdowns
    companies = Company.objects.all().order_by('company_name')
    categories = Category.objects.all().order_by('name')
    job_types = Job.JOB_TYPE  #Access form models

    context = {
        'jobs':page_obj,
        'companies':companies, #for company filter dropdown
        'categories':categories,
        'job_types':Job.JOB_TYPE,
        'status_choices':Job.STATUS_CHOICES,
        'query':query,
        'company_filter':company_filter,
        'category_filter':category_filter,
        'job_type_filter':job_type_filter,
        'status_filter':status_filter,
        'current_page':'manage_jobs'
    }
    return render(request,'job_list.html', context)

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job=form.save()
            messages.success(request,f"Job '{job.title}' posted successfully!")
            return redirect('job_list')
    else:
        form =JobForm()

    context = {
        'form':form,
        'form_title':'Post New Job',
        'submit_button_text':'Post Job',
        'current_page':'manage_jobs',
    }
    return render(request,'job_form.html',context)
    
@login_required
def job_update(request,pk):
    job=get_object_or_404(Job, pk=pk)
    if request.method=='POST':
        form=JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully!")
            return redirect('job_list')
    else:
        form=JobForm(instance=job)

    context = {
        'form':form,
        'job':job,
        'form_title':f'Edit JOb:{job.title}',
        'submit_button_text':'Update Job',
        'current_page':'manage_jobs',
    }
    return render(request,'job_form.html',context)
    
@login_required
def job_delete(request,pk):
    job=get_object_or_404(Job, pk=pk)
    if request.method=='POST':
        job.delete()
        messages.success(request,f"Job '{job.title}' deleted successfully!")
        return redirect('job_list')
    
    context = {
        'job':job,
        'current_page':'manage_jobs',
    }
    return render(request,'job_confirm_delete.html',context)

@login_required
def toggle_job_status(request,pk):
    job=get_object_or_404(Job, pk=pk)
    if request.method =='POST':
        job.is_active =not job.is_active
        job.save()
        messages.success(request,f"Job '{job.title}' is now {'Active' if job.is_active else 'Inactive'}.")
    return redirect('job_list')

# Job Seeker
@login_required
def job_seeker_list(request):
    job_seekers = JobSeeker.objects.all().order_by('user__first_name','user__last_name')

    query = request.GET.get('q')
    if query:
        job_seekers = job_seekers.filter(
            Q(user__first_name__icontain=query) |
            Q(user__last_name__icontain=query) |
            Q(user__email__icontains=query)
        ).distinct()

    context = {
        'job_seekers':job_seekers,
        'query':query,
        'current_page':'manage_job_seekers'
    }
    return render(request,'job_seeker_list.html',context)

@login_required
def job_seeker_toggle_status(request, pk):
    job_seeker=get_object_or_404(JobSeeker, pk=pk)
    job_seeker.is_active=not job_seeker.is_active
    job_seeker.save()
    status_message='activated' if job_seeker.is_active else "deactivated"
    messages.success(request, f"Job seeker '{job_seeker.user.username}' has been {status_message}.")
    return redirect('job_seeker_list')

@login_required
def job_seeker_detail(request,pk):
    job_seeker=get_object_or_404(JobSeeker,pk=pk)
    context = {
        'job_seeker':job_seeker,
        'current_page':'manage_job_seekers'
    }
    return render(request, 'job_seeker_detail.html',context)

@login_required
def job_seeker_delete(request,pk):
    job_seeker=get_object_or_404(JobSeeker,pk=pk)
    username=job_seeker.user.username
    if request.method=='POST':
        job_seeker.delete()
        messages.success(request, f"Job seeker '{username}' and their account have been deleted successfully.")
        return redirect('job_seeker_list')
    
    context={
        'job_seeker':job_seeker,
        'current_page':'manage_job_seekers',
    }
    return render(request, 'job_seeker_confirm_delete.html',context)

@login_required
def application_list(request):
    applications=Application.objects.all().order_by('-applied_at')

    # Search and filter logic
    query=request.GET.get('q')
    status_filter=request.GET.get('status')

    if query:
        applications = applications.filter(
            Q(job__title__icontains=query) |
            Q(job_seeker__user__first_name__icontains=query) |
            Q(job_seeker__user__last_name__icontains=query)
        ).distinct()

    if status_filter:
        applications=applications.filter(status=status_filter)

    context = {
        'applications':applications,
        'status_choices':Application.APPLICATION_STATUS_CHOICES,
        'query':query,
        'status_filter':status_filter,
        'current_page':'manage_applications',
    }
    return render(request,'application_list.html', context)

@login_required
def application_detail(request,pk):
    application=get_object_or_404(Application,pk=pk)
    context={
        'application':application,
        'status_choices':Application.APPLICATION_STATUS_CHOICES,
        'current_page':'manage_applications',
    }
    return render(request,'application_detail.html',context)

@login_required
def application_update_status(request,pk):
    if request.method == 'POST':
        application=get_object_or_404(Application, pk=pk)
        new_status=request.POST.get('status')

        if new_status and new_status in dict(Application.APPLICATION_STATUS_CHOICES):
            application.status=new_status
            application.save()
            messages.success(request,f"Application for '{application.job.title}' by {application.job_seeker.user.first_name} has been updated to '{application.get_status_display()}'")
        else:
            messages.error(request,"Invalid status provided.")

        return redirect('application_detail', pk=pk)
    
    return redirect('application_list')


@login_required
def application_delete(request,pk):
    application=get_object_or_404(Application,pk=pk)
    if request.method=='POST':
        app_title=application.job.titl
        app_seeker=application.job_seeker.user.first_name
        application.delete()
        messages.success(request, f"Application for '{app_title}' by {app_seeker} has been deleted successfully.")
        return redirect('application_list')
    
    context={
        'application':application,
        'current_page':'manage_application',
    }
    return render(request,'application_confirm_delete.html',context)

@login_required
def admin_settings(request):
    settings, created= SiteSetting.objects.get_or_create(pk=1)

    if request.method=='POST':
        form=SiteSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated successfully!")
            return redirect('admin_settings')
    else:
        form=SiteSettingForm(instance=settings)

    context={
        'form':form,
        'current_page':'admin_settings',

    }
    return render(request, 'admin_settings.html', context)

@login_required
def reports_dashboard_view(request):
    total_companies=Company.objects.count()
    total_active_companies=Company.objects.filter(is_active=True).count()
    total_approved_companies=Company.objects.filter(is_approved=True).count()

    total_jobs=Job.objects.count()
    total_active_jobs=Job.objects.filter(is_active=True).count()
    total_pending_jobs=Job.objects.filter(status='pending').count()

    total_job_seekers=JobSeeker.objects.count()
    total_active_job_seekers=JobSeeker.objects.filter(is_active=True).count()

    total_applications=Application.objects.count()
    total_pending_applications=Application.objects.filter(status='pending').count()

    context={
        'total_companies':total_companies,
        'total_active_companies':total_active_companies,
        'total_approved_companies':total_approved_companies,
        'total_jobs':total_jobs,
        'total_active_jobs':total_active_jobs,
        'total_pending_jobs':total_pending_jobs,
        'total_job_seekers':total_job_seekers,
        'total_active_job_seekers':total_active_job_seekers,
        'total_applications':total_applications,
        'total_pending_applications':total_pending_applications,
        'current_page':'reports',
    }
    return render(request, 'reports_dashboard.html', context)

@login_required
def reports_dashboard_view(request):
    #company metrics
    total_companies=Company.objects.count()
    total_active_companies=Company.objects.filter(is_active=True).count()
    total_approved_companies=Company.objects.filter(is_approved=True).count()

    #Job Metrics
    total_jobs=Job.objects.count()
    total_active_jobs=Job.objects.filter(is_active=True, status='active').count()
    total_pending_jobs=Job.objects.filter(status='pending').count()
    total_closed_jobs=Job.objects.filter(status='closed').count()

    #Job seeker metrics
    total_job_seekers=JobSeeker.objects.count()
    total_active_job_seekers=JobSeeker.objects.filter(is_active=True).count()

    #Application metrics
    total_applications=Application.objects.count()
    total_pending_applications=Application.objects.filter(status='pending').count()
    total_reviewed_applications=Application.objects.filter(status='reviewed').count()
    total_hired_applications=Application.objects.filter(status='hired').count()

    context = {
        'total_companies': total_companies,
        'total_active_companies': total_active_companies,
        'total_approved_companies': total_approved_companies,
        'total_jobs': total_jobs,
        'total_active_jobs': total_active_jobs,
        'total_pending_jobs': total_pending_jobs,
        'total_closed_jobs': total_closed_jobs,
        'total_job_seekers': total_job_seekers,
        'total_active_job_seekers': total_active_job_seekers,
        'total_applications': total_applications,
        'total_pending_applications': total_pending_applications,
        'total_reviewed_applications': total_reviewed_applications,
        'total_hired_applications': total_hired_applications,
        'current_page': 'reports',
    }
    return render(request, 'reports_dashboard.html', context)

@login_required
def feedback_list(request):
    feedback_entries=Feedback.objects.all().order_by('-created_at')

    context={
        'feedback_entries':feedback_entries,
        'current_page':'feedback_complaints',
    }
    return render(request, 'feedback_list.html', context)

@login_required
def feedback_detail(request,pk):
    feedback=get_object_or_404(Feedback, pk=pk)

    #atomatically mark as read when the admin views it
    if not feedback.is_read:
        feedback.is_read=True
        feedback.save()

    context={
        'feedback':feedback,
        'current_page':'feedback_complaints',
    }
    return render(request, 'feedback_detail.html', context)

@login_required
def feedback_delete(request,pk):
    feedback=get_object_or_404(Feedback,pk=pk)

    if request.methos=='POST':
        feedback.delete()
        messages.success(request, "The feedback entry has been deleted successfully.")
        return redirect('feedback_list')
    
    context={
        'feedback':feedback,
        'current_page':'feedback_complaints',
    }
    return render(request, 'feedback_confirm_delete.html', context)


@login_required
def send_notification_view(request):
    if request.method=='POST':
        form=NotificationForm(request.POST)
        if form.is_valid():
            notification=form.save(commit=False)
            notification.sender=request.user
            notification.save()
            messages.success(request, "Notification sent successfully!")
            return redirect('send_notification')
    else:
        form=NotificationForm()

    context={
        'form':form,
        'current_page':'notifications_messaging',
    }
    return render(request,'send_notification.html', context)







        

