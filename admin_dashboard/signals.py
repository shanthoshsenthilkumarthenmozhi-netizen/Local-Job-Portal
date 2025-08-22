from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from admin_dashboard.models import Job, Category

def update_category_job_count(category):
    if category:
        category.job_count=category.jobs.filter(status='active').count()
        category.save(update_fields=['job_count'])

@receiver(post_save, sender=Job)
def job_post_save_handler(sender, instance,created, **kwargs):
    update_category_job_count(instance.category)

    if not created:
        try:
            old_category=sender.objects.get(pk=instance.pk).category

            if old_category and old_category != instance.category:
                update_category_job_count(old_category)
        except sender.DoesNotExist:
            pass

@receiver(post_delete, sender=Job)
def job_post_delete_handler(sender, instance, **kwargs):
    update_category_job_count(instance.category)
