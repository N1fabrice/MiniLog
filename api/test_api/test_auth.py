from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.urls import reverse

class JWTAthenticationTest(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")

        self.user_registration = {
                "username": "simba",
                "email": "simba@gmail.com",
                "password": "simba_123",
                "password2": "simba_123"
                }
        self.user = {
                "username": "simba",
                "email": "simba@gmail.com",
                "password": "simba_123"
                }

    def test_register_user(self):
        """
        Testing registering a user
        """
        # Registering user with all fields
        response = self.client.post(self.register_url, self.user_registration)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], self.user["username"])
        self.assertEqual(response.data["email"], self.user["email"])

        # Registering user with missing username field
        user = {
                "email": "simba@gmail.com",
                "password": "simba_123",
                "password2": "simba_123"
                }
        response = self.client.post(self.register_url, user)
        self.assertEqual(response.status_code, 400)

        # Registering user with missing email field
        user = {
                "username": "simba",
                "password": "simba_123",
                "password2": "simba_123"
                }
        response = self.client.post(self.register_url, user)
        self.assertEqual(response.status_code, 400)

        # Registering user with unmatching password
        user = {
                "username": "simba",
                "email": "simba@gmail.com",
                "password": "simba_123",
                "password2": "simba@123"
                }
        response = self.client.post(self.register_url, user)
        self.assertEqual(response.status_code, 400)


    def test_correct_credentials(self):
        """
        Testing login with correct credentials, 200 Ok and valid token
        """
        # Start by registering user
        user = self.client.post(self.register_url, self.user_registration)
        self.assertEqual(user.status_code, 201)

        # Login with all fields
        response = self.client.post(self.login_url, self.user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    
    def test_bad_credentials(self):
        """
        Testing login with incorrect credentials, 401 Unauthorized
        """
        # Start by registering user
        user = self.client.post(self.register_url, self.user_registration)
        self.assertEqual(user.status_code, 201)

        # Login user with wrong credentials
        wrong_user = {
                "username": "simba",
                "email": "simba@gmail.com",
                "password": "simba_456" # correct password = "simba_123"
                }
        response = self.client.post(self.login_url, wrong_user)
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_token(self):
        """
        Testing token in an Authorization header and access a protected route
        """
        # Start by registering user
        user = self.client.post(self.register_url, self.user_registration)
        self.assertEqual(user.status_code, 201)

        # Login the user
        response = self.client.post(self.login_url, self.user)
        self.assertEqual(response.status_code, 200)
        
        # Providing token to header
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        # Accessing a protected route
        result = self.client.get(reverse("entry-list"))
        self.assertEqual(result.status_code, 200)

    def test_protected_route_without_token(self):
        """
        Testing accessing protected route without token
        """
        # Start by registering user
        user = self.client.post(self.register_url, self.user_registration)
        self.assertEqual(user.status_code, 201)

        # Login the user
        response = self.client.post(self.login_url, self.user)
        self.assertEqual(response.status_code, 200)

         # Accessing a protected route without token
        result = self.client.get(reverse("entry-list"))
        self.assertEqual(result.status_code, 401)
