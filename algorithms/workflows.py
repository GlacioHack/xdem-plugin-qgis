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
import webbrowser

import plutoprint
from qgis.core import (
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterRasterLayer,
)
from qgis.utils import iface
from xdem.workflows import Accuracy, Topo
from xdem.workflows.schemas import COREG_METHODS, STATS_METHODS, TERRAIN_ATTRIBUTES

from .base import XdemProcessingAlgorithm

COREG_METHODS = COREG_METHODS[:-1]  # Squeeze the last value (None)


def add_layers_to_project(output_folder):
    """
    Add the workflow output layers to the current project
    """
    rasters_folder = os.path.join(output_folder, "rasters")
    for file in os.listdir(rasters_folder):
        file_path = os.path.join(rasters_folder, file)
        iface.addRasterLayer(file_path)


def generate_pdf(output_folder):
    """
    Generate the pdf from the html
    """
    book = plutoprint.Book(plutoprint.PAGE_SIZE_A4)
    book.load_url(os.path.join(output_folder, "report.html"))
    book.write_to_pdf(os.path.join(output_folder, "report.pdf"))


def open_pdf_in_browser(output_folder):
    """
    Open the pdf in the browser
    """
    path = os.path.join(output_folder, "report.pdf")
    webbrowser.open(f"file://{path}")


class AccuracyWorkflow(XdemProcessingAlgorithm):
    """
    This class is designed to perform an accuracy assessment of an elevation dataset
    """

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="tba_dem",
                description="To be aligned DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="ref_dem",
                description="Reference DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="stats",
                description="Statistics",
                options=STATS_METHODS,
                defaultValue=["min", "max", "mean", "median", "nmad"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="level",
                description="Level for detailed outputs",
                options=["1", "2"],
                defaultValue="1",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                name="add_layers",
                description="Add layers to project",
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                name="open_pdf",
                description="Open PDF report",
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="method1",
                description="Method - 1",
                options=COREG_METHODS,
                defaultValue="NuthKaab",
                usesStaticStrings=True,
            )
        )

        parameter = QgsProcessingParameterEnum(
            name="method2",
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
            name="method3",
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
                name="output", description="Output folder"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "tba_dem", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "ref_dem", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.source()
        ref_dem_path = ref_dem_layer.source()

        stats = self.parameterAsEnumStrings(parameters, "stats", context)
        level = self.parameterAsInt(parameters, "level", context)
        add_layers = self.parameterAsBoolean(parameters, "add_layers", context)
        open_pdf = self.parameterAsBoolean(parameters, "open_pdf", context)
        method1 = self.parameterAsString(parameters, "method1", context)
        method2 = self.parameterAsString(parameters, "method2", context)
        method3 = self.parameterAsString(parameters, "method3", context)

        output_folder = self.parameterAsString(parameters, "output", context)
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
                "path": output_folder,
            },
            "coregistration": {
                "step_one": {"method": method1},
                "step_two": {"method": method2 if method2 else None},
                "step_three": {"method": method3 if method3 else None},
            },
            "statistics": stats,
        }

        workflow = Accuracy(config)
        workflow.run()

        generate_pdf(output_folder)

        if add_layers:
            add_layers_to_project(output_folder)

        if open_pdf:
            open_pdf_in_browser(output_folder)

        return {}

    def name(self):
        return "Accuracy"

    def groupId(self):
        return "Workflows"

    def tags(self):
        return COREG_METHODS

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/cli_accuracy.html"

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
    This class is designed to perform a topographical summary of an elevation dataset
    """

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="dem",
                description="DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="attributes",
                description="Terrain attributes",
                options=TERRAIN_ATTRIBUTES,
                defaultValue=["slope", "aspect", "hillshade", "profile_curvature"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="stats",
                description="Statistics",
                options=STATS_METHODS,
                defaultValue=["min", "max", "mean", "median", "nmad"],
                allowMultiple=True,
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="level",
                description="Level for detailed outputs",
                options=["1", "2"],
                defaultValue="2",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                name="add_layers",
                description="Add layers to project",
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                name="open_pdf",
                description="Open PDF report",
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name="output", description="Output folder"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "dem", context)

        # Extracting paths
        dem_path = dem_layer.source()

        attributes = self.parameterAsEnumStrings(parameters, "attributes", context)
        stats = self.parameterAsEnumStrings(parameters, "stats", context)
        level = self.parameterAsInt(parameters, "level", context)
        add_layers = self.parameterAsBoolean(parameters, "add_layers", context)
        open_pdf = self.parameterAsBoolean(parameters, "open_pdf", context)

        output_folder = self.parameterAsString(parameters, "output", context)
        os.makedirs(output_folder, exist_ok=True)

        # Configuration setup
        config = {
            "inputs": {
                "reference_elev": {
                    "path_to_elev": dem_path,
                    "downsample": 1,
                },
            },
            "outputs": {"level": level, "path": output_folder},
            "statistics": stats,
            "terrain_attributes": attributes,
        }

        workflow = Topo(config)
        workflow.run()

        generate_pdf(output_folder)

        if add_layers:
            add_layers_to_project(output_folder)

        if open_pdf:
            open_pdf_in_browser(output_folder)

        return {}

    def name(self):
        return "Topography"

    def groupId(self):
        return "Workflows"

    def tags(self):
        return TERRAIN_ATTRIBUTES

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/cli_topo.html"

    def shortHelpString(self):
        return (
            "The topo workflow performs a topographical summary of an elevation dataset.\n"
            "This summary derives a series of terrain attributes (e.g. slope, hillshade, aspect, etc.) "
            "with statistics (e.g. mean, max, min, etc.).\n"
            "Two output levels are available, Level 1 corresponds to the basic version, while Level 2 allows you to save rasters and statistics."
        )

    def createInstance(self):
        return TopoWorkflow()
