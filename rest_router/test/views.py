from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
import unittest
import os
import six
import urllib3

ACCESS_PATH = os.path.join(os.path.dirname(__file__),
                           "resources", "testing.json")


# Overriding urllib methods here, so we can test as much as possible...
def override_connection(*args, **kwargs):
    class FakeResponse(dict):
        def __init__(self, *args, **kwargs):
            super(FakeResponse, self).__init__(*args, **kwargs)
        status = 200
        data = "OK"
        headers = {}

        def getheaders(self):
            return self.headers.keys()

        def getheader(self, name):
            return self.headers[name]

    class FakeConn(object):
        def urlopen(self, method, url, *args, **kwargs):
            response = FakeResponse()
            if method == "GET":
                if url == "http://localhost/testing/v1/ok":
                    response.data = "This is valid service #1"

            if method == "DELETE":
                response.data = "Method DELETE"

            if method == "PUT":
                response.data = "Method PUT"

            if method == "PATCH":
                response.data = "Method PATCH"

            if method == "POST":
                response.data = "Method POST"

            # Just reflecting back all headers given to us.
            for header in kwargs["headers"]:
                response[header] = kwargs["headers"][header]
            return response
    return FakeConn()


@override_settings(R2_ACCESS_FILE=ACCESS_PATH)
class TestProxy(TestCase):
    def test_bad_service(self):
        client = Client()
        response = client.get(reverse('proxy',
                                      kwargs={"service": "nogo", "url": "ok"}),
                              SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 403)
        error = b"Your app doesn't have access to nogo"
        self.assertEquals(response.content, error)

    def test_no_client_id(self):
        client = Client()
        response = client.get(reverse('proxy',
                                      kwargs={"service": "nogo", "url": "ok"}),
                              )

        self.assertEquals(response.status_code, 403)

        error = b"No client identification provided"
        self.assertEquals(response.content, error)

    def test_ok_service1(self):
        original = urllib3.connection_from_url

        urllib3.connection_from_url = override_connection

        client = Client()
        response = client.get(reverse('proxy',
                                      kwargs={"service": "valid1",
                                              "url": "ok"}),
                              SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 200)
        content = b"This is valid service #1"
        self.assertEquals(response.content, content)

        response = client.put(reverse('proxy',
                                      kwargs={"service": "valid1",
                                              "url": "ok"}),
                              SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 200)
        content = b"Method PUT"
        self.assertEquals(response.content, content)

        response = client.delete(reverse('proxy',
                                         kwargs={"service": "valid1",
                                                 "url": "ok"}),
                                 SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 200)
        content = b"Method DELETE"
        self.assertEquals(response.content, content)

        response = client.post(reverse('proxy',
                                       kwargs={"service": "valid1",
                                               "url": "ok"}),
                               SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 200)
        content = b"Method POST"
        self.assertEquals(response.content, content)

        response = client.patch(reverse('proxy',
                                        kwargs={"service": "valid1",
                                                "url": "ok"}),
                                SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 200)
        content = b"Method PATCH"
        self.assertEquals(response.content, content)

        urllib3.connection_from_url = original

    @unittest.skip("Not passing back headers now")
    def test_headers(self):
        original = urllib3.connection_from_url

        urllib3.connection_from_url = override_connection

        client = Client()
        response = client.get(reverse('proxy',
                                      kwargs={"service": "valid2",
                                              "url": "ok"}),
                              SSL_CLIENT_S_DN_CN="ok_service",
                              X_CUSTOM_REFLECT_TEST="Test Value")

        self.assertEquals(response.status_code, 200)

        self.assertEquals(response["X-CUSTOM-REFLECT-TEST"], "Test Value")

        urllib3.connection_from_url = original
