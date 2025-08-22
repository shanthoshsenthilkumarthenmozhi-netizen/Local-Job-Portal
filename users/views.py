from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from users.forms import JobSeekerSignUpForm

# Create your views here.

def jobseeker_signup(request):
    if request.method=='POST':
        form=JobSeekerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,'Account created successfully!')
            return redirect('jobseeker_dashboard')
    else:
        form=JobSeekerSignUpForm()

    return render(request, 'registration/jobseeker_signup.html',{'form':form})

