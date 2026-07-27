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


import xdem
from qgis.core import (
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base import XdemProcessingAlgorithm


class TerrainAttributes(XdemProcessingAlgorithm):
    def initAlgorithm(self, config=None):
        """
        Display parameters in the QGIS UI
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="dem",
                description="DEM",
            )
        )

        self.dem_func = self.func()

        # Generate parameters specific to each attribute
        self.generate_parameters(self.dem_func)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="output",
                description=self.name(),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        dem_layer = self.parameterAsRasterLayer(parameters, "dem", context)
        output_path = self.parameterAsOutputLayer(parameters, "output",
                                                  context)

        dem = xdem.DEM(dem_layer.source())

        # Get all the specific parameters entered in the UI
        kwargs = self.get_kwargs(self.dem_func, parameters, context)

        # Instantiate attribute with these parameters
        attribute = self.dem_func(dem, **kwargs)

        attribute.to_file(output_path)

        return {"output": output_path}

    def groupId(self):
        return "Terrain attributes"

    def shortHelpString(self):
        return self.func().__doc__


class Slope(TerrainAttributes):
    def func(self):
        return xdem.DEM.slope

    def name(self):
        return "Slope"

    def createInstance(self):
        return Slope()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#slope"


class Hillshade(TerrainAttributes):
    def func(self):
        return xdem.DEM.hillshade

    def name(self):
        return "Hillshade"

    def createInstance(self):
        return Hillshade()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#hillshade"


class Aspect(TerrainAttributes):
    def func(self):
        return xdem.DEM.aspect

    def name(self):
        return "Aspect"

    def createInstance(self):
        return Aspect()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#aspect"


class TopographicPositionIndex(TerrainAttributes):
    def func(self):
        return xdem.DEM.topographic_position_index

    def name(self):
        return "Topographic position index"

    def createInstance(self):
        return TopographicPositionIndex()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#topographic-position-index" # noqa


class TerrainRuggednessIndex(TerrainAttributes):
    def func(self):
        return xdem.DEM.terrain_ruggedness_index

    def name(self):
        return "Terrain ruggedness index"

    def createInstance(self):
        return TerrainRuggednessIndex()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#terrain-ruggedness-index" # noqa


class Roughness(TerrainAttributes):
    def func(self):
        return xdem.DEM.roughness

    def name(self):
        return "Roughness"

    def createInstance(self):
        return Roughness()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#roughness"


class Rugosity(TerrainAttributes):
    def func(self):
        return xdem.DEM.rugosity

    def name(self):
        return "Rugosity"

    def createInstance(self):
        return Rugosity()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#rugosity"


class FractalRoughness(TerrainAttributes):
    def func(self):
        return xdem.DEM.fractal_roughness

    def name(self):
        return "Fractal roughness"

    def createInstance(self):
        return FractalRoughness()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#fractal-roughness" # noqa


class TextureShading(TerrainAttributes):
    def func(self):
        return xdem.DEM.texture_shading

    def name(self):
        return "Texture shading"

    def createInstance(self):
        return TextureShading()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#texture-shading" # noqa


class TangentialCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.tangential_curvature

    def name(self):
        return "Tangential curvature"

    def createInstance(self):
        return TangentialCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#tangential-curvature" # noqa


class PlanformCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.planform_curvature

    def name(self):
        return "Planform curvature"

    def createInstance(self):
        return PlanformCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#planform-curvature" # noqa


class ProfileCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.profile_curvature

    def name(self):
        return "Profile curvature"

    def createInstance(self):
        return ProfileCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#profile-curvature" # noqa


class FlowlineCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.flowline_curvature

    def name(self):
        return "Flowline curvature"

    def createInstance(self):
        return FlowlineCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#flowline-curvature" # noqa


class MaxCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.max_curvature

    def name(self):
        return "Max curvature"

    def createInstance(self):
        return MaxCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#maximal-maximum-curvature" # noqa


class MinCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.min_curvature

    def name(self):
        return "Min curvature"

    def createInstance(self):
        return MinCurvature()

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/terrain.html#minimal-minimum-curvature" # noqa
