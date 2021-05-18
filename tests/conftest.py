import pytest

from subdivisions.client import SubClient


@pytest.fixture
def sub_client():
    test_instance = SubClient()
    test_instance.topic = "FooBar"
    return test_instance
