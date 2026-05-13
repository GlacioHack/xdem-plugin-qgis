import os
from xdem.workflows import Accuracy, Topo
from xdem.workflows.schemas import STATS_METHODS, TERRAIN_ATTRIBUTES, COREG_METHODS
from qgis.utils import iface
from qgis.core import (
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFolderDestination,
)
from .processing_tools import XdemProcessingAlgorithm

COREG_METHODS = COREG_METHODS[:-1]  # Squeeze the last value (None)


def generate_pdf(workflow):
    from weasyprint import HTML

    HTML(workflow.outputs_folder / "report.html").write_pdf(
        workflow.outputs_folder / "report.pdf"
    )


class AccuracyWorkflow(XdemProcessingAlgorithm):
    """
    This class is designed to perform an accuracy assessment of an elevation dataset.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param TBA_DEM: The DEM requiring correction.
        :param REF_DEM: The reference DEM.
        :param STATS: The requested statistics.
        :param LEVEL: The level for detailed outputs.
        :param METHOD1: The (first) coreg method.
        :param METHOD2: If needed, a second method can be used to operate as a pipeline.
        :param METHOD3: If needed, a third method can be used to operate as a pipeline.
        :param OUTPUT: The results folder.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBA_DEM", description="DEM to be aligned"
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="REF_DEM", description="Reference DEM"
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="STATS",
                description="Statistics",
                options=STATS_METHODS,
                defaultValue=["min", "max", "mean", "median", "nmad"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="LEVEL",
                description="Level for detailed outputs",
                options=["1", "2"],
                defaultValue="2",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="METHOD1",
                description="Method - 1",
                options=COREG_METHODS,
                defaultValue="NuthKaab",
                usesStaticStrings=True,
            )
        )

        parameter = QgsProcessingParameterEnum(
            name="METHOD2",
            description="Method - 2",
            options=COREG_METHODS,
            optional=True,
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterEnum(
            name="METHOD3",
            description="Method - 3",
            options=COREG_METHODS,
            optional=True,
            usesStaticStrings=True,
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name="OUTPUT", description="Accuracy folder"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "TBA_DEM", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "REF_DEM", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.dataProvider().dataSourceUri()
        ref_dem_path = ref_dem_layer.dataProvider().dataSourceUri()

        stats = self.parameterAsEnumStrings(parameters, "STATS", context)
        level = self.parameterAsInt(parameters, "LEVEL", context)
        method1 = self.parameterAsString(parameters, "METHOD1", context)
        method2 = self.parameterAsString(parameters, "METHOD2", context)
        method3 = self.parameterAsString(parameters, "METHOD3", context)

        output_folder = self.parameterAsString(parameters, "OUTPUT", context)
        os.makedirs(output_folder, exist_ok=True)

        # Configuration setup
        config = {
            "inputs": {
                "reference_elev": {
                    "path_to_elev": ref_dem_path,
                },
                "to_be_aligned_elev": {
                    "path_to_elev": tba_dem_path,
                },
            },
            "outputs": {
                "level": level,
                "path": str(output_folder),
            },
            "coregistration": {
                "step_one": {"method": method1},
                "step_two": {"method": None if method2 == "" else method2},
                "step_three": {"method": None if method3 == "" else method3},
            },
            "statistics": stats,
        }

        workflow = Accuracy(config)
        workflow.run()
        generate_pdf(workflow)

        rasters_folder = os.path.join(output_folder, "rasters")
        for file in os.listdir(rasters_folder):
            file_path = os.path.join(rasters_folder, file)
            iface.addRasterLayer(file_path)

        return {}

    def name(self):
        return "Accuracy"

    def groupId(self):
        return "Workflows"

    def tags(self):
        return COREG_METHODS

    def shortHelpString(self):
        return (
            "The accuracy workflow performs an accuracy assessment of an elevation dataset.\n"
            "This assessment relies on analyzing the elevation differences to a secondary elevation dataset on static surfaces, "
            "as an error proxy to perform coregistration and bias-correction (systematic errors) and to perform uncertainty quantification (structured random errors).\n"
            "Two output levels are available, Level 1 corresponds to the basic version, while Level 2 allows you to save rasters and statistics."
        )

    def createInstance(self):
        return AccuracyWorkflow()


class TopoWorkflow(XdemProcessingAlgorithm):
    """
    This class is designed to perform a topographical summary of an elevation dataset.
    """

    def initAlgorithm(self, config=None):
        """
        Function to retrieve parameters entered in QGIS.
        :param DEM: The concerned DEM.
        :param ATTRIBUTES: The requested attributes
        :param STATS: The requested statistics.
        :param LEVEL: The level for detailed outputs.
        :param OUTPUT: The results folder.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(name="DEM", description="DEM")
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="ATTRIBUTES",
                description="Terrain attributes",
                options=TERRAIN_ATTRIBUTES,
                defaultValue=["slope", "aspect", "hillshade", "profile_curvature"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="STATS",
                description="Statistics",
                options=STATS_METHODS,
                defaultValue=["min", "max", "mean", "median", "nmad"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="LEVEL",
                description="Level for detailed outputs",
                options=["1", "2"],
                defaultValue="2",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name="OUTPUT", description="Topography folder"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "DEM", context)

        # Extracting paths
        dem_path = dem_layer.dataProvider().dataSourceUri()

        attributes = self.parameterAsEnumStrings(parameters, "ATTRIBUTES", context)
        stats = self.parameterAsEnumStrings(parameters, "STATS", context)
        level = self.parameterAsInt(parameters, "LEVEL", context)

        output_folder = self.parameterAsString(parameters, "OUTPUT", context)
        os.makedirs(output_folder, exist_ok=True)

        # Configuration setup
        config = {
            "inputs": {
                "reference_elev": {
                    "path_to_elev": dem_path,
                    "force_source_nodata": None,
                    "from_vcrs": None,
                    "to_vcrs": None,
                    "path_to_mask": None,
                    "downsample": 1,
                },
            },
            "outputs": {"level": level, "path": str(output_folder)},
            "statistics": stats,
            "terrain_attributes": attributes,
        }

        workflow = Topo(config)
        workflow.run()
        generate_pdf(workflow)

        rasters_folder = os.path.join(output_folder, "rasters")
        for file in os.listdir(rasters_folder):
            file_path = os.path.join(rasters_folder, file)
            iface.addRasterLayer(file_path)

        return {}

    def name(self):
        return "Topography"

    def groupId(self):
        return "Workflows"

    def tags(self):
        return TERRAIN_ATTRIBUTES

    def shortHelpString(self):
        return (
            "The topo workflow performs a topographical summary of an elevation dataset.\n"
            "This summary derives a series of terrain attributes (e.g. slope, hillshade, aspect, etc.) "
            "with statistics (e.g. mean, max, min, etc.).\n"
            "Two output levels are available, Level 1 corresponds to the basic version, while Level 2 allows you to save rasters and statistics."
        )

    def createInstance(self):
        return TopoWorkflow()
