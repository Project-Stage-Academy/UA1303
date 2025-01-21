from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import NotificationCategory, NotificationPreference, NotificationMethod
from profiles.models import InvestorProfile, StartupProfile
from .serializers import (
    StartUpNotificationCreateSerializer,
    InvestorNotificationCreateSerializer
)
from projects.models import Project
import logging


logger = logging.getLogger(__name__)

NOTIFICATION_CATEGORIES = {
    'follow': None,
    'profile_update': None,
    'new_project': None
}

NOTIFICATION_METHODS = {
    'in_app': None,
    'email': None
}

def initialize_notification_categories_and_methods():
    """Initialize notification categories and methods once at startup"""
    for name in NOTIFICATION_CATEGORIES.keys():
        NOTIFICATION_CATEGORIES[name] = NotificationCategory.objects.get(name=name)
    for name in NOTIFICATION_METHODS.keys():
        NOTIFICATION_METHODS[name] = NotificationMethod.objects.get(name=name)

initialize_notification_categories_and_methods()


def have_preference(notification_receiver, notification_category):
    """
    Check if a user has enabled notifications for a specific category.
    
    Args:
        notification_receiver: Profile instance (InvestorProfile or StartupProfile)
        notification_category: NotificationCategory instance
        
    Returns:
        bool: True if user has enabled this notification type, False otherwise
    """
    try:
        profile_preference = NotificationPreference.objects.get(user=notification_receiver.user)
        
        if NOTIFICATION_METHODS['in_app'] not in profile_preference.allowed_notification_methods.all():
            logger.info(f"Profile {notification_receiver.id} does not have a preference for "
                       f"the '{NOTIFICATION_METHODS['in_app'].name}' method. Skipping notification creation.")
            return False
        
        if notification_category not in profile_preference.allowed_notification_categories.all():
            logger.info(f"Profile {notification_receiver.id} does not have a preference for "
                       f"the '{notification_category.name}' category. Skipping notification creation.")
            return False
        return True
    except NotificationPreference.DoesNotExist:
        logger.info(f"No notification preferences found for user {notification_receiver.user.id}. "
                   f"Skipping notification creation.")
        return False


def create_notification(notification_receiver, notification_category, data, serializer_class):
    """
    Create a notification after validating user preferences and data.
    
    Args:
        notification_receiver: Profile instance receiving the notification
        notification_category: NotificationCategory instance
        data: Dictionary containing notification data
        serializer_class: Serializer class to use for validation and creation
    """
    if not have_preference(notification_receiver, notification_category):
        return False
    
    serializer = serializer_class(data=data)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Notification created for {notification_receiver.__class__.__name__} {notification_receiver.id}.")
    else:
        logger.error(f"Failed to create notification: {serializer.errors}")


@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Signal handler for when an investor follows a startup.
    Creates a notification for the startup when they gain a new follower.
    
    Triggered by:
    - Changes to the StartupProfile.followers many-to-many relationship
    """
    try:
        if action == 'post_add' and reverse:
            for pk in pk_set:
                investor = InvestorProfile.objects.get(pk=pk)
                notification_category = NOTIFICATION_CATEGORIES['follow']
                data = {
                    'notification_category': notification_category.id,
                    'investor': investor.id,
                    'startup': instance.id,
                }
                create_notification(instance, notification_category, data, StartUpNotificationCreateSerializer)
    except Exception as e:
        logger.error(f"Unexpected error occurs during StartUp notification creation: {e}")


@receiver(post_save, sender=StartupProfile)
def notify_startup_update(sender, instance, created, **kwargs):
    """
    Signal handler for startup profile updates.
    Notifies all followers when a startup updates their profile.
    
    Triggered by:
    - Any save operation on StartupProfile
    """
    followers = instance.followers.all()
    notification_category = NOTIFICATION_CATEGORIES['profile_update']
    for investor in followers:
        data = {
            'notification_category': notification_category.id,
            'investor': investor.id,
            'startup': instance.id,
        }
        create_notification(investor, notification_category, data, InvestorNotificationCreateSerializer)


@receiver(post_save, sender=Project)
def notify_investors_about_new_project(sender, instance, created, **kwargs):
    """
    Signal handler for new project creation.
    Notifies all followers of the startup when they create a new project.
    
    Triggered by:
    - Creation of a new Project instance
    """
    if not created:
        return
    followers = instance.startup.followers.all()
    notification_category = NOTIFICATION_CATEGORIES['new_project']
    for investor in followers:
        data = {
            'notification_category': notification_category.id,
            'investor': investor.id,
            'startup': instance.startup.id,
        }
        create_notification(investor, notification_category, data, InvestorNotificationCreateSerializer)
                