from django import forms
from admin_dashboard.models import Company, Job, Category, SiteSetting, Notification, Application, Feedback # Ensure all necessary models are imported
from django.contrib.auth.models import User # Needed for NotificationForm recipient queryset

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name', 'phone_number', 'website', 'address', 
            'description', 'logo', 'company_size', 'industry', 'location', 
            'is_active', 'is_approved'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_size': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}), 
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__' 
        widgets = {
            'company': forms.Select(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Job Title/Designation'}),
            'vacancy': forms.NumberInput(attrs={'class':'form-control', 'min':'1','placeholder':'Number of open positions'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'rows':6, 'placeholder':'Detailed job description...'}),
            'location': forms.TextInput(attrs={'class':'form-control','placeholder':'Job location'}),
            'salary': forms.TextInput(attrs={'class':'form-control', 'placeholder':'e.g., ₹2,00,000 - ₹4,00,000 or Negotiable'}),
            'job_type': forms.Select(attrs={'class':'form-control'}),
            'requirements': forms.Textarea(attrs={'class':'form-control', 'rows':4, 'placeholder':'Key requirements for the role...'}),
            'responsibilities': forms.Textarea(attrs={'class':'form-control', 'rows':4, 'placeholder':'Main responsibilities...'}),
            'status': forms.Select(attrs={'class':'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

class NotificationForm(forms.ModelForm):
    recipient=forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Recipient",
        required=True,
        widget=forms.Select(attrs={'class':'form-select'})
    )
    message=forms.CharField(
        widget=forms.Textarea(attrs={'class':'form-control','rows':5}),
        label="Message",
        required=True
    )
    class Meta:
        model=Notification
        fields=['recipient', 'message'] 
        
class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = '__all__' 
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'max_jobs_per_company': forms.NumberInput(attrs={'class': 'form-control', 'min':'1'}),
            'auto_approve_jobs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_expiry_days': forms.NumberInput(attrs={'class': 'form-control', 'min':'1'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'job': forms.Select(attrs={'class':'form-control'}),
            'job_seeker': forms.Select(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Category Name'}),
            'icon_class': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Font Awesome Icon Class (e.g., fa-briefcase)'}),
            'job_count': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class':'form-control'}),
            'subject': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Subject'}),
            'message': forms.Textarea(attrs={'class':'form-control', 'rows':5, 'placeholder':'Your feedback or complaint...'}),
            'is_read': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
