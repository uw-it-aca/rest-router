from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
import os

ACCESS_PATH = os.path.join(os.path.dirname(__file__),
                           "resources", "testing.json")


@override_settings(R2_ACCESS_FILE=ACCESS_PATH)
class TestProxy(TestCase):
    def test_bad_service(self):
        client = Client()
        response = client.get(reverse('proxy',
                                      kwargs={"service": "nogo", "url": "ok"}),
                              SSL_CLIENT_S_DN_CN="ok_service")

        self.assertEquals(response.status_code, 403)
