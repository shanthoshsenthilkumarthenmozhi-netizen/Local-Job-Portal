from django.urls import path
from users import views


urlpatterns=[
    path('signup/', views.jobseeker_signup, name='jobseeker_signup'),
    
]