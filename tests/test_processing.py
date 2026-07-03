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

import numpy as np
import processing
from qgis.core import QgsRasterLayer


def check_layer(ref_layer, output_layer):
    """
    Check if the output layer can be open in qgis and if projecttion is valid
    """
    assert output_layer.isValid()
    assert ref_layer.crs() == output_layer.crs()
    assert ref_layer.extent() == output_layer.extent()


def test_terrain_attribute(ref_dem_layer, tmp_path):
    output_path = os.path.join(tmp_path, "test_terrain_attribute.tif")

    result = processing.run(
        "XDEM:Slope",
        {
            "dem": ref_dem_layer,
            "surface_fit": 0,
            "degrees": True,
            "output": output_path,
        },
    )
    output_layer = QgsRasterLayer(result["output"])

    check_layer(ref_dem_layer, output_layer)


def test_coreg(tba_dem_layer, ref_dem_layer, tmp_path):
    output_path = os.path.join(tmp_path, "test_coreg.tif")

    result = processing.run(
        "XDEM:Nuth and Kääb (2011)",
        {
            "tba_dem": tba_dem_layer,
            "ref_dem": ref_dem_layer,
            "mask": None,
            "blocksize": 0,
            "max_iterations": 10,
            "offset_threshold": 0.001,
            "bin_before_fit": True,
            "vertical_shift": True,
            "output": output_path,
        },
    )
    output_layer = QgsRasterLayer(result["output"])

    check_layer(ref_dem_layer, output_layer)

    # Convert layers to numpy array for more accurate testing
    ref_dem_array = ref_dem_layer.as_numpy()
    tba_dem_array = tba_dem_layer.as_numpy()
    output_array = output_layer.as_numpy()

    # Absolute tolerance set on one pixel
    tol = ref_dem_layer.rasterUnitsPerPixelX()

    # First, check if the tba dem does not pass the conditions
    assert not np.allclose(ref_dem_array, tba_dem_array, atol=tol)

    # Next, check if there has been an improvement
    assert np.allclose(ref_dem_array, output_array, atol=tol)


def test_workflow(ref_dem_layer, tmp_path):
    output_folder = os.path.join(tmp_path, "test_workflow")

    attributes = ["slope", "aspect", "hillshade", "profile_curvature"]

    processing.run(
        "XDEM:Topography",
        {
            "dem": ref_dem_layer,
            "attributes": attributes,
            "stats": ["min", "max", "mean", "median", "nmad"],
            "level": "2",
            "add_layers": False,
            "output": output_folder,
        },
    )
    # Check if html was generated
    output_files = os.listdir(output_folder)
    assert "report.html" in output_files

    # Check if all raster where generated
    raster_folder = os.path.join(output_folder, "rasters")

    assert len(attributes) == len(os.listdir(raster_folder))

    for raster in os.listdir(raster_folder):
        raster_path = os.path.join(raster_folder, raster)
        raster_layer = QgsRasterLayer(raster_path)
        check_layer(ref_dem_layer, raster_layer)
