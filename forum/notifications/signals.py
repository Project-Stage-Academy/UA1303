from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import NotificationCategory
from profiles.models import InvestorProfile, StartupProfile
from .serializers import StartUpNotificationCreateSerializer
from projects.models import Project
import logging

logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            investor = InvestorProfile.objects.get(pk=pk)
            notification_category = NotificationCategory.objects.get(name='follow')
            data = {
                'notification_category': notification_category.id,
                'investor': investor.id,
                'startup': instance.id,
            }
            serializer = StartUpNotificationCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Notification created for startup.")
            else:
                logger.error(f"Failed to create notification: {serializer.errors}")

#notify investors when a startup updates their profile
@receiver(post_save, sender=StartupProfile)
def notify_startup_update(sender, instance, created, **kwargs):
    followers = instance.followers.all()
    notification_category, _ = NotificationCategory.objects.get_or_create(name='profile_update')
    for investor in followers:
        data = {
            'notification_category': notification_category.id,
            'investor': investor.id,
            'startup': instance.id,
        }
        serializer = StartUpNotificationCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Notification created for investor {investor.id}.")
        else:
            logger.error(f"Failed to create notification: {serializer.errors}")

#notify investors when a startup launches a new project
@receiver(post_save, sender=Project)
def notify_investors_about_new_project(sender, instance, created, **kwargs):
    # Only notify when a new project is created
    if not created:
        return
    followers = instance.startup.followers.all()
    notification_category, _ = NotificationCategory.objects.get_or_create(name='new_project')
    for investor in followers:
        data = {
            'notification_category': notification_category.id,
            'investor': investor.id,
            'startup': instance.startup.id,
        }
        serializer = StartUpNotificationCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Notification about new project created for investor {investor.id}.")
        else:
            logger.error(f"Failed to create notification: {serializer.errors}")