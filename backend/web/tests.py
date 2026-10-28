from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import Registration, TeamMember

class SecurityAndRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unregistered_access_to_success_redirects_to_register(self):
        """Unregistered users or failed registrations must NOT access the success page."""
        response = self.client.get(reverse('success'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('register')))

    def test_unregistered_access_to_receipt_redirects_to_register(self):
        """Unregistered users must NOT access the receipt page."""
        response = self.client.get(reverse('receipt'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('register')))

    def test_unregistered_access_to_pdf_receipt_redirects_to_register(self):
        """Unregistered users must NOT access the pdf-receipt page."""
        response = self.client.get(reverse('pdf_receipt'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('register')))

    def test_honeypot_bot_rejection(self):
        """If anti-bot honeypot is filled, registration must be rejected."""
        dummy_file = SimpleUploadedFile("abstract.pdf", b"%PDF-1.4 dummy abstract", content_type="application/pdf")
        post_data = {
            'website_hp': 'I am a bot',
            'project_title': 'Bot Project',
            'team_size': '2',
            'college_selection': 'NRCM',
            'project_document': dummy_file,
            'member_name_1': 'Bot Lead',
            'member_email_1': 'bot@example.com',
            'member_mobile_1': '9876543210',
            'member_roll_1': '23X01A0501',
            'member_dept_1': 'CSE',
            'member_tshirt_1': 'M',
            'member_food_1': 'VEG',
            'member_name_2': 'Bot Two',
            'member_email_2': 'bot2@example.com',
            'member_mobile_2': '9876543211',
            'member_roll_2': '23X01A0502',
            'member_dept_2': 'CSE',
            'member_tshirt_2': 'M',
            'member_food_2': 'VEG',
        }
        response = self.client.post(reverse('register'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Registration.objects.filter(project_title='Bot Project').count(), 0)

    def test_failed_registration_does_not_redirect_to_success(self):
        """Invalid form submission should render register.html with error and NOT redirect to success."""
        # Missing required project_document and member details
        post_data = {
            'project_title': 'Incomplete Project',
            'team_size': '2',
            'college_selection': 'NRCM',
        }
        response = self.client.post(reverse('register'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/register.html')
        self.assertEqual(Registration.objects.filter(project_title='Incomplete Project').count(), 0)
        # Session must not have registration_id
        self.assertIsNone(self.client.session.get('registration_id'))

    @patch('web.views.send_registration_email')
    def test_successful_registration_flow(self, mock_send_email):
        """Valid registration redirects to success, sets session, and allows viewing success page."""
        dummy_doc = SimpleUploadedFile("abstract.pdf", b"%PDF-1.4 test document content", content_type="application/pdf")
        post_data = {
            'project_title': 'Smart AI Health Monitor',
            'team_size': '2',
            'college_selection': 'NRCM',
            'project_document': dummy_doc,
            'member_name_1': 'Alice Sharma',
            'member_email_1': 'alice@example.com',
            'member_mobile_1': '9876543210',
            'member_roll_1': '23X01A0501',
            'member_dept_1': 'CSE',
            'member_tshirt_1': 'M',
            'member_food_1': 'VEG',
            'member_name_2': 'Bob Verma',
            'member_email_2': 'bob@example.com',
            'member_mobile_2': '9876543211',
            'member_roll_2': '23X01A0502',
            'member_dept_2': 'CSE',
            'member_tshirt_2': 'L',
            'member_food_2': 'NON-VEG',
        }
        response = self.client.post(reverse('register'), post_data)
        # Must redirect to success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('success'))

        # Check DB records
        reg = Registration.objects.filter(project_title='Smart AI Health Monitor').first()
        self.assertIsNotNone(reg)
        self.assertEqual(reg.team_members.count(), 2)

        # Now following the redirect to success with the active session
        success_response = self.client.get(reverse('success'))
        self.assertEqual(success_response.status_code, 200)
        self.assertContains(success_response, 'Smart AI Health Monitor')
        self.assertContains(success_response, 'Alice Sharma')
