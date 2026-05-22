import importlib
import importlib.metadata
import os
import shutil
import subprocess
import sys

import requests
from packaging.requirements import Requirement


class XdemInstaller:
    """
    The xdem python installer.
    """

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

    def get_python_version(self):
        """
        Get the major and minor python version.
        """
        version = [sys.version_info.major, sys.version_info.minor]
        return version

    def exist_in_qgis(self, package):
        """
        Check if a specified package exist in qgis.
        """
        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False

    def install_packages(self):
        """
        Install xdem and its dependencies in the libs folder.
        """
        for package in self.required_packages:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    self.libs_folder,
                    package,
                ]
            )

    def clean_shared_packages(self):
        """
        Clean the libs folder by removing the packages already present in qgis.
        """
        for xdem_package in os.listdir(self.libs_folder):
            for shared_package in self.shared_packages:
                if self.exist_in_qgis(shared_package):
                    if xdem_package.startswith(shared_package):
                        target_package = os.path.join(self.libs_folder, xdem_package)
                        shutil.rmtree(target_package)

    def download_requirements(self):
        """
        Download the xdem requirements file.
        """
        url = "https://raw.githubusercontent.com/GlacioHack/xdem/main/requirements.txt"
        requirements = requests.get(url).text
        return requirements

    def check_dependencies(self, requirements):
        """
        Check if the environment satisfies the requirements.
        """
        for line in requirements.splitlines():
            if not line or line.startswith("#"):
                continue
            req = Requirement(line)
            installed_version = importlib.metadata.version(req.name)
            if installed_version not in req.specifier:
                return False
        return True

    def run(self):
        """
        Check if xdem is already installed, if not it proceed with the install.
        """
        if not self.exist_in_qgis("xdem"):
            # Python check, xdem works starting with version 3.10
            if not self.get_python_version() >= [3, 10]:
                raise Exception(
                    "Unable to install xdem, python version lower than 3.10"
                )

            # Installing packages and managing conflicts
            if not os.path.isdir(self.libs_folder):
                try:
                    os.makedirs(self.libs_folder, exist_ok=True)
                    self.install_packages()
                    self.clean_shared_packages()
                except Exception as e:
                    shutil.rmtree(self.libs_folder)
                    raise Exception(f"Unable to install xdem, error:{e}")

            # Add to the python path as the first entry
            if self.libs_folder not in sys.path:
                sys.path.insert(0, self.libs_folder)

            if not self.exist_in_qgis("xdem"):
                shutil.rmtree(self.libs_folder)
                raise Exception("Unable to import xdem after installation")

            if not self.check_dependencies(self.download_requirements()):
                shutil.rmtree(self.libs_folder)
                raise Exception(
                    "Unable to install xdem, requirements are not satisfied"
                )

        return True
