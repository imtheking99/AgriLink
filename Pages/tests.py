from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from .models import Crop

class CropAccessControlTests(TestCase):
    def setUp(self):
        # Create two test users
        self.farmer_a = User.objects.create_user(username='farmer_a', password='password123')
        self.farmer_b = User.objects.create_user(username='farmer_b', password='password123')
        
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
