from django.shortcuts import render
from admin_dashboard.models import Category, Job

# Create your views here.


def index(request):
    categories=Category.objects.filter(jobs__status='active').distinct().order_by('name')

    recent_jobs=Job.objects.filter(status='active').order_by('-posted_at')[:5]

    context={
        'categories':categories,
        'recent_jobs':recent_jobs,
    }
    return render(request, 'index.html',context)