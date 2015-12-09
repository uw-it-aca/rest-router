from django.test import TestCase
from rest_router.util import get_timeout, clean_headers
from django.test.utils import override_settings
import os

ACCESS_PATH = os.path.join(os.path.dirname(__file__),
                           "resources", "testing.json")


@override_settings(R2_ACCESS_FILE=ACCESS_PATH)
class TestData(TestCase):
    def test_overrides(self):
        self.assertEquals(get_timeout("ok_service", "valid2"), 20)
        self.assertEquals(get_timeout("ok_service", "valid1"), 15)
        self.assertEquals(get_timeout("override_timeout", "valid1"), 60)

    def test_bad_headers(self):
        headers = {"wsgi_test1": "bad",
                   "wsgi_test2": "also bad",
                   "WSgI_test3": "still bad",
                   "SSL_CLIENT_S_DN_CN": "oops",
                   "HTTP_SSL_CLIENT_S_DN_CN": "oops",
                   "ssl_something_else": "meh",
                   "remote_user": "don't send!",
                   "query_string": "nope=nope&no=no",
                   }

        cleaned = clean_headers(headers)
        self.assertFalse("wsgi_test1" in cleaned)
        self.assertFalse("wsgi_test2" in cleaned)
        self.assertFalse("WSgI_test3" in cleaned)
        self.assertFalse("SSL_CLIENT_S_DN_CN" in cleaned)
        self.assertFalse("HTTP_SSL_CLIENT_S_DN_CN" in cleaned)
        self.assertFalse("SSL-CLIENT-S-DN-CN" in cleaned)
        self.assertFalse("ssl_something_else" in cleaned)
        self.assertFalse("remote_user" in cleaned)
        self.assertFalse("REMOTE_USER" in cleaned)
        self.assertFalse("REMOTE-USER" in cleaned)
        self.assertFalse("query_string" in cleaned)
        self.assertFalse("QUERY-STRING" in cleaned)
        self.assertFalse("QUERY_STRING" in cleaned)

    def test_good_headers(self):
        headers = {"HTTP_HOST": "demo.example.com",
                   "HTTP_X_CUSTOM_HEADER": "ok",
                   "http_accept": "text/csv",
                   "CONTENT_TYPE": "text/ok",
                   "CONTENT_LENGTH": 1024,
                   }

        cleaned = clean_headers(headers)
        # Make sure the raw form of those headers isn't used
        self.assertFalse("HTTP_HOST" in cleaned)
        self.assertFalse("HTTP_X_CUSTOM_HEADER" in cleaned)
        self.assertFalse("http_accept" in cleaned)
        self.assertFalse("CONTENT_TYPE" in cleaned)
        self.assertFalse("CONTENT_LENGTH" in cleaned)

        # Make sure the cleaned versions are
        self.assertTrue("HOST" in cleaned)
        self.assertTrue("X-CUSTOM-HEADER" in cleaned)
        self.assertTrue("ACCEPT" in cleaned)
        self.assertTrue("CONTENT-TYPE" in cleaned)
        self.assertTrue("CONTENT-LENGTH" in cleaned)
