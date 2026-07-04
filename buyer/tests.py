from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Pages.models import Crop
from buyer.models import Bid
from datetime import date
from decimal import Decimal

# Create your tests here.
class BuyerSystemTests(TestCase):
    def setUp(self):
        # Create users
        self.farmer = User.objects.create_user(username='farmer1', password='password123')
        self.buyer = User.objects.create_user(username='buyer1', password='password123')
        
        # Create crops
        self.crop1 = Crop.objects.create(
            farmer=self.farmer,
            crop_name='CarrotCrop',
            quantity='100 kg',
            district='Colombo',
            expected_harvest_date=date(2026, 7, 15)
        )
        self.crop2 = Crop.objects.create(
            farmer=self.farmer,
            crop_name='PotatoCrop',
            quantity='500 kg',
            district='Nuwara Eliya',
            expected_harvest_date=date(2026, 8, 20)
        )

    def test_anonymous_redirect(self):
        """Verify that anonymous users are redirected to login."""
        response = self.client.get(reverse('buyer_dashboard'))
        self.assertRedirects(response, '/login/?next=/buyer/')
        
        response = self.client.get(reverse('crop_search'))
        self.assertRedirects(response, '/login/?next=/buyer/search/')
        
        response = self.client.get(reverse('crop_detail', args=[self.crop1.id]))
        self.assertRedirects(response, f'/login/?next=/buyer/crop/{self.crop1.id}/')

    def test_crop_search_filtering(self):
        """Verify searching by crop name, district, and harvest date works."""
        self.client.login(username='buyer1', password='password123')
        
        # Search by crop name
        response = self.client.get(reverse('crop_search'), {'crop_name': 'carrot'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CarrotCrop')
        self.assertNotContains(response, 'PotatoCrop')
        
        # Search by district
        response = self.client.get(reverse('crop_search'), {'district': 'Nuwara'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PotatoCrop')
        self.assertNotContains(response, 'CarrotCrop')
        
        # Search by harvest date
        response = self.client.get(reverse('crop_search'), {'harvest_date': '2026-07-15'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CarrotCrop')
        self.assertNotContains(response, 'PotatoCrop')

    def test_place_bid_workflow(self):
        """Verify that buyers can place a bid, and it shows on their dashboard."""
        self.client.login(username='buyer1', password='password123')
        
        # Place a valid bid
        detail_url = reverse('crop_detail', args=[self.crop1.id])
        response = self.client.post(detail_url, {'amount': '15000.00'})
        self.assertRedirects(response, detail_url)
        
        # Check bid in database
        self.assertEqual(Bid.objects.count(), 1)
        bid = Bid.objects.first()
        self.assertEqual(bid.buyer, self.buyer)
        self.assertEqual(bid.crop, self.crop1)
        self.assertEqual(bid.amount, Decimal('15000.00'))
        
        # Check bid appears on dashboard
        response = self.client.get(reverse('buyer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CarrotCrop')
        self.assertContains(response, 'LKR 15000.00')

    def test_invalid_bid_handling(self):
        """Verify that negative or empty bids are rejected."""
        self.client.login(username='buyer1', password='password123')
        detail_url = reverse('crop_detail', args=[self.crop1.id])
        
        # Negative bid
        response = self.client.post(detail_url, {'amount': '-50.00'})
        self.assertEqual(response.status_code, 200)  # Form returns with errors
        self.assertEqual(Bid.objects.count(), 0)
        
        # Zero bid
        response = self.client.post(detail_url, {'amount': '0.00'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bid.objects.count(), 0)
