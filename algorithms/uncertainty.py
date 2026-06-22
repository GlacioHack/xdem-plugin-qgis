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


import geoutils as gu
import xdem
from qgis.core import (
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base import XdemProcessingAlgorithm


class Heteroscedasticity(XdemProcessingAlgorithm):
    """
    This class is designed to model Heteroscedasticity using terrain slope and maximum curvature as explanatory variables,
    and with stable terrain as an error proxy for moving terrain.
    """

    def initAlgorithm(self, config=None):
        """
        - param AL_DEM: The aligned DEM.
        - param REF_DEM: The reference DEM.
        - param MASK: The mask corresponding to the stable terrain (0 for unstable, 1 for stable).
        - param OUTPUT: The the error map.
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="al_dem",
                description="Aligned DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="ref_dem",
                description="Reference DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="mask",
                description="Stable terrain mask",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="output",
                description="Map of variable error",
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        al_dem_layer = self.parameterAsRasterLayer(parameters, "al_dem", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "ref_dem", context)
        stable_terrain_layer = self.parameterAsRasterLayer(parameters, "mask", context)
        output_path = self.parameterAsOutputLayer(parameters, "output", context)

        aligned_dem = xdem.DEM(al_dem_layer.source())
        ref_dem = xdem.DEM(ref_dem_layer.source())

        # Creating a DEM difference object
        ddem = ref_dem - aligned_dem

        if stable_terrain_layer:
            stable_terrain = gu.Raster(stable_terrain_layer.source(), is_mask=True)
        else:
            stable_terrain = None

        # Run the pipeline with slope and max curvature
        slope, max_curvature = xdem.terrain.get_terrain_attribute(
            ref_dem, attribute=["slope", "max_curvature"]
        )
        error_map, df_binning, error_function = (
            xdem.spatialstats.infer_heteroscedasticity_from_stable(
                dvalues=ddem,
                list_var=[slope, max_curvature],
                list_var_names=["slope", "maxc"],
                stable_mask=stable_terrain,
            )
        )

        error_map.to_file(output_path)

        return {"output": output_path}

    def name(self):
        return "Heteroscedasticity"

    def groupId(self):
        return "Uncertainty"

    def shortHelpString(self):
        return (
            "Digital elevation models have a precision that can vary with terrain and instrument-related variables.\n"
            "Heteroscedasticity occurs when the variance of the errors is not constant across all values of the explanatory variables.\n"
            "This algorithm relies on a framework of non-stationary spatial statistics to estimate and model this variability in elevation error, "
            "using terrain slope and maximum curvature as explanatory variables, with stable terrain as an error proxy for moving terrain."
        )

    def createInstance(self):
        return Heteroscedasticity()
