from django.contrib import admin
from .models import Category, Company, JobSeeker, Job, Application, SiteSetting, Feedback, Notification

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Corrected list_display to only use fields from the Category model
    list_display = ('name', 'job_count', 'icon_class')
    search_fields = ('name',)
    # Removed list_filter as Category model doesn't have is_active, is_approved, created_at
    # If you need filtering for Category, it would be based on its own fields like 'name'

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # This list_display must EXACTLY match the fields/methods you want to show
    list_display = (
        'company_name',     # Direct field on Company model
        'get_username',     # Custom method to get username from linked User
        'get_email',        # Custom method to get email from linked User
        'phone_number',     # Direct field on Company model
        'location',         # Direct field on Company model
        'is_active',
        'is_approved',
        'created_at'
    )
    list_filter = ('is_active', 'is_approved', 'created_at')
    search_fields = ('company_name', 'phone_number', 'description', 'location', 'user__username', 'user__email')
    actions = ['approve_companies', 'deactivate_companies']

    # Custom method to retrieve username from the associated User object
    def get_username(self, obj):
        # Safely check if 'user' attribute exists and is not None
        return obj.user.username if hasattr(obj, 'user') and obj.user else 'N/A'
    get_username.short_description = 'Username' # This sets the column header in the admin

    # Custom method to retrieve email from the associated User object
    def get_email(self, obj):
        # Safely check if 'user' attribute exists and is not None
        return obj.user.email if hasattr(obj, 'user') and obj.user else 'N/A'
    get_email.short_description = 'Email' # This sets the column header in the admin

    # Custom actions
    def approve_companies(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected companies have been approved.")
    approve_companies.short_description = "Approve selected companies"

    def deactivate_companies(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected companies have been deactivated.")
    deactivate_companies.short_description = "Deactivate selected companies"

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_username', 'get_email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'phone', 'skills')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'location', 'job_type', 'status', 'is_featured', 'posted_at')
    list_filter = ('status', 'job_type', 'is_featured', 'category', 'company')
    search_fields = ('title', 'description', 'location', 'company__company_name')
    date_hierarchy = 'posted_at'
    actions = ['mark_as_active', 'mark_as_inactive', 'mark_as_featured', 'mark_as_not_featured']

    def mark_as_active(self, request, queryset):
        queryset.update(status='active', is_active=True)
        self.message_user(request, "Selected jobs marked as active.")
    mark_as_active.short_description = "Mark selected jobs as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive', is_active=False)
        self.message_user(request, "Selected jobs marked as inactive.")
    mark_as_inactive.short_description = "Mark selected jobs as inactive"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, "Selected jobs marked as featured.")
    mark_as_featured.short_description = "Mark selected jobs as featured"

    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, "Selected jobs marked as not featured.")
    mark_as_not_featured.short_description = "Mark selected jobs as not featured"

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'job_seeker', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'job_seeker__user__username')
    date_hierarchy = 'applied_at'
    actions = ['mark_pending', 'mark_reviewed', 'mark_interview', 'mark_hired', 'mark_rejected']

    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, "Selected applications marked as pending.")
    mark_pending.short_description = "Mark as Pending"

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
        self.message_user(request, "Selected applications marked as reviewed.")
    mark_reviewed.short_description = "Mark as Reviewed"

    def mark_interview(self, request, queryset):
        queryset.update(status='interview')
        self.message_user(request, "Selected applications marked as interview scheduled.")
    mark_interview.short_description = "Mark as Interview Scheduled"

    def mark_hired(self, request, queryset):
        queryset.update(status='hired')
        self.message_user(request, "Selected applications marked as hired.")
    mark_hired.short_description = "Mark as Hired"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected applications marked as rejected.")
    mark_rejected.short_description = "Mark as Rejected"

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'phone_number', 'max_jobs_per_company', 'auto_approve_jobs')
    fieldsets = (
        ('Website Configuration', {
            'fields': ('site_name', 'site_tagline', 'logo', 'contact_email', 'phone_number')
        }),
        ('Job Board Settings', {
            'fields': ('max_jobs_per_company', 'auto_approve_jobs', 'job_expiry_days')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
        ('SEO & Meta Tags', {
            'fields': ('meta_description', 'meta_keywords')
        }),
    )

    def has_add_permission(self, request):
        return SiteSetting.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'get_username', 'get_email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'message', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    def get_username(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    get_username.short_description = 'Submitted By (Username)'

    def get_email(self, obj):
        return obj.user.email if obj.user else 'N/A'
    get_email.short_description = 'Submitted By (Email)'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected feedback marked as read.")
    mark_as_read.short_description = "Mark selected feedback as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Selected feedback marked as unread.")
    mark_as_unread.short_description = "Mark selected feedback as unread"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'recipient', 'sender')
    search_fields = ('recipient__username', 'sender__username', 'message')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Selected notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
