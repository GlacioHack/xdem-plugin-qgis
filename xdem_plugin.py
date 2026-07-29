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
from qgis.core import QgsApplication, QgsTask, Qgis, QgsMessageLog


class XdemPlugin():
    def __init__(self):
        self.installer = None
        self.provider = None
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
            self.log("Python version lower than 3.10")
            return

        from .xdem_installer import XdemInstaller
        self.installer = XdemInstaller(target_dir=self.deps_dir, xdem_version=self.xdem_version)

        self.installer.taskCompleted.connect(self.load)
        self.installer.taskTerminated.connect(self.unload)

        QgsApplication.taskManager().addTask(self.installer)

    def load(self):
        sys.path.append(self.deps_dir)
        self.set_proj_db()
        if self.xdem_installed():
            self.log(f"xDEM {self.xdem_version} successfully loaded")
            from .xdem_provider import XdemProvider
            self.provider = XdemProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
        else:
            self.log("Unable to import xDEM after installation", level=Qgis.MessageLevel.Critical)
            self.unload()

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
