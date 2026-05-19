import os
import sys
import shutil
import importlib
from pip._internal.cli.main import main as pip_main


class XdemInstaller:
    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.libs_folder = os.path.join(self.plugin_dir, "xdem_libs")

        self.required_packages = [
            "cerberus",
            "matplotlib",
            "pytest",
            "scikit-learn",
            "weasyprint",
            "xdem",
        ]

        self.shared_packages = [
            "geopandas",
            "numpy",
            "pandas",
            "pyproj",
            "rasterio",
            "shapely",
        ]

    def check_package(self, package):
        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False

    def install_packages(self):
        for package in self.required_packages:
            pip_main(["install", "--target", self.libs_folder, package])

    def clean_shared_packages(self):
        for xdem_package in os.listdir(self.libs_folder):
            for shared_package in self.shared_packages:
                if self.check_package(shared_package):
                    if xdem_package.startswith(shared_package):
                        target_package = os.path.join(self.libs_folder, xdem_package)
                        shutil.rmtree(target_package)

    def install(self):
        if self.check_package("xdem"):
            return True
        else:
            if not os.path.isdir(self.libs_folder):
                os.makedirs(self.libs_folder, exist_ok=True)
                self.install_packages()
                self.clean_shared_packages()

            if self.libs_folder not in sys.path:
                sys.path.insert(0, self.libs_folder)

            return self.check_package("xdem")
