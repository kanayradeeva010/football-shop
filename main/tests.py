from django.test import TestCase, Client
from .models import Product
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

class FootballShopFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create single browser instance for all tests
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close browser after all tests complete
        cls.browser.quit()

    def setUp(self):
        # Create user for testing
        self.test_user = User.objects.create_user(
            username='testadmin',
            password='testpassword'
        )

    def tearDown(self):
        # Clean up browser state between tests
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        # Navigate to blank page to reset state
        self.browser.get("about:blank")

    def login_user(self):
        """Helper method to login user"""
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

    def test_login_page(self):
        # Test login functionality
        self.login_user()

        # Check if login is successful
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Kavza")

        logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertTrue(logout_link.is_displayed())

    def test_register_page(self):
        # Test register functionality
        self.browser.get(f"{self.live_server_url}/register/")

        # Check if register page opens
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        # Fill register form
        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        # Check redirect to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_product(self):
        """Test create product functionality with stable login and waits"""
        # 1. Login user
        self.login_user()

        # Tunggu sampai halaman utama muncul
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Kavza"))

        # 2. Klik tombol Add Product
        add_button = self.browser.find_element(By.XPATH, "//a/button[contains(text(), 'Create Product')]")
        add_button.click()

        # Tunggu sampai halaman Add Product muncul
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Create Product"))

        # 3. Isi form dengan data valid
        name_input = self.browser.find_element(By.NAME, "name")
        price_input = self.browser.find_element(By.NAME, "price")
        description_input = self.browser.find_element(By.NAME, "description")
        category_select = self.browser.find_element(By.NAME, "category")
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        stock_input = self.browser.find_element(By.NAME, "product_stock")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")

        name_input.send_keys("Test Product Name")
        price_input.send_keys("150000")  # pastikan integer
        description_input.send_keys("Test product description for selenium testing")
        thumbnail_input.send_keys("https://example.com/image.jpg")
        stock_input.send_keys("10")  # pastikan integer

        # Set category (pastikan value ada di model choices)
        Select(category_select).select_by_value("shoes")

        # Check is_featured checkbox
        is_featured_checkbox.click()

        # 4. Submit form
        submit_button = self.browser.find_element(By.XPATH, "//input[@type='submit' and @value='Create Product']")
        submit_button.click()

        # 5. Tunggu redirect ke halaman utama
        try:
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Kavza"))
        except Exception:
            print("Current page h1 after submit:", self.browser.find_element(By.TAG_NAME, "h1").text)
            self.browser.save_screenshot("debug_create_product.png")
            raise

        # 6. Pastikan nama produk muncul di halaman utama
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Test Product Name")))
        product_name = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Test Product Name")
        self.assertTrue(product_name.is_displayed())


    def test_product_detail(self):
        # Test news detail page

        # Login first because of @login_required decorator
        self.login_user()

        # Create news for testing
        product = Product.objects.create(
             name="Detail Test Product",
            description="Content for detail testing",
            category="shoes",
            user=self.test_user,
            price=150000,
            product_stock=5
        )

        # Open news detail page
        self.browser.get(f"{self.live_server_url}/product/{product.id}/")

         # Pastikan halaman detail terbuka dengan benar
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Detail Test Product"))

        # Cek isi halaman sesuai dengan data product
        self.assertIn("Detail Test Product", self.browser.page_source)
        self.assertIn("Content for detail testing", self.browser.page_source)
        self.assertIn("Shoes", self.browser.page_source)  # category display
        self.assertIn("Author: testadmin", self.browser.page_source)


    def test_logout(self):
        # Test logout functionality
        self.login_user()

        # Click logout button - text is inside button, not link
        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        # Check if redirected to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_main_page(self):
        # Buat products untuk testing
        Product.objects.create(
            name="My Test Product",
            description="My product content",
            category="shoes",
            price=100000,
            product_stock=10,
            user=self.test_user
        )
        Product.objects.create(
            name="Other User Product",
            description="Other content",
            category="apparel",
            price=150000,
            product_stock=5,
            user=self.test_user  # Bisa diganti user lain kalau mau tes multi-user
        )

        # Login user
        self.login_user()

        wait = WebDriverWait(self.browser, 10)

        # Test filter "All Products"
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Products")))
        all_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "All Products")
        all_button.click()
        self.assertIn("My Test Product", self.browser.page_source)
        self.assertIn("Other User Product", self.browser.page_source)

        # Test filter "My Products"
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "My Products")))
        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Products")
        my_button.click()
        self.assertIn("My Test Product", self.browser.page_source)
        self.assertIn("Other User Product", self.browser.page_source)  # Masih user yang sama
