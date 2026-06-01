# Copyright (c) 2026 xDEM developers
#
# This file is part of the xDEM project:
# https://github.com/glaciohack/xdem
# https://github.com/GlacioHack/xdem-plugin-qgis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import importlib
import importlib.metadata
import os
import shutil
import sys

import requests
from packaging.requirements import Requirement
from pip._internal.cli.main import main as pip_main
from qgis.core import Qgis, QgsMessageLog


class XdemInstaller:
    """
    The xdem python installer.
    """

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.deps_dir = os.path.join(self.plugin_dir, "xdem_dependencies")

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

    def log(self, message, info=True, critical=False, warning=False):
        """
        Displays information in the QGIS console, in the xDEM section.
        """
        if info:
            level = Qgis.MessageLevel.Info
        elif critical:
            level = Qgis.MessageLevel.Critical
        elif warning:
            level = Qgis.MessageLevel.Warning

        QgsMessageLog.logMessage(message, "xDEM", level)

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
        Install xdem and its dependencies in the dependencies folder.
        """
        for package in self.required_packages:
            pip_main(
                [
                    "install",
                    "--target",
                    self.deps_dir,
                    package,
                    "--trusted-host",
                    "pypi.org",
                ]
            )

    def clean_shared_packages(self):
        """
        Clean the libs folder by removing the packages already present in qgis.
        """
        for xdem_package in os.listdir(self.deps_dir):
            for shared_package in self.shared_packages:
                if self.exist_in_qgis(shared_package):
                    if xdem_package.startswith(shared_package):
                        target_package = os.path.join(self.deps_dir, xdem_package)
                        shutil.rmtree(target_package)

    def download_requirements(self):
        """
        Download the xdem requirements file.
        """
        url = "https://raw.githubusercontent.com/GlacioHack/xdem/main/requirements.txt"
        requirements = requests.get(url).text
        return requirements

    def check_dependencies(self):
        """
        Check if the environment satisfies the requirements.
        """
        try:
            requirements = self.download_requirements()
            for line in requirements.splitlines():
                if not line or line.startswith("#"):
                    continue
                req = Requirement(line)
                installed_version = importlib.metadata.version(req.name)
                if installed_version not in req.specifier:
                    return False
            return True
        except Exception as e:
            self.log(f"Unable to check xdem dependencies: {e}", warning=True)
            return True

    def set_proj_gdal_env(self):
        """
        Search for and set geoutils (rasterio) gdal and proj config.
        - proj.db is the projection database containing all CRS and transforms
        - gdal_data contains drivers (GeoTIFF, JPEG2000, etc.)
        """
        for root, dirs, files in os.walk(self.deps_dir):
            if "rasterio" in root:
                if "proj.db" in files:
                    os.environ["PROJ_DATA"] = root

                if "gdal_data" in dirs:
                    os.environ["GDAL_DATA"] = os.path.join(root, "gdal_data")

    def run(self):
        """
        Check if xdem is already installed, if not it proceed with the install.
        """
        # Python check, xdem works starting with version 3.10
        if sys.version_info < (3, 10):
            self.log(
                "Installation failed, python version lower than 3.10", critical=True
            )
            return False

        # Installing packages and managing conflicts
        if not os.path.isdir(self.deps_dir):
            try:
                os.makedirs(self.deps_dir, exist_ok=True)
                self.install_packages()
                self.clean_shared_packages()
            except Exception as e:
                shutil.rmtree(self.deps_dir)
                self.log(f"Installation failed, error:{e}", critical=True)
                return False

        # Add libs folder to the python path and initialize the proj and gdal data
        if self.deps_dir not in sys.path:
            sys.path.insert(0, self.deps_dir)
            self.set_proj_gdal_env()

        if not self.check_dependencies():
            shutil.rmtree(self.deps_dir)
            self.log("Installation failed, requirements unsatisfied", critical=True)
            return False

        if not self.exist_in_qgis("xdem"):
            shutil.rmtree(self.deps_dir)
            self.log("Installation failed, unable to import xdem", critical=True)
            return False

        self.log("Dependencies loaded successfully")
        return True
