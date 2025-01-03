from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from projects.models import Investment
from .factories import (UserFactory, StartupProfileFactory,
                    InvestorProfileFactory, ProjectFactory)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        # Create test user and project
        self.user = UserFactory(email="testuser@example.com", password="password")
        self.startup = StartupProfileFactory(user=self.user)
        self.investor = InvestorProfileFactory(user=self.user)
        self.project = ProjectFactory(startup=self.startup, funding_goal=Decimal("100.00"), is_completed=False)

    def test_valid_subscription(self):
        """Test that a valid investment is successfully created."""
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("50.00"))
        investment.full_clean()  # Should not raise any ValidationError
        investment.save()

        self.assertEqual(self.project.total_funding, Decimal("50.00"))

    def test_negative_or_zero_share(self):
        """Test that a investment with a negative or zero share is invalid."""
        invalid_shares = [Decimal("0.00"), Decimal("-10.00")]
        for share in invalid_shares:
            with self.subTest(share=share):
                investment = Investment(investor=self.investor, project=self.project, share=share)
                with self.assertRaises(ValidationError):
                    investment.full_clean()

    def test_share_exceeding_funding_goal(self):
        """Test that a investment exceeding the funding goal is invalid."""
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("200.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_share_exceeding_remaining_funds(self):
        """Test that a investment exceeding the remaining funding goal is invalid."""
        Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("80.00"))
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("30.00"))

        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_project_fully_funded(self):
        """Test that no investment can be created for a fully funded project."""
        self.project.is_completed = True
        self.project.save()

        investment = Investment(investor=self.investor, project=self.project, share=Decimal("10.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_exact_funding_completion(self):
        """Test that a investment that exactly completes the funding goal is valid."""
        Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("80.00"))
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("20.00"))
        investment.full_clean()  # Should not raise any ValidationError
        investment.save()

        self.assertEqual(self.project.total_funding, Decimal("100.00"))
        self.assertFalse(self.project.is_completed)  # Assuming you update this separately
