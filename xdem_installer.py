import importlib
import importlib.metadata
import os
import shutil
import subprocess
import sys

import requests
from packaging.requirements import Requirement
from qgis.core import Qgis, QgsMessageLog
from requests.exceptions import RequestException


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
        try:
            url = "https://raw.githubusercontent.com/GlacioHack/xdem/main/requirements.txt"
            requirements = requests.get(url).text
            return requirements
        except RequestException:
            QgsMessageLog.logMessage(
                "Request failled, unable to check xdem requirements",
                tag="xDEM",
                level=Qgis.MessageLevel.Warning,
            )
            return None

    def check_dependencies(self, requirements):
        """
        Check if the environment satisfies the requirements.
        """
        if requirements:
            for line in requirements.splitlines():
                if not line or line.startswith("#"):
                    continue
                req = Requirement(line)
                installed_version = importlib.metadata.version(req.name)
                if installed_version not in req.specifier:
                    return False
            return True
        return True

    def run(self):
        """
        Check if xdem is already installed, if not it proceed with the install.
        """
        # Python check, xdem works starting with version 3.10
        if sys.version_info < (3, 10):
            QgsMessageLog.logMessage(
                "Unable to proceed with the installation, python version lower than 3.10",
                tag="xDEM",
                level=Qgis.MessageLevel.Critical,
            )
            return False

        # Installing packages and managing conflicts
        if not os.path.isdir(self.libs_folder):
            try:
                os.makedirs(self.libs_folder, exist_ok=True)
                self.install_packages()
                self.clean_shared_packages()
            except Exception as e:
                shutil.rmtree(self.libs_folder)
                QgsMessageLog.logMessage(
                    f"Unable to install xdem, error:{e}",
                    tag="xDEM",
                    level=Qgis.MessageLevel.Critical,
                )
                return False

        # Add libs folder to the python path as the first entry
        if self.libs_folder not in sys.path:
            sys.path.insert(0, self.libs_folder)

        if not self.exist_in_qgis("xdem"):
            shutil.rmtree(self.libs_folder)
            QgsMessageLog.logMessage(
                "Unable to import xdem after installation",
                tag="xDEM",
                level=Qgis.MessageLevel.Critical,
            )
            return False

        if not self.check_dependencies(self.download_requirements()):
            shutil.rmtree(self.libs_folder)
            QgsMessageLog.logMessage(
                "Unable to install xdem, requirements are not satisfied",
                tag="xDEM",
                level=Qgis.MessageLevel.Critical,
            )
            return False

        QgsMessageLog.logMessage(
            "xdem loaded", tag="xDEM", level=Qgis.MessageLevel.Info
        )
        return True
