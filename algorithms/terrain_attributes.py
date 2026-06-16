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


import xdem
from qgis.core import (
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base import XdemProcessingAlgorithm


class TerrainAttributes(XdemProcessingAlgorithm):
    def initAlgorithm(self, config=None):
        """
        Get all the parameters of an attribute and displays them in the QGIS UI
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="INPUT",
                description="DEM",
            )
        )

        self.func = self.func()

        self.add_specific_parameters(self.func)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT",
                description=self.name(),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        dem_layer = self.parameterAsRasterLayer(parameters, "INPUT", context)
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        dem = xdem.DEM(dem_layer.source())

        kwargs = self.get_kwargs(self.func, parameters, context)

        attribute_func = getattr(dem, self.func.__name__)
        attribute = attribute_func(**kwargs)

        attribute.to_file(output_path)

        return {"OUTPUT": output_path}

    def groupId(self):
        return "Terrain attributes"


class Slope(TerrainAttributes):
    def func(self):
        return xdem.DEM.slope

    def name(self):
        return "Slope"

    def createInstance(self):
        return Slope()


class Hillshade(TerrainAttributes):
    def func(self):
        return xdem.DEM.hillshade

    def name(self):
        return "Hillshade"

    def createInstance(self):
        return Hillshade()


class Aspect(TerrainAttributes):
    def func(self):
        return xdem.DEM.aspect

    def name(self):
        return "Aspect"

    def createInstance(self):
        return Aspect()


class TopographicPositionIndex(TerrainAttributes):
    def func(self):
        return xdem.DEM.topographic_position_index

    def name(self):
        return "Topographic position index"

    def createInstance(self):
        return TopographicPositionIndex()


class TerrainRuggednessIndex(TerrainAttributes):
    def func(self):
        return xdem.DEM.terrain_ruggedness_index

    def name(self):
        return "Terrain ruggedness index"

    def createInstance(self):
        return TerrainRuggednessIndex()


class Roughness(TerrainAttributes):
    def func(self):
        return xdem.DEM.roughness

    def name(self):
        return "Roughness"

    def createInstance(self):
        return Roughness()


class Rugosity(TerrainAttributes):
    def func(self):
        return xdem.DEM.rugosity

    def name(self):
        return "Rugosity"

    def createInstance(self):
        return Rugosity()


class FractalRoughness(TerrainAttributes):
    def func(self):
        return xdem.DEM.fractal_roughness

    def name(self):
        return "Fractal roughness"

    def createInstance(self):
        return FractalRoughness()


class TextureShading(TerrainAttributes):
    def func(self):
        return xdem.DEM.texture_shading

    def name(self):
        return "Texture shading"

    def createInstance(self):
        return TextureShading()


class TangentialCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.tangential_curvature

    def name(self):
        return "Tangential curvature"

    def createInstance(self):
        return TangentialCurvature()


class PlanformCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.planform_curvature

    def name(self):
        return "Planform curvature"

    def createInstance(self):
        return PlanformCurvature()


class ProfileCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.profile_curvature

    def name(self):
        return "Flowline curvature"

    def createInstance(self):
        return ProfileCurvature()


class FlowlineCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.flowline_curvature

    def name(self):
        return "Flowline curvature"

    def createInstance(self):
        return FlowlineCurvature()


class MaxCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.max_curvature

    def name(self):
        return "Max curvature"

    def createInstance(self):
        return MaxCurvature()


class MinCurvature(TerrainAttributes):
    def func(self):
        return xdem.DEM.min_curvature

    def name(self):
        return "Min curvature"

    def createInstance(self):
        return MinCurvature()
