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


import os

import numpy as np
import pytest
import xdem
from qgis.core import QgsRasterLayer


@pytest.fixture
def ref_dem_layer():
    ref_dem_path = xdem.examples.get_path("longyearbyen_ref_dem")
    layer = QgsRasterLayer(ref_dem_path)
    return layer


@pytest.fixture
def tba_dem_layer(tmp_path):
    ref_dem = xdem.DEM(xdem.examples.get_path("longyearbyen_ref_dem"))

    x_shift = 30
    y_shift = 30
    z_shift = 10

    matrix = np.array(
        [
            [1, 0, 0, x_shift],
            [0, 1, 0, y_shift],
            [0, 0, 1, z_shift],
            [0, 0, 0, 1],
        ]
    )

    # Applying the offset to the DEM
    tba_dem = xdem.coreg.apply_matrix(ref_dem, matrix)

    # Save the file because QgsRasterLayer take a path as input
    tba_dem_path = os.path.join(tmp_path, "tba_dem.tif")
    tba_dem.to_file(tba_dem_path)

    layer = QgsRasterLayer(tba_dem_path)
    return layer
