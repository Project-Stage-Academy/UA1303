from PIL import Image
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from profiles.models import StartupProfile

def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")
    
    valid_extensions = ["jpg", "jpeg", "png"]
    if not file.name.split(".")[-1].lower() in valid_extensions:
        raise ValidationError(f"Only {", ".join(valid_extensions)} files are allowed.")
    
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("The file size must not exceed 5MB.")
# Create your models here.

class Project(models.Model):
    """
    Represents a project created by a startup on the platform.

    Attributes:
        startup (ForeignKey): A reference to the `StartupProfile` that owns the project.
        title (CharField): The title of the project (max length: 100 characters).
        funding_goal (DecimalField): The funding target for the project, 
                                     with a minimum value of 0.00.
        is_published (BooleanField): Indicates whether the project is visible to the public.
        is_completed (BooleanField): Indicates whether the project has been completed.
        created_at (DateTimeField): The date and time the project was created.
        updated_at (DateTimeField): The date and time the project was last updated.
    """
    startup = models.ForeignKey(
        StartupProfile, 
        on_delete=models.CASCADE, 
        related_name="projects", 
        db_index=True
        )
    title = models.CharField(max_length=100)
    funding_goal = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0.00)]
        )
    is_published = models.BooleanField(default=False, db_index=True)
    is_completed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(check=models.Q(funding_goal__gte=0), name="funding_goal_non_negative")]

    def __str__(self):
        return (
            f"Project("
            f"id={self.pk}, "
            f"startup={self.startup.company_name}, "
            f"funding goal={self.funding_goal}"
            f")"
        )


class Media(models.Model):
    """
    Represents media files (e.g., images) associated with a project.

    Attributes:
        project (ForeignKey): A reference to the `Project` the media belongs to.
        file (ImageField): An uploaded media file, validated for allowed formats 
                           (e.g., .jpg, .jpeg, .png) and size limits.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="media")
    file = models.ImageField(validators=[validate_image])

    def __str__(self):
        return f"Media(id={self.pk}, startup={self.project.startup.company_name}, project={self.project.title}, file={self.file})"
    
        


class Description(models.Model):
    """
    Represents a detailed description of a project.

    Attributes:
        project (OneToOneField): A one-to-one reference to the `Project` being described.
        description (TextField): A detailed text description of the project.
        created_at (DateTimeField): The date and time the description was created.
        updated_at (DateTimeField): The date and time the description was last updated.
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="description")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Description(id={self.pk}, startup={self.project.startup.company_name}, project={self.project.title}, description={self.description})"