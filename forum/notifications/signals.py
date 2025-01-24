from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import NotificationCategory, InvestorNotification
from profiles.models import InvestorProfile, StartupProfile
from .serializers import StartUpNotificationCreateSerializer, InvestorNotificationCreateSerializer
from projects.models import Project
import logging

logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and reverse:
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
                logger.error(
                    f"Error creating notification for startup {instance.id} "
                    f"and investor {investor.id}: {serializer.errors}"
                )

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
    notification_category, _ = NotificationCategory.objects.get_or_create(name='new_project')
    for investor in followers:
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

#notify investors when a followed project is updated
@receiver(post_save, sender=Project)
def notify_investors_about_project_update(sender, instance, created, **kwargs):
    """
    Notify investors when a project they are following is updated.
    """
    logger.info("Signal triggered for project update.")
    logger.info(f"Project ID: {instance.id}, Created: {created}")

    # Skip if the project is being created
    if created:
        logger.info("Project is being created. Skipping notification.")
        return

    try:
        # Get the "Project Update" notification category
        notification_category, _ = NotificationCategory.objects.get_or_create(name='Project Update')
        logger.info(f"Notification category: {notification_category.id}")

        # Get all investors who are following the startup associated with the project
        investors = instance.startup.followers.prefetch_related('user_notification_preferences').all()
        logger.info(f"Investors found: {investors.count()}")

        # Prepare a list of valid notifications
        notifications_to_create = []
        for investor in investors:
            # Check if the investor has allowed notifications for this category
            # if not have_preference(investor, notification_category):
            #     logger.info(f"Investor {investor.id} does not allow notifications for this category.")
            #     continue

            logger.info(f"Creating notification for investor: {investor.id}")
            notifications_to_create.append({
                'notification_category': notification_category,
                'investor': investor,
                'startup': instance.startup,
            })

            # Bulk create notifications to reduce database queries
            if notifications_to_create:
                created_notifications = InvestorNotification.objects.bulk_create([
                    InvestorNotification(**data) for data in notifications_to_create
                ])
                logger.info(f"Successfully created {len(created_notifications)} notifications.")
            else:
                logger.info("No notifications to create.")

    except Exception as e:
        logger.error(f"An error occurred while processing project update notifications: {e}")