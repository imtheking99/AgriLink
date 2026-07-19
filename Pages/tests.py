from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from unittest.mock import Mock, patch
from .models import Crop, UserProfile

class CropAccessControlTests(TestCase):
    def setUp(self):
        # Create two test users
        self.farmer_a = User.objects.create_user(username='farmer_a', password='password123')
        UserProfile.objects.create(user=self.farmer_a, user_type='farmer', phone='12345', district='Galle')
        self.farmer_b = User.objects.create_user(username='farmer_b', password='password123')
        UserProfile.objects.create(user=self.farmer_b, user_type='farmer', phone='67890', district='Colombo')
        
        # Create a small dummy image for testing file uploads
        self.dummy_image = SimpleUploadedFile(
            name='test_crop.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/gif'
        )
        
        # Create a crop belonging to farmer_a
        self.crop_a = Crop.objects.create(
            farmer=self.farmer_a,
            crop_name='Paddy',
            quantity='1000 kg',
            district='Galle',
            expected_harvest_date=date(2026, 8, 15),
            crop_image=self.dummy_image
        )

    def test_anonymous_redirect(self):
        """Verify that anonymous users are redirected to login when accessing dashboard or CRUD urls."""
        response = self.client.get(reverse('farmer_dashboard'))
        self.assertRedirects(response, '/login/?next=/farmer/')
        
        response = self.client.get(reverse('crop_add'))
        self.assertRedirects(response, '/login/?next=/farmer/add/')
        
        response = self.client.get(reverse('crop_edit', args=[self.crop_a.id]))
        self.assertRedirects(response, f'/login/?next=/farmer/edit/{self.crop_a.id}/')

    def test_owner_can_view_and_manage(self):
        """Verify that a farmer can view and manage their own crops."""
        # Log in as farmer_a
        self.client.login(username='farmer_a', password='password123')
        
        # Verify dashboard shows the crop
        response = self.client.get(reverse('farmer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paddy')
        self.assertContains(response, '1000 kg')
        
        # Verify can edit crop
        edit_url = reverse('crop_edit', args=[self.crop_a.id])
        edit_data = {
            'crop_name': 'Paddy Updated',
            'quantity': '1200 kg',
            'district': 'Galle',
            'expected_harvest_date': '2026-08-20',
            # Leaving image blank since we want to check if it keeps the original image
        }
        response = self.client.post(edit_url, edit_data)
        self.assertRedirects(response, reverse('farmer_dashboard'))
        self.crop_a.refresh_from_db()
        self.assertEqual(self.crop_a.crop_name, 'Paddy Updated')
        self.assertEqual(self.crop_a.quantity, '1200 kg')

    def test_non_owner_restricted(self):
        """Verify that a farmer cannot view, edit, or delete another farmer's crop."""
        # Log in as farmer_b
        self.client.login(username='farmer_b', password='password123')
        
        # Verify farmer_b's dashboard does NOT show farmer_a's crop
        response = self.client.get(reverse('farmer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Paddy')
        
        # Verify farmer_b cannot edit farmer_a's crop
        edit_url = reverse('crop_edit', args=[self.crop_a.id])
        edit_data = {
            'crop_name': 'Hacked Paddy',
            'quantity': '9999 kg',
            'district': 'Colombo',
            'expected_harvest_date': '2026-08-20',
        }
        response = self.client.post(edit_url, edit_data)
        self.assertRedirects(response, reverse('farmer_dashboard'))
        
        # Check database remains unchanged
        self.crop_a.refresh_from_db()
        self.assertEqual(self.crop_a.crop_name, 'Paddy')
        
        # Verify farmer_b cannot delete farmer_a's crop
        delete_url = reverse('crop_delete', args=[self.crop_a.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('farmer_dashboard'))
        self.assertTrue(Crop.objects.filter(id=self.crop_a.id).exists())

    @patch('Pages.views.requests.get')
    def test_dashboard_shows_weather_for_crop_district(self, mock_get):
        """The farmer dashboard should display weather details for the crop district."""
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            'name': 'Galle',
            'main': {'temp': 27, 'humidity': 78},
            'weather': [{'main': 'Clouds', 'description': 'few clouds'}],
        }
        mock_get.return_value = mock_response

        self.client.login(username='farmer_a', password='password123')
        response = self.client.get(reverse('farmer_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weather for Galle')
        self.assertContains(response, 'Few clouds')


class BuyerDashboardTests(TestCase):
    def setUp(self):
        # Create a buyer user
        self.buyer = User.objects.create_user(username='buyer_test', password='password123')
        UserProfile.objects.create(user=self.buyer, user_type='buyer', phone='12345', district='Colombo')

        # Create a farmer user
        self.farmer = User.objects.create_user(username='farmer_test', password='password123')
        UserProfile.objects.create(user=self.farmer, user_type='farmer', phone='67890', district='Kandy')

        # Create a crop and bid
        self.dummy_image = SimpleUploadedFile(
            name='test_crop.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/gif'
        )
        self.crop = Crop.objects.create(
            farmer=self.farmer,
            crop_name='Carrot',
            quantity='100 kg',
            district='Kandy',
            expected_harvest_date=date(2026, 8, 15),
            crop_image=self.dummy_image
        )

    def test_anonymous_redirect(self):
        """Verify that anonymous users are redirected to login when accessing buyer dashboard."""
        response = self.client.get(reverse('buyer_dashboard'))
        self.assertRedirects(response, '/login/?next=/buyer/')

    def test_farmer_restricted_from_buyer_dashboard(self):
        """Verify that farmer user is redirected to farmer dashboard when trying to access buyer dashboard."""
        self.client.login(username='farmer_test', password='password123')
        response = self.client.get(reverse('buyer_dashboard'))
        self.assertRedirects(response, reverse('farmer_dashboard'))

    def test_buyer_can_view_dashboard(self):
        """Verify that buyer user can view buyer dashboard and context is calculated properly."""
        self.client.login(username='buyer_test', password='password123')
        response = self.client.get(reverse('buyer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buyer Dashboard')
        self.assertIn('active_bids_count', response.context)
        self.assertIn('won_bids_count', response.context)
        self.assertIn('total_spent_formatted', response.context)

    def test_buyer_can_filter_bidding_page_by_harvest_date(self):
        """Verify that a buyer can filter crop listings on the bidding page by crop name and harvest date range."""
        # Create another crop with a different harvest date
        Crop.objects.create(
            farmer=self.farmer,
            crop_name='Leeks',
            quantity='50 kg',
            district='Nuwara Eliya',
            expected_harvest_date=date(2026, 9, 20),
            crop_image=self.dummy_image
        )

        self.client.login(username='buyer_test', password='password123')

        # Request bidding page with range matching only Carrot crop (2026-08-01 to 2026-08-31)
        response = self.client.get(reverse('bidding_page') + '?start_date=2026-08-01&end_date=2026-08-31')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h2>Carrot</h2>')
        self.assertNotContains(response, '<h2>Leeks</h2>')

        # Request bidding page with range matching only Leeks crop (2026-09-01 to 2026-09-30)
        response = self.client.get(reverse('bidding_page') + '?start_date=2026-09-01&end_date=2026-09-30')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h2>Leeks</h2>')
        self.assertNotContains(response, '<h2>Carrot</h2>')

        # Request bidding page with range matching both crops (2026-08-01 to 2026-10-01)
        response = self.client.get(reverse('bidding_page') + '?start_date=2026-08-01&end_date=2026-10-01')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h2>Carrot</h2>')
        self.assertContains(response, '<h2>Leeks</h2>')

        # Request bidding page with name filter matching Carrot
        response = self.client.get(reverse('bidding_page') + '?crop_name=Carrot')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h2>Carrot</h2>')
        self.assertNotContains(response, '<h2>Leeks</h2>')

        # Request bidding page with name filter matching Carrot but out of date range
        response = self.client.get(reverse('bidding_page') + '?crop_name=Carrot&start_date=2026-09-01')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<h2>Carrot</h2>')
        self.assertNotContains(response, '<h2>Leeks</h2>')



