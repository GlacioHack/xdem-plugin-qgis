import os
import xdem
from qgis.utils import iface
from qgis.core import (
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterFolderDestination,
)
from xdem.terrain import available_attributes
from .processing_tools import XdemProcessingAlgorithm, dem_info


class TerrainAttributes(XdemProcessingAlgorithm):
    """
    This class represents the base class from which all terrain attributes inherit.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param DEM: The DEM on which the calculation will be performed.
        :param OUTPUT: The final results.
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

        # Display DEM informations in the QGIS console
        feedback.pushInfo("DEM informations:")
        dem_info(dem, feedback)

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
        """
        Call to the parent class, with the addition of parameters specific to Slope.
        :param SURFACE_FIT: The surface fit to use.
        :param UNIT: The unit in degrees or radians.
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
        Call to the parent class, with the addition of parameters specific to Aspect.
        :param SURFACE_FIT: The surface fit to use.
        :param UNIT: The unit in degrees or radians.
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
        Call to the parent class, with the addition of parameters specific to Hillshade.
        :param SURFACE_FIT: The surface fit to use.
        :param ALTITUDE: The shading altitude in degrees.
        :param AZIMUTH: The shading azimuth in degrees.
        :param ZFACTOR: The vertical exaggeration factor.
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


class Curvature(TerrainAttributes):
    """
    This class represents the base class from which all curvature inherit.
    """

    def initAlgorithm(self, config=None):
        super().initAlgorithm()
        """
        Call to the parent class, with the addition of parameters specific to Curvature, .
        :param SURFACE_FIT: The surface fit to use.
        :param CURV_METHOD: The method to use to calculate the curvature.
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


class GetTerrainAttributes(XdemProcessingAlgorithm):
    """
    This class enables the simultaneous calculation of a wide range of terrain attributes.
    """

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(name="DEM", description="DEM")
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="ATTRIBUTES",
                description="Attributes",
                options=available_attributes,
                defaultValue=["slope", "aspect", "hillshade", "profile_curvature"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name="OUTPUT", description="Attributes folder"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading the layer from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "DEM", context)

        # Loading attributes list
        attributes_list = self.parameterAsEnumStrings(parameters, "ATTRIBUTES", context)

        # Extracting the path
        dem_path = dem_layer.dataProvider().dataSourceUri()

        dem = xdem.DEM(dem_path)

        # Display DEM informations in the QGIS console
        feedback.pushInfo("DEM informations:")
        dem_info(dem, feedback)

        output_folder = self.parameterAsString(parameters, "OUTPUT", context)
        os.makedirs(output_folder, exist_ok=True)

        attributes = dem.get_terrain_attribute(attribute=attributes_list)

        if len(attributes_list) == 1:
            attributes = [attributes]

        for name, res in zip(attributes_list, attributes):
            output = os.path.join(output_folder, f"{name}.tif")
            res.to_file(output)

        for file in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file)
            if file_path.endswith(".tif"):
                iface.addRasterLayer(file_path)

        return {}

    def name(self):
        return "Get terrain attributes"

    def groupId(self):
        return "Terrain attributes"

    def createInstance(self):
        return GetTerrainAttributes()
