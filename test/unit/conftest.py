"""Test fixtures."""
from builtins import super

import pytest
from napalm.base.test import conftest as parent_conftest

from napalm.base.test.double import BaseTestDouble

from napalm_asa import asa
from _API_CALL_MOCK_FILES_MAPPING import API_CALL_MOCK_FILES_MAPPING
import json
import re


@pytest.fixture(scope='class')
def set_device_parameters(request):
    """Set up the class."""
    def fin():
        request.cls.device.close()
    request.addfinalizer(fin)

    request.cls.driver = asa.ASADriver
    request.cls.patched_driver = PatchedASADriver
    request.cls.vendor = 'asa'
    parent_conftest.set_device_parameters(request)


def pytest_generate_tests(metafunc):
    """Generate test cases dynamically."""
    parent_conftest.pytest_generate_tests(metafunc, __file__)


class PatchedASADriver(asa.ASADriver):
    """Patched ASA Driver."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Patched ASA Driver constructor."""
        super().__init__(hostname, username, password, timeout, optional_args)

        self.patched_attrs = ['device']
        self.device = FakeASADevice()

    def _authenticate(self):
        """Fake token authentication"""

        return (True, None)

    def _delete_token(self):
        """Fake Delete auth token."""

        return (True, None)


class FakeASADevice(BaseTestDouble):
    """ASA device test double."""

    def get_resp(self, endpoint="", data=None):
        """Fake get_resp method."""
        filename = re.sub(r'\/', '_', endpoint)

        if data is not None:
            parsed_data = json.loads(data)
            if "commands" in parsed_data:
                list_of_commands = parsed_data.get("commands")
                for command in list_of_commands:
                    cmd = re.sub(r'[\[\]\*\^\+\s\|\/]', '_', command)
                    filename += '_{}'.format(cmd)
        output = self.read_json_file('test/unit/asa/mock_data/{}'.format(API_CALL_MOCK_FILES_MAPPING[filename]))
        """Fake an API request to the device by just returning the content of a file."""
        return output

    def has_active_token(self):
        """Fake method to return token status"""
        return True
