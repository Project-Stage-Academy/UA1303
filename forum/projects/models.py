from django.core.validators import MinValueValidator
from django.db import models
from profiles.models import StartupProfile

# Create your models here.

class Project(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name="project")
    title = models.CharField(max_length=100)
    funding_goal = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0.00)]
        )
    is_published = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"Project("
            f"id={self.pk}, "
            f"startup={self.startup.company_name}, "
            f"funding goal={self.funding_goal}"
            f")"
        )


class Media(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="media")
    file = models.ImageField()


class Description(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="description")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)