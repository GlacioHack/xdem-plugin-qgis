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


import platform
import importlib
import os
import shutil
import sys

from pathlib import Path
from importlib.metadata import version
from qgis.core import QgsApplication, QgsTask, Qgis, QgsMessageLog


class XdemInstaller(QgsTask):
    """
    The xDEM python installer
    """

    def __init__(self):
        super().__init__("Installing xDEM Python dependencies",
                         QgsTask.CanCancel)
        self.plugin_dir = os.path.dirname(__file__)
        self.deps_dir = os.path.join(self.plugin_dir, "xdem_dependencies")

        metadata_file = os.path.join(self.plugin_dir, "metadata.txt")

        # Cut the plugin version in metadata.txt to get the xDEM version
        with open(metadata_file, "r") as f:
            for line in f:
                if line.startswith("version="):
                    line_splited = line.split("=")
                    self.required_xdem_version = (line_splited[1])[0:5]
                    break

        self.required_packages = [
            "scipy<=1.17",  # Force max scipy 1.17 because 1.18 needs numpy >= 2.0 (QGIS runs on numpy 1.26.4) # noqa
            "plutoprint",
            "matplotlib",
            "pytest",
            "cairocffi",  # Matplotlib-specific backend
            "cerberus",
            "scikit-learn",
            f"xdem=={self.required_xdem_version}",
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
        except ImportError as e:
            self.log(f"xDEM import error: {e}")
            return False

    def python_exec(self):
        # Linux
        if platform.system() == "Linux":
            path = sys.executable
            return path

        # Windows
        elif platform.system() == "Windows":
            base_path = Path(sys.prefix)
            for file in ["python.exe", "python3.exe"]:
                path = base_path / file
                if path.is_file():
                    return str(path)

        # MacOS (test)
        elif platform.system() == "Darwin":
            base_paths = [
                Path(sys.prefix),
                Path(sys.prefix) / "bin",
                Path(sys.executable).parent,
            ]
            for base_path in base_paths:
                for file in ["python", "python3"]:
                    path = base_path / file
                    if path.is_file():
                        return str(path)

    def install_packages(self):
        """
        Install xDEM and its dependencies in the dependencies folder
        """
        cmd = [
            self.python_exec(),
            "-um",
            "pip",
            "install",
            "--target",
            self.deps_dir,
            "--trusted-host",
            "pypi.org",
            "--trusted-host",
            "files.pythonhosted.org",
            ] + self.required_packages

        import subprocess
        subprocess.run(cmd)

    def check_version(self):
        if version("xdem") != self.required_xdem_version:
            self.log(f"Update to xDEM {self.required_xdem_version}")
            shutil.rmtree(self.deps_dir)
            self.run()

    def set_proj_db(self):
        """
        Search for and set proj database
        """
        for root, dirs, files in os.walk(self.deps_dir):
            if "rasterio" in root and "proj.db" in files:
                os.environ["PROJ_DATA"] = root
                break

    def run(self):
        """
        Check if xDEM is already installed, if not it proceed with the install
        """
        if not os.path.isdir(self.deps_dir):
            os.makedirs(self.deps_dir, exist_ok=True)
            self.install_packages()

        if self.deps_dir not in sys.path:
            sys.path.append(self.deps_dir)
            self.set_proj_db()

        return True

    def finished(self, result):
        if result and self.xdem_installed():
            self.check_version()
            self.load_plugin()
            self.log(f"xDEM {self.required_xdem_version} loaded successfully")
        else:
            self.log("xDEM installation failed",
                     level=Qgis.MessageLevel.Critical)
            shutil.rmtree(self.deps_dir)

    def load_plugin(self):
        from .xdem_provider import XdemProvider
        self.provider = XdemProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)
