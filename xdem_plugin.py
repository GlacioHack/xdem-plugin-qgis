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


import os
import sys
import importlib
import shutil
import platform

from pathlib import Path
from qgis.core import QgsApplication, Qgis, QgsMessageLog


class XdemPlugin():
    """
    Startup class for the plugin,
    used for initializing the QGIS environment,
    when xDEM is installed correctly, it starts the provider
    """

    def __init__(self, iface):
        self.installer = None
        self.provider = None
        self.iface = iface
        self.python_path = self.get_python_path()
        self.plugin_dir = os.path.dirname(__file__)
        self.deps_dir = os.path.join(self.plugin_dir, "xdem_dependencies")

        metadata_file = os.path.join(self.plugin_dir, "metadata.txt")
        with open(metadata_file, "r") as f:
            for line in f:
                if line.startswith("version="):
                    self.xdem_version = line.split("=")[1][0:5]

    def initGui(self):
        self.initProcessing()

    def initProcessing(self):
        # Python version check
        if sys.version_info < (3, 10):
            self.log("Python version lower than 3.10",
                     level=Qgis.MessageLevel.Critical)
            self.unload()
            return

        if not os.path.isdir(self.deps_dir):
            self.iface.messageBar().pushMessage(
                "xDEM installation in progress", level=Qgis.Info)

            from .xdem_installer import XdemInstaller

            self.installer = XdemInstaller(target_dir=self.deps_dir,
                                           python_path=self.python_path,
                                           xdem_version=self.xdem_version)

            self.installer.taskCompleted.connect(self.install_complete)
            self.installer.taskTerminated.connect(self.install_failled)

            QgsApplication.taskManager().addTask(self.installer)

        else:
            self.install_complete()

    def install_complete(self):
        sys.path.append(self.deps_dir)
        self.set_proj_db()
        if self.xdem_installed():
            self.load()
        else:
            self.install_failled()

    def install_failled(self):
        self.log("Installation failed", level=Qgis.MessageLevel.Critical)
        shutil.rmtree(self.deps_dir)
        self.unload()

    def load(self):
        from .xdem_provider import XdemProvider
        self.provider = XdemProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)
        self.log(f"xDEM {self.xdem_version} successfully loaded")

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def log(self, message, level=Qgis.MessageLevel.Info):
        """
        Displays information in the QGIS console, in the xDEM section
        """
        QgsMessageLog.logMessage(message, "xDEM", level)

    def xdem_installed(self):
        return importlib.util.find_spec("xdem") is not None

    def set_proj_db(self):
        """
        Search for and set geoutils proj database
        """
        for root, dirs, files in os.walk(self.deps_dir):
            if "rasterio" in root and "proj.db" in files:
                os.environ["PROJ_DATA"] = root
                break

    def get_python_path(self):
        """
        Return the path of the Python executable
        """
        system = platform.system()

        # Linux
        if system == "Linux":
            return sys.executable

        # Windows
        elif system == "Windows":
            base_path = Path(sys.prefix)
            for name in ("python.exe", "python3.exe"):
                path = base_path / name
                if path.is_file():
                    return str(path)

        # MacOS
        elif system == "Darwin":
            base_paths = [
                Path(sys.prefix),
                Path(sys.prefix) / "bin",
                Path(sys.executable).parent,
            ]
            for base_path in base_paths:
                for name in ("python", "python3"):
                    path = base_path / name
                    if path.is_file():
                        return str(path)
