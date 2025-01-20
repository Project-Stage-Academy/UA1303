from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import NotificationCategory, NotificationPreference
from profiles.models import InvestorProfile, StartupProfile
from .serializers import (
    StartUpNotificationCreateSerializer,
    InvestorNotificationCreateSerializer
)
from projects.models import Project
import logging

logger = logging.getLogger(__name__)

def have_preference(notification_receiver, notification_category):
    startup_preference = NotificationPreference.objects.get(user=notification_receiver.user)
    if notification_category not in startup_preference.allowed_notification_categories.all():
        logger.info(f"Startup {notification_receiver.id} does not have a preference for "
                    f"the '{notification_category.name}' category. Skipping notification creation.")
        return False
    return True

@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    try:
        if action == 'post_add' and reverse:
            for pk in pk_set:
                investor = InvestorProfile.objects.get(pk=pk)
                notification_category = NotificationCategory.objects.get(name='follow')
                
                if have_preference(instance, notification_category):
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
    except Exception as e:
        logger.error(f"Unexpected error occurs during StartUp notification creation: {e}")

#notify investors when a startup updates their profile
@receiver(post_save, sender=StartupProfile)
def notify_startup_update(sender, instance, created, **kwargs):
    followers = instance.followers.all()
    notification_category = NotificationCategory.objects.get(name='profile_update')
    for investor in followers:
        if have_preference(investor, notification_category):
            data = {
                'notification_category': notification_category.id,
                'investor': investor.id,
                'startup': instance.id,
            }
            serializer = InvestorNotificationCreateSerializer(data=data)
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
    notification_category = NotificationCategory.objects.get(name='new_project')
    for investor in followers:
        if have_preference(investor, notification_category):
            data = {
                'notification_category': notification_category.id,
                'investor': investor.id,
                'startup': instance.startup.id,
            }
            serializer = InvestorNotificationCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Notification about new project created for investor {investor.id}.")
            else:
                logger.error(f"Failed to create notification: {serializer.errors}")
                