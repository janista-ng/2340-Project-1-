from django.urls import path
from . import views

app_name = 'jobs' 

urlpatterns = [
    path('', views.job_list, name='job_list'),              
    path('post/', views.job_create, name='job_create'),      
    path('<int:pk>/', views.job_detail, name='job_detail'), 
    path('<int:pk>/apply/', views.apply_to_job, name='job_apply'),  
    path('<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('applications/', views.my_applications, name='my_applications'),
    path('<int:pk>/applications/', views.job_applications, name='job_applications'),
    path('applications/<int:app_id>/status/', views.update_application_status, name='update_application_status'),
]
