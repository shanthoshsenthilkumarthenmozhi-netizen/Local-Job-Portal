from django.urls import path
from admin_dashboard import views

urlpatterns= [
    path('admin_login/',views.admin_login_view,name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-logout',views.logout_view, name='logout'),

    #Post job section URLs
    path('post-job-selection/', views.post_job_selection_view, name='post_job_selection'),
    path('register-company/', views.register_company_view, name='register_company'),
    path('company-login', views.company_login_view, name='company_login'),
    path('post-job-form/<int:company_id>/', views.post_job_form_view, name='post_job_form',),

    #Manage Companies URLs
    path('companies/',views.company_list, name='company_list'),
    path('companies/create',views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/',views.company_update, name='company_update'),
    path('companies/<int:pk>/delete/',views.company_delete, name='company_delete'),
    path('companies/<int:pk>/toggle-status/',views.company_toggle_status, name='company_toggle_status'),

    #Job management URLs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_update, name='job_update'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:pk>/toggle-status/', views.toggle_job_status, name='job_toggle_status'),

    #Job seeker management URLs
    path('job-seekers/',views.job_seeker_list, name='job_seeker_list'),
    path('job-seekers/<int:pk>/toggle-status/', views.job_seeker_toggle_status, name='job_seeker_toggle_status'),
    path('job-seekers/<int:pk>/', views.job_seeker_detail, name='job_seeker_detail'),
    path('job-seekers/<int:pk>/delete/',views.job_seeker_delete, name='job_seeker_detail'),

    #Application Management URLs
    path('applications/',views.application_list, name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/update-status/', views.application_update_status, name='application_update_status'),
    path('application/<int:pk>/delete/', views.application_delete, name='application_delete'),

    #Admin Settings
    path('settings/', views.admin_settings, name='admin_settings'),

    #Reports URL
    path('reports/', views.reports_dashboard_view, name='reports_dashboard'),

    #Feedback
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:pk>/delete/', views.feedback_delete, name='feedback_delete'),

    #notification
    path('send-notification/', views.send_notification_view, name='send_notification'),
]