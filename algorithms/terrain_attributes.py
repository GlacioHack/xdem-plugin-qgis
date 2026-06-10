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
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base_processing import XdemProcessingAlgorithm


class TerrainAttributes(XdemProcessingAlgorithm):
    """
    This class represents the base class from which all terrain attributes inherit.
    """

    def initAlgorithm(self, config=None):
        """
        - param DEM: The DEM on which the calculation will be performed.
        - param OUTPUT: The final results.
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(name="DEM", description="DEM")
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description=self.name()
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading the layer from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "DEM", context)

        # Extracting the path
        dem_path = dem_layer.dataProvider().dataSourceUri()

        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        dem = xdem.DEM(dem_path)
        self.get_dem_info(feedback, dem)

        # Calling the attribute get function with its parameters
        function_with_parameters = self.get_attribute_and_parameters(
            parameters, context
        )

        # Calculation and saving
        attribute = function_with_parameters(dem)
        attribute.to_file(output_path)

        return {"OUTPUT": output_path}

    def groupId(self):
        return "Terrain attributes"


class Slope(TerrainAttributes):
    def initAlgorithm(self, config=None):
        super().initAlgorithm()
        """.
        - param SURFACE_FIT: The surface fit to use.
        - param UNIT: The unit in degrees or radians.
        """
        parameter = QgsProcessingParameterEnum(
            name="SURFACE_FIT",
            description="Surface fit",
            options=["Florinsky", "Horn", "ZevenbergThorne"],
            defaultValue="Florinsky",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterEnum(
            name="UNIT",
            description="Unit",
            options=["Degrees", "Radians"],
            defaultValue="Degrees",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

    def get_attribute_and_parameters(self, parameters, context):
        """
        This function gets the advanced settings specific to slope and returns it with those specific settings.
        """
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        degrees = (
            True
            if self.parameterAsString(parameters, "UNIT", context) == "Degrees"
            else False
        )
        return lambda dem: dem.slope(surface_fit=surface_fit, degrees=degrees)

    def name(self):
        return "Slope"

    def createInstance(self):
        return Slope()


class Aspect(TerrainAttributes):
    def initAlgorithm(self, config=None):
        super().initAlgorithm()
        """
        - param SURFACE_FIT: The surface fit to use.
        - param UNIT: The unit in degrees or radians.
        """
        parameter = QgsProcessingParameterEnum(
            name="SURFACE_FIT",
            description="Surface fit",
            options=["Florinsky", "Horn", "ZevenbergThorne"],
            defaultValue="Florinsky",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterEnum(
            name="UNIT",
            description="Unit",
            options=["Degrees", "Radians"],
            defaultValue="Degrees",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        degrees = (
            True
            if self.parameterAsString(parameters, "UNIT", context) == "Degrees"
            else False
        )
        return lambda dem: dem.aspect(surface_fit=surface_fit, degrees=degrees)

    def name(self):
        return "Aspect"

    def createInstance(self):
        return Aspect()


class Hillshade(TerrainAttributes):
    def initAlgorithm(self, config=None):
        super().initAlgorithm()
        """
        - param SURFACE_FIT: The surface fit to use.
        - param ALTITUDE: The shading altitude in degrees.
        - param AZIMUTH: The shading azimuth in degrees.
        - param ZFACTOR: The vertical exaggeration factor.
        """
        parameter = QgsProcessingParameterEnum(
            name="SURFACE_FIT",
            description="Surface fit",
            options=["Florinsky", "Horn", "ZevenbergThorne"],
            defaultValue="Florinsky",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            name="ALTITUDE",
            description="Altitude",
            defaultValue=45,
            minValue=0,
            maxValue=90,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            name="AZIMUTH",
            description="Azimuth",
            defaultValue=315,
            minValue=0,
            maxValue=360,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            name="ZFACTOR", description="Z factor", defaultValue=1
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        altitude = self.parameterAsInt(parameters, "ALTITUDE", context)
        azimuth = self.parameterAsInt(parameters, "AZIMUTH", context)
        z_factor = self.parameterAsInt(parameters, "ZFACTOR", context)
        return lambda dem: dem.hillshade(
            surface_fit=surface_fit,
            azimuth=azimuth,
            altitude=altitude,
            z_factor=z_factor,
        )

    def name(self):
        return "Hillshade"

    def createInstance(self):
        return Hillshade()


class TopographicPositionIndex(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.topographic_position_index()

    def name(self):
        return "Topographic position index"

    def createInstance(self):
        return TopographicPositionIndex()


class TerrainRuggednessIndex(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.terrain_ruggedness_index()

    def name(self):
        return "Terrain ruggedness index"

    def createInstance(self):
        return TerrainRuggednessIndex()


class Roughness(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.roughness()

    def name(self):
        return "Roughness"

    def createInstance(self):
        return Roughness()


class Rugosity(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.rugosity()

    def name(self):
        return "Rugosity"

    def createInstance(self):
        return Rugosity()


class FractalRoughness(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.fractal_roughness()

    def name(self):
        return "Fractal roughness"

    def createInstance(self):
        return FractalRoughness()


class TextureShading(TerrainAttributes):
    def get_attribute_and_parameters(self, parameters, context):
        return lambda dem: dem.texture_shading()

    def name(self):
        return "Texture shading"

    def createInstance(self):
        return TextureShading()


class Curvature(TerrainAttributes):
    """
    This class represents the base class from which all curvature inherit.
    """

    def initAlgorithm(self, config=None):
        super().initAlgorithm()
        """
        - param SURFACE_FIT: The surface fit to use.
        - param CURV_METHOD: The method to use to calculate the curvature.
        """
        parameter = QgsProcessingParameterEnum(
            name="SURFACE_FIT",
            description="Surface fit",
            options=["Florinsky", "ZevenbergThorne"],
            defaultValue="Florinsky",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterEnum(
            name="CURV_METHOD",
            description="Method",
            options=["geometric", "directional"],
            defaultValue="geometric",
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)


class ProfileCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.profile_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Profile curvature"

    def createInstance(self):
        return ProfileCurvature()


class TangentialCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.tangential_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Tangential curvature"

    def createInstance(self):
        return TangentialCurvature()


class PlanformCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.planform_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Planform curvature"

    def createInstance(self):
        return PlanformCurvature()


class FlowlineCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.flowline_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Flowline curvature"

    def createInstance(self):
        return FlowlineCurvature()


class MaxCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.max_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Max curvature"

    def createInstance(self):
        return MaxCurvature()


class MinCurvature(Curvature):
    def get_attribute_and_parameters(self, parameters, context):
        surface_fit = self.parameterAsString(parameters, "SURFACE_FIT", context)
        curv_method = self.parameterAsString(parameters, "CURV_METHOD", context)
        return lambda dem: dem.min_curvature(
            surface_fit=surface_fit, curv_method=curv_method
        )

    def name(self):
        return "Min curvature"

    def createInstance(self):
        return MinCurvature()
