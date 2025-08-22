from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Login, Logout, Dashboard
    path('signup/', views.company_signup, name='company_signup'),
    path('login/', views.company_login, name='company_login'),
    path('logout/', views.company_logout_view, name='company_logout'),
    path('dashboard/', views.company_dashboard, name='company_dashboard'),

    # Job Management
    path('post-job/', views.post_job, name='post_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('manage-candidates/', views.manage_candidates, name='manage_candidates'),

    #profile Settings and related actions
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('update_email/', views.update_email, name='update_email'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify_otp/',views.verify_otp, name='verify_otp'),
    path('change_password/',views.change_password, name='change_password'),
    
    #Jon actions
    path('job/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job/edit/<int:job_id>/',views.edit_job, name='edit_job'),
    path('manage_applicants/<int:job_id>/', views.manage_applicants, name='manage_applicants'),
    # path('view_application/<int:application_id>/', views.view_application, name='view_application'),
    path('job/toggle-status/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),
]
