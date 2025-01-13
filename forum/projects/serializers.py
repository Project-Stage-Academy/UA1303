from rest_framework import serializers
from django.db import transaction
from .models import Project, Description, Investment


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['description']


class ProjectSerializer(serializers.ModelSerializer):
    """Nested serializer that handles both Project and its description"""

    description = serializers.CharField(
        source="description.description",
        allow_blank=True,
        required=False
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['startup', 'is_completed']

    def create(self, validated_data):
        """Overridden method to create a project with description"""
        description_data = validated_data.pop('description', None)
        with transaction.atomic():
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
            if attr in self.fields and value != getattr(instance, attr):
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


class InvestmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an investment.
    This serializer is responsible for validating and saving investment data.
    It expects only the 'share' field to be provided by the user.
    """
    class Meta:
        model = Investment
        fields = ['share', 'investor', 'project']
        read_only_fields = ['investor', 'project']

    def save(self, **kwargs):
        investor = kwargs.get('investor')
        project = kwargs.get('project')

        if not investor or not project:
            raise serializers.ValidationError("Investor and project are required.")

        investment = Investment(
            investor=investor,
            project=project,
            share=self.validated_data['share']
        )
        investment.clean()
        investment.save()
        return investment

    def validate_share(self, value):
        if value <= 0:
            raise serializers.ValidationError("Share must be greater than zero.")
            
        if value > 100:
            raise serializers.ValidationError("Share cannot exceed 100.")

        project = self.context.get('project')
        if project and (project.total_funding + value > project.funding_goal):
            raise serializers.ValidationError("Share exceeds the remaining funding goal.")
        return value
