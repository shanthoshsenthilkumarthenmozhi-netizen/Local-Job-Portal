from django.urls import path
from . import views



urlpatterns = [
    path("register/", views.register_jobseeker, name="register_jobseeker"),
    path("login/", views.login_jobseeker, name="login_jobseeker"),
    path("logout/", views.logout_jobseeker, name="logout_jobseeker"),
    path("dashboard/", views.jobseeker_dashboard, name="jobseeker_dashboard"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("profile/", views.profile_jobseeker, name="profile_jobseeker"),
    path("applications/", views.view_applications, name="view_applications"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("browse-jobs/", views.browse_jobs, name="browse_jobs"),
    path("logout/", views.logout_jobseeker, name="logout_jobseeker"),

]
