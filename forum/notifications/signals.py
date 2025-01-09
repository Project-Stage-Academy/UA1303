from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StartupProfile, NotificationForUpdates, Project

@receiver(post_save, sender=StartupProfile)
def create_notification_on_startup_profile_update(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return  # Only triggers on updates
    NotificationForUpdates.objects.create(
        user=instance.user, 
        startup_profile=instance,
        message=f"{instance.company_name} has updated their profile."
    )

@receiver(post_save, sender=Project)
def create_notification_on_new_project(sender, instance, **kwargs):
    if kwargs.get('created', False):  # Only triggers on creation
        NotificationForUpdates.objects.create(
            user=instance.startup.user,  
            project=instance,
            message=f"{instance.startup.company_name} has posted a new project: {instance.title}."
        )