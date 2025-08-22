from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# class CustomUser(AbstractUser):
#Models for category
class Category(models.Model):
    name=models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    icon_class=models.CharField(max_length=50, blank=True, null=True, verbose_name="Icon Class(Font Awesome)")
    job_count=models.IntegerField(default=0, verbose_name="Number of Jobs")

    class Meta:
        verbose_name_plural="Categories"
        ordering=['name']

    def __str__(self):
        return self.name

#models for companies  
class Company(models.Model):
    # This is the crucial link to the User model for authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile', verbose_name="User Account")
    
    # Renamed 'name' to 'company_name' for consistency with forms
    company_name = models.CharField(max_length=255, unique=True, verbose_name="Company Name")
    
    # Renamed 'phone' to 'phone_number' for consistency with forms
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    
    website = models.URLField(blank=True, null=True, verbose_name="Website URL")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    description = models.TextField(blank=True, null=True, verbose_name="Company Description")
    logo = models.FileField(upload_to='company_logos/', blank=True, null=True, verbose_name="Company Logo")
    
    # Added missing fields expected by forms
    company_size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Company Size")
    industry = models.CharField(max_length=100, blank=True, null=True, verbose_name="Industry")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Company Location") 

    #New social media fields
    linkedin_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="LinkedIn URL")
    twitter_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Twitter URL")
    facebook_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Facebook URL")


    is_active=models.BooleanField(default=True, verbose_name="Is Active")
    is_approved=models.BooleanField(default=False, verbose_name="Is Approved by Admin")
    created_at=models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at=models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name_plural="Companies"
        ordering=['company_name'] # Order by company_name

    def __str__(self):
        return self.company_name
    
#models for job seekers/users
class JobSeeker(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile',verbose_name="User Account")
    phone=models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone NUmber")
    resume=models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name="Resume File")
    skills=models.TextField(blank=True, null=True, verbose_name="Skills (comma-separated)")
    experience=models.TextField(blank=True, null=True, verbose_name="Experience Details")
    is_active=models.BooleanField(default=True, verbose_name="Is Active")
    created_at=models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at=models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name_plural= "Job Seekers"
        ordering=['user__first_name','user__last_name'] #Order by user's name

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"
    
#model for job posting
class Job(models.Model):
    JOB_TYPE=[
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('FL', 'Freelance'),
        ('CT', 'Contract'),
        ('IN', 'Internship'),
    ]
    STATUS_CHOICES=[
        ('active', 'Active'),
        ('inactive','Inactive'),
        ('pending', "Pending Approval"),
        ('closed', 'Closed'),
    ]

    company=models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name="Company")
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs', verbose_name="Category")
    title=models.CharField(max_length=255, verbose_name="Job Title/Designation")
    vacancy=models.IntegerField(default=1, verbose_name="Number of Vacancies")
    description=models.TextField(verbose_name="Job Description")
    location=models.CharField(max_length=100, verbose_name="Job Location")
    salary=models.CharField(max_length=100, blank=True, null=True, verbose_name="Salary")
    job_type=models.CharField(max_length=2, choices=JOB_TYPE, default='FT', verbose_name="Job Type")
    requirements=models.TextField(blank=True, null=True, verbose_name="Job Requirements")
    responsibilities=models.TextField(blank=True, null=True, verbose_name="Job Responsibilities")
    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Job Status")
    is_featured=models.BooleanField(default=False, verbose_name="Is Featured Job")
    posted_at=models.DateTimeField(auto_now_add=True, verbose_name="Posted At")
    updated_at=models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    is_active=models.BooleanField(default=True, verbose_name="Is Active")
    class Meta:
        verbose_name_plural="Jobs"
        ordering=['-posted_at'] #order by most recent jobs first

    def __str__(self):
        return f"{self.title} at {self.company.company_name}" 
    
#models for job applications
class Application(models.Model):
    job=models.ForeignKey(Job, on_delete=models.CASCADE, related_name='application', verbose_name="Job Applied For")
    job_seeker=models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications', verbose_name="Applicant")

    #status of the applocation
    APPLICATION_STATUS_CHOICES=[
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview Scheduled'),
        ('hired', 'Hired'),
        ('rejected','Rejected'),
    ]
    status=models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending', verbose_name="Application Status")
    applied_at=models.DateTimeField(auto_now_add=True, verbose_name="Applied At")
    updated_at=models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name_plural="Application"
        unique_together=('job','job_seeker') #job seeker can only apply once per job
        ordering=['-applied_at'] #order by most recent applications

    def __str__(self):
        return f"Application for {self.job.title} by {self.job_seeker.user.username}"
    
# admin settings
class SiteSetting(models.Model):
    #Website Config
    site_name = models.CharField(max_length=255, default="LocalTalentz")
    site_tagline=models.CharField(max_length=255, blank=True, null=True)
    logo=models.FileField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Contact Email") # ADDED
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number") # ADDED
    
    #Job Board Settings
    max_jobs_per_company=models.IntegerField(default=10)
    auto_approve_jobs=models.BooleanField(default=False)
    job_expiry_days=models.IntegerField(default=30)

    #Social Media
    facebook_url=models.URLField(blank=True, null=True)
    twitter_url=models.URLField(blank=True, null=True)
    linkedin_url=models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True) # Ensure this is also present if used in admin.py

    #SEO
    meta_description=models.TextField(blank=True, null=True)
    meta_keywords=models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name="Site Settings"
        verbose_name_plural="Site Settings"

    def __str__(self):
        return "Site Settings"
    
    def save(self,*args, **kwargs):
        if SiteSetting.objects.count()>0 and self.pk is None:
            return
        super(SiteSetting, self).save(*args, **kwargs)

class Feedback(models.Model):
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subject=models.CharField(max_length=255)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural="Feedback & Complaints"
        ordering=['-created_at']

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'}"
    

#Notification models
class Notification(models.Model):
    recipient=models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Notifications"
        ordering=['-created_at']

    def __str__(self):
        # Corrected to safely access sender username
        return f"Message for {self.recipient.username} from {self.sender.username if self.sender else 'System'}"
