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
import processing
from qgis.core import QgsRasterLayer


def test_slope(ref_dem_layer, tmp_path):
    output_path = os.path.join(tmp_path, "test_slope.tif")

    result = processing.run(
        "XDEM:Slope",
        {
            "DEM": ref_dem_layer,
            "SURFACE_FIT": "Florinsky",
            "UNIT": "Degrees",
            "OUTPUT": output_path,
        },
    )
    output = QgsRasterLayer(result["OUTPUT"])

    assert output.isValid()


def test_coreg(tba_dem_layer, ref_dem_layer, tmp_path):
    output_path = os.path.join(tmp_path, "test_coreg.tif")

    result = processing.run(
        "XDEM:Coregistration",
        {
            "TBA_DEM": tba_dem_layer,
            "REF_DEM": ref_dem_layer,
            "MASK": None,
            "METHOD": "Nuth and Kääb (2011)",
            "BLOCKSIZE": None,
            "OUTPUT": output_path,
        },
    )
    output_layer = QgsRasterLayer(result["OUTPUT"])

    # Checks if layer can be open in qgis and if projection is correct
    assert output_layer.isValid()
    assert ref_dem_layer.crs() == output_layer.crs()
    assert ref_dem_layer.extent() == output_layer.extent()

    # Convert layers to numpy array for more accurate testing
    ref_dem_array = ref_dem_layer.as_numpy()
    tba_dem_array = tba_dem_layer.as_numpy()
    output_array = output_layer.as_numpy()

    # Absolute tolerance set on 40 due to a potential residual offset of 35.
    atol = 40.0

    # First, check if the tba dem does not pass the conditions
    assert not np.allclose(ref_dem_array, tba_dem_array, atol=atol)

    # Next, check if there has been an improvement
    assert np.allclose(ref_dem_array, output_array, atol=atol)
