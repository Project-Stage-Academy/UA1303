from rest_framework import serializers
from .models import Project, Description


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['description']


class ProjectSerializer(serializers.ModelSerializer):
    """Nested serializer that handles both Project and its description"""

    description = DescriptionSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['startup', 'is_completed']

    def create(self, validated_data):
        """Overridden method to create a project with description"""
        description_data = validated_data.pop('description', None)
        project = Project.objects.create(**validated_data)

        # Handle description data if data exists
        if description_data:
            Description.objects.create(project=project, **description_data)
        return project

    def update(self, instance, validated_data):

        """Overridden method that updates a project and it's description.
         Or creates a new description if the old one doesn't exist"""

        description_data = validated_data.pop('description', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle description data if data exists
        if description_data:
            if hasattr(instance, 'description'):
                for attr, value in description_data.items():
                    setattr(instance.description, attr, value)
                instance.description.save()
            else:
                Description.objects.create(project=instance, **description_data)
        return instance



