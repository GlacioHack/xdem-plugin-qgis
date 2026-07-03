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
import os
import sys

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
            "cairocffi",  # Matplotlib-specific backend
            "cerberus",
            "scikit-learn",
            "xdem",
        ]

    def log(self, message, level=Qgis.MessageLevel.Info):
        """
        Displays information in the QGIS console, in the xDEM section
        """
        QgsMessageLog.logMessage(message, "xDEM", level)

    def xdem_installed(self):
        try:
            importlib.import_module("xdem")
            return True
        except ModuleNotFoundError as e:
            self.log(f"xdem package not found, error: {e}")
            return False
        except ImportError as e:
            self.log(f"xdem found, import error: {e}")
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

    def run(self):
        """
        Check if xdem is already installed, if not it proceed with the install
        """
        # Python version check
        if sys.version_info < (3, 10):
            self.log(
                "Installation failed, python version lower than 3.10",
                level=Qgis.MessageLevel.Critical,
            )
            return False

        # Installing dependencies
        if not os.path.isdir(self.deps_dir):
            os.makedirs(self.deps_dir, exist_ok=True)
            self.install_packages()

        # Add libs folder add the end of the python path
        if self.deps_dir not in sys.path:
            sys.path.append(self.deps_dir)

        if self.xdem_installed():
            self.log("Dependencies loaded successfully")
            return True
        else:
            self.log(
                "Installation failed, unable to import xdem",
                level=Qgis.MessageLevel.Critical,
            )
            return False
