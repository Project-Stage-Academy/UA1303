# Generated by Django 5.1.4 on 2024-12-28 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Notification Category',
                'verbose_name_plural': 'Notification Categories',
                'db_table': 'notification_categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='NotificationMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Notification Method',
                'verbose_name_plural': 'Notification Methods',
                'db_table': 'notification_methods',
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='notificationpreference',
            name='allowed_notification_types',
        ),
        migrations.AlterModelOptions(
            name='notificationpreference',
            options={'ordering': ['user'], 'verbose_name': 'Notification Preference', 'verbose_name_plural': 'Notification Preferences'},
        ),
        migrations.AlterModelTable(
            name='notificationpreference',
            table='notification_preferences',
        ),
        migrations.AddField(
            model_name='notificationpreference',
            name='allowed_notification_categories',
            field=models.ManyToManyField(related_name='allowed_categories', to='notifications.notificationcategory'),
        ),
        migrations.AddField(
            model_name='notificationpreference',
            name='allowed_notification_methods',
            field=models.ManyToManyField(related_name='allowed_methods', to='notifications.notificationmethod'),
        ),
        migrations.DeleteModel(
            name='NotificationType',
        ),
    ]