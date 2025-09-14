from django.shortcuts import render, redirect
from django.contrib import messages
from admin_dashboard.models import JobSeeker, Job, JobApplication
from django.contrib.auth.hashers import make_password, check_password

def register_jobseeker(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")

        jobseeker = JobSeeker.objects.create(
            name=name,
            email=email,
            phone=phone,
            username=username,
            password=make_password(password),  # secure hash
        )

        # store in session
        request.session["jobseeker_id"] = jobseeker.id
        request.session["jobseeker_username"] = jobseeker.username
        request.session["jobseeker_name"] = jobseeker.name

        messages.success(request, f"Registration successful! Welcome {jobseeker.name} 🎉")
        return redirect("jobseeker_dashboard")

    return render(request, "register.html")


def login_jobseeker(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            jobseeker = JobSeeker.objects.get(username=username)
            if check_password(password, jobseeker.password):
                request.session["jobseeker_id"] = jobseeker.id
                
                request.session["jobseeker_name"] = jobseeker.name
                messages.success(request, f"Welcome back, {jobseeker.name}!")
                return redirect("jobseeker_dashboard")
            else:
                messages.error(request, "Invalid username or password")
        except JobSeeker.DoesNotExist:
            messages.error(request, "Invalid username or password")

        return redirect("login_jobseeker")

    return render(request, "login.html")


def logout_jobseeker(request):
    request.session.flush()
    return redirect("home")


def jobseeker_dashboard(request):
    if "jobseeker_id" not in request.session:
        return redirect("login_jobseeker")

    jobseeker_name = request.session.get("jobseeker_name", "Guest")
    jobs = Job.objects.all()
    return render(request, "dashboard.html", {"jobs": jobs, "jobseeker_name": jobseeker_name})


def apply_job(request, job_id):
    if "jobseeker_id" not in request.session:
        return redirect("login_jobseeker")

    jobseeker = JobSeeker.objects.get(id=request.session["jobseeker_id"])
    job = Job.objects.get(id=job_id)

    # prevent duplicate applications
    if not JobApplication.objects.filter(jobseeker=jobseeker, job=job).exists():
        JobApplication.objects.create(jobseeker=jobseeker, job=job)

    messages.success(request, "You have successfully applied for this job!")
    return redirect("jobseeker_dashboard")
