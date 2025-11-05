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

# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from admin_dashboard.models import JobSeeker
from django.contrib.auth.hashers import make_password

def profile_jobseeker(request):
    if "jobseeker_id" not in request.session:
        return redirect("login_jobseeker")

    jobseeker = JobSeeker.objects.get(id=request.session["jobseeker_id"])

    if request.method == "POST":
        # Basic details
        jobseeker.name = request.POST.get("name")
        jobseeker.email = request.POST.get("email")
        jobseeker.phone = request.POST.get("phone")
        jobseeker.dob = request.POST.get("dob") or None
        jobseeker.gender = request.POST.get("gender")
        jobseeker.address = request.POST.get("address")

        # Professional details
        jobseeker.education = request.POST.get("education")
        jobseeker.experience = request.POST.get("experience") or 0
        jobseeker.skills = request.POST.get("skills")
        jobseeker.linkedin = request.POST.get("linkedin")
        jobseeker.github = request.POST.get("github")
        jobseeker.expected_salary = request.POST.get("expected_salary") or None
        jobseeker.availability = request.POST.get("availability")

        # File uploads
        if "profile_pic" in request.FILES:
            jobseeker.profile_pic = request.FILES["profile_pic"]

        if "resume" in request.FILES:
            jobseeker.resume = request.FILES["resume"]

        # Change password (optional)
        password = request.POST.get("password")
        if password:
            jobseeker.password = make_password(password)

        jobseeker.save()
        messages.success(request, "Profile updated successfully ✅")
        return redirect("profile_jobseeker")

    return render(request, "profile.html", {"jobseeker": jobseeker})

def view_applications(request):
    if "jobseeker_id" not in request.session:
        return redirect("login_jobseeker")

    jobseeker = JobSeeker.objects.get(id=request.session["jobseeker_id"])
    applications = JobApplication.objects.filter(jobseeker=jobseeker).select_related("job")

    return render(request, "view_applications.html", {
        "applications": applications,
        "jobseeker_name": jobseeker.name,
    })

def browse_jobs(request):
    jobs = Job.objects.filter(is_active=True).order_by("-posted_at")
    return render(request, "browse_jobs.html", {"jobs": jobs})

