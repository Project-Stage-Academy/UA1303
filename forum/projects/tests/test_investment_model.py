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

    def test_valid_investment(self):
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

    def test_multiple_investors_exceeding_goal(self):
        """Test that multiple investors' investments do not exceed the funding goal."""
        Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("80.00"))

        other_investor = InvestorProfileFactory()
        investment = Investment(investor=other_investor, project=self.project, share=Decimal("30.00"))

        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_large_number_of_small_investments(self):
        """Test that many small investments are aggregated correctly."""
        for _ in range(100):
            Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("1.00"))

        self.assertEqual(self.project.total_funding, Decimal("100.00"))
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("1.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_decimal_precision(self):
        """Test that investments with high precision are handled correctly."""
        investment = Investment(
            investor=self.investor, project=self.project, share=Decimal("50.123456")
        )
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_investment_after_funding_completion(self):
        """Test that investments cannot be made after funding is completed."""
        Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("100.00"))
        self.project.is_completed = True
        self.project.save()

        investment = Investment(investor=self.investor, project=self.project, share=Decimal("10.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_multiple_investments_same_investor(self):
        """Test that multiple investments by the same investor are allowed and aggregated."""
        Investment.objects.create(investor=self.investor, project=self.project, share=Decimal("30.00"))
        investment = Investment(investor=self.investor, project=self.project, share=Decimal("20.00"))

        investment.full_clean()  # Should not raise ValidationError
        investment.save()

        self.assertEqual(self.project.total_funding, Decimal("50.00"))

    def test_investment_with_nonexistent_investor(self):
        """Test that investments cannot be created with an invalid investor."""
        invalid_investor = None
        investment = Investment(investor=invalid_investor, project=self.project, share=Decimal("50.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()

    def test_investment_to_project_with_zero_funding_goal(self):
        """Test that no investments can be made to a project with a funding goal of zero."""
        self.project.funding_goal = Decimal("0.00")
        self.project.save()

        investment = Investment(investor=self.investor, project=self.project, share=Decimal("10.00"))
        with self.assertRaises(ValidationError):
            investment.full_clean()
