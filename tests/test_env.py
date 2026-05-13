import pytest
import importlib


packages = [
    "cerberus",
    "matplotlib",
    "pytest",
    "sklearn",
    "weasyprint",
    "xdem",
]


def test_packages():
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            pytest.fail(f"{package} is not correctly installed")
