from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from admin_dashboard.models import JobSeeker

class JobSeekerSignUpForm(UserCreationForm):
    first_name=forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    email=forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    profile_picture=forms.FileField(required=False, widget=forms.FileInput(attrs={'class':'form-control'}))
    resume=forms.FileField(required=False, widget=forms.FileInput(attrs={'class':'form-control'}))
    skills=forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'e.g. Python, Django, Java'}))
    bio=forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control', 'rows':3}))

    class Meta(UserCreationForm.Meta):
        model=User
        fields=UserCreationForm.Meta.fields + ('first_name','last_name','email')

    def save(self, commit=True):
        user=super().save(commit=False)
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
            job_seeker=JobSeeker.objects.create(
                user=user,
                profile_picture=self.cleaned_data['profirl_picture'],
                resume=self.cleaned_data['resume'],
                skills=self.cleaned_data['skills'],
                bio=self.cleaned_data['bio']
            )
        return user



