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

import pytest
import xdem
from qgis.core import QgsRasterLayer


@pytest.fixture
def ref_dem_layer():
    ref_dem_path = xdem.examples.get_path("longyearbyen_ref_dem")
    layer = QgsRasterLayer(ref_dem_path)
    return layer


@pytest.fixture
def tba_dem_layer():
    tba_dem_path = xdem.examples.get_path("longyearbyen_tba_dem")
    layer = QgsRasterLayer(tba_dem_path)
    return layer
