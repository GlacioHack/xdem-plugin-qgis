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


import shutil


def classFactory(iface):

    # Initialization, verification of the installation before starting the plugin

    from .xdem_installer import XdemInstaller

    installer = XdemInstaller()

    if installer.run():
        from .xdem_plugin import XdemPlugin

        return XdemPlugin()

    else:
        shutil.rmtree(installer.deps_dir)

        return None
