from django.test import TestCase
from rest_router.util import get_timeout
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
