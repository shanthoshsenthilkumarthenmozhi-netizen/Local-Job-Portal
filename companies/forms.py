from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from admin_dashboard.models import Company, Job, Category  # Ensure this import is correct
from django.core.exceptions import ValidationError

class CompanySignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    company_size = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Size (e.g., 1-10, 11-50)'}))
    logo = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    industry = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry (e.g., Tech, Finance)'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Company Description'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL (Optional)'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Optional)'}))
    location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Location'})) # ADDED LOCATION FIELD

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',) # 'email' is part of User model

    def save(self, commit=True):
        _cleaned_data = self.cleaned_data 
        print(f"DEBUG:CompanySignupForm cleaned_data: {_cleaned_data}")

        # Call the parent's save method to create the User object
        user = super().save(commit=False)
        
        # Set email on the user object (it's a field on the User model)
        user.email = _cleaned_data['email'] # Ensure email is set on the User model
        print(f"DEBUG: User object before save: Username={user.username}, Email={user.email}")
        
        # Save the User object first if commit is True
        if commit:
            user.save() 
            print(f"DEBUG: User object saved:ID={user.id}, Username={user.username}, Email={user.email}")

            # Create the Company profile instance linked to this user
            company = Company(
                company_name=_cleaned_data['company_name'],
                user=user, # Pass the created User instance here
                 
                # company_size=_cleaned_data.get('company_size'), 
                logo=_cleaned_data.get('logo'), 
                industry=_cleaned_data.get('industry'), 
                description=_cleaned_data.get('description'),
                website=_cleaned_data.get('website'),
                phone_number=_cleaned_data.get('phone_number'),
                location=_cleaned_data.get('location') # SAVE LOCATION HERE
            )
            print(f"DEBUG: Company object before save: Name={company.company_name}, Location={company.location}, User ID={company.user.id}")
            company.save() # Save the company instance to the database
            print(f"DEBUG:Company object saved: ID={company.id}, Name={company.company_name}")
        return user
    

class JobPostForm(forms.ModelForm):
    #Fields for the dropdown menu of job categories
    category=forms.ModelChoiceField(queryset=Category.objects.all(),empty_label="Select a category", 
    widget=forms.Select(attrs={'class':'form-select'})
    )

    class Meta:
        model=Job
        fields=[
            'title','description','vacancy','location','salary','job_type','category','requirements','responsibilities',
        ]

        widgets={
            'title':forms.TextInput(attrs={'class':'form-control','placeholder':'e.g., Senior Software Engineer'}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':5, 'placeholder':'Provide a detailed description of the role...'}),
            'vacancy':forms.NumberInput(attrs={'class':'form-control','placeholder':'1'}),
            'location':forms.TextInput(attrs={'class':'form-control','placeholder':'e.g.Old bus stand,Tiruppur'}),
            'salary':forms.TextInput(attrs={'class':'fomr-control','placeholder':'e.g., ₹5,00,000 - ₹7,00,000 per annum'}),
            'job_type':forms.Select(attrs={'class':'form-select'}),
            'requirements':forms.Textarea(attrs={'class':'form-control','rows':3, 'placeholder':'e.g., 1+ years of experience in python...'}),
            'responsibilities':forms.Textarea(attrs={'class':'form-control','rows':3, 'placeholder':'e.g., Develop and maintain web applications...'}),
            'is_featured':forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
        labels={
            'title':'Job Title/Designation',
            'description':'Job Description',
            'vacancy':'Number of Vacancies',
            'location':'Job Location',
            'salary':'Salary (In Rupees)',
            'job_type':'Job Type',
            'category':'Job Category',
            'requirements':'Job Requirements',
            'responsibilities':'Job Responsibilities',
            'is_featured':'Featured this job?',
        }

#Detailed company profile form
class CompanyProfileForm(forms.ModelForm):
    # Set fields to not be required
    company_name = forms.CharField(max_length=255, required=False)
    logo = forms.FileField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))
    industry = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=255, required=False)
    website = forms.URLField(required=False)
    linkedin_url = forms.URLField(required=False)
    twitter_url = forms.URLField(required=False)
    facebook_url = forms.URLField(required=False)

    class Meta:
        model = Company
        fields = ['company_name', 'logo', 'phone_number', 'description', 'industry', 'address', 'website', 'linkedin_url', 'twitter_url', 'facebook_url']
    
#Form for updating the user's email address
class UpdateEmailForm(forms.ModelForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields =['email']

    def clean_email(self):
        email=self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another user.")
        return email
    
#Form for changing a user's password
class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class']='form-control'
