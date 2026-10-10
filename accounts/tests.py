from django.test import TestCase

from .forms import SignupForm


class SignupFormTests(TestCase):
    def test_short_password_is_rejected(self):
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'short',
            'password2': 'short',
            'phone': '09120000000',
            'role': 'customer',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_signup_creates_a_customer_profile(self):
        form = SignupForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass!234',
            'password2': 'StrongPass!234',
            'phone': '09120000000',
            'role': 'customer',
        })

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.customerprofile.phone, '09120000000')

    def test_signup_creates_a_seller_profile(self):
        form = SignupForm(data={
            'username': 'newseller',
            'email': 'seller@example.com',
            'password1': 'StrongPass!234',
            'password2': 'StrongPass!234',
            'phone': '09120000001',
            'role': 'seller',
        })

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertTrue(hasattr(user, 'sellerprofile'))
