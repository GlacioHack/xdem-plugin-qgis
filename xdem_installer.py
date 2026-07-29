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
from pip._internal.cli.main import main as pip_main
from qgis.core import QgsTask


class XdemInstaller(QgsTask):
    """
    The xDEM python installer
    """

    def __init__(self, target_dir, xdem_version):
        super().__init__("xDEM Installation", QgsTask.CanCancel)

        self.target_dir = target_dir
        self.xdem_version = xdem_version

        self.required_packages = [
            "scipy<=1.17",  # scipy 1.18 needs numpy >= 2.0, QGIS runs numpy 1.26.4
            "plutoprint",
            "matplotlib",
            "pytest",
            "cairocffi",  # Matplotlib-specific backend
            "cerberus",
            "scikit-learn",
            f"xdem=={self.xdem_version}",
        ]

    def run(self):
        if not os.path.isdir(self.target_dir):
            os.makedirs(self.target_dir, exist_ok=True)

            cmd = [
                "install",
                "--target",
                self.target_dir,
                "--trusted-host",
                "pypi.org",
                "--trusted-host",
                "files.pythonhosted.org",
            ] + self.required_packages

            pip_main(cmd)

        return True
