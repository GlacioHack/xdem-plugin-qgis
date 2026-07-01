# Copyright (c) 2026 Centre National d'Etudes Spatiales (CNES).
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
import sys

import requests
from packaging.requirements import Requirement
from pip._internal.cli.main import main as pip_main
from qgis.core import Qgis, QgsMessageLog


class XdemInstaller:
    """
    The xdem python installer
    """

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.deps_dir = os.path.join(self.plugin_dir, "xdem_dependencies")

        self.required_packages = [
            "scipy<=1.17",  # Force max scipy 1.17 because 1.18 needs numpy >= 2.0 (QGIS runs on numpy 1.26.4)
            "weasyprint",
            "matplotlib",
            "pytest",
            "cairocffi",
            "cerberus",
            "scikit-learn",
            "xdem",
        ]

    def log(self, message):
        """
        Displays information in the QGIS console, in the xDEM section
        """
        QgsMessageLog.logMessage(message, "xDEM", Qgis.MessageLevel.Info)

    def exist_in_qgis(self, package):
        """
        Check if a specified package exist in qgis
        """
        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False

    def install_packages(self):
        """
        Install xdem and its dependencies in the dependencies folder
        """
        pip_cmd = [
            "install",
            "--target",
            self.deps_dir,
            "--trusted-host",
            "pypi.org",
        ] + self.required_packages

        pip_main(pip_cmd)

    def check_requirements(self):
        """
        Check if the environment satisfies the requirements.
        """
        try:
            url = "https://raw.githubusercontent.com/GlacioHack/xdem/main/requirements.txt"
            requirements = requests.get(url).text
        except Exception as e:
            self.log(f"Unable to check requirements, error: {e}")
            return True

        for line in requirements.splitlines():
            if not line or line.startswith("#"):
                continue

            req = Requirement(line)
            installed_version = importlib.metadata.version(req.name)

            if installed_version in req.specifier:
                self.log(f"Requirements: {req.name} {installed_version}, satified")
            else:
                self.log(f"Requirements: {req.name} {installed_version}, not satisfied")
                self.log("Installation canceled")
                return False

        return True

    def run(self):
        """
        Check if xdem is already installed, if not it proceed with the install
        """
        # Python version check
        if sys.version_info < (3, 10):
            self.log("Installation failed, python version lower than 3.10")
            return False

        # Installing dependencies
        if not os.path.isdir(self.deps_dir):
            os.makedirs(self.deps_dir, exist_ok=True)
            self.install_packages()

        # Add libs folder add the end of the python path and set proj and gdal environ
        if self.deps_dir not in sys.path:
            sys.path.append(self.deps_dir)

        # Check requirements before import
        if not self.check_requirements():
            return False

        if self.exist_in_qgis("xdem"):
            self.log("Dependencies loaded successfully")
            return True
        else:
            self.log("Installation failed, unable to import xdem")
            return False
