import sys
import pytest
import importlib


def test_python_version():
    assert sys.version_info >= (3, 10)


def test_packages():
    required_packages = [
        "cerberus",
        "matplotlib",
        "pytest",
        "sklearn",
        "weasyprint",
        "xdem",
    ]
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            pytest.fail(f"{package} is not correctly installed")
