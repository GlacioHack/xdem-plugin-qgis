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

import xdem
from qgis.core import (
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base import XdemProcessingAlgorithm


class BiasCorrection(XdemProcessingAlgorithm):
    """
    This class is designed to correct elevation errors using various bias correction methods.
    """

    def initAlgorithm(self, config=None):
        """
        - param TBA_DEM: The DEM requiring correction.
        - param REF_DEM: The reference DEM.
        - param MASK: An optional inlier mask used to define reliable data points (0 for outliers, 1 for inliers)
        - param METHOD: Specifies the bias correction method (e.g., "Deramping", "Directional biases").
        - param OUTPUT: The aligned DEM.
        """
        self.methods = {
            "Deramping": xdem.coreg.Deramp(),
            "Directional biases": xdem.coreg.DirectionalBias(),
            "Terrain biases": xdem.coreg.TerrainBias(),
        }

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBA_DEM",
                description="To be aligned DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="REF_DEM",
                description="Reference DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="MASK", description="Inlier mask", defaultValue=None, optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="METHOD",
                description="Method",
                options=self.methods,
                defaultValue="Deramping",
                usesStaticStrings=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description="Aligned DEM"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "TBA_DEM", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "REF_DEM", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.dataProvider().dataSourceUri()
        ref_dem_path = ref_dem_layer.dataProvider().dataSourceUri()

        method_name = self.parameterAsString(parameters, "METHOD", context)
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        tba_dem = xdem.DEM(tba_dem_path)
        ref_dem = xdem.DEM(ref_dem_path)
        inlier_mask = self.load_mask(parameters, context, feedback)

        # Loading the corresponding method
        coreg = self.methods[method_name]

        coreg.fit(ref_dem, tba_dem, inlier_mask)
        aligned_dem = coreg.apply(tba_dem)
        self.get_coreg_info(feedback, coreg)

        aligned_dem.to_file(output_path)

        return {"OUTPUT": output_path}

    def name(self):
        return "Bias correction"

    def groupId(self):
        return "Corrections"

    def tags(self):
        return self.methods

    def shortHelpString(self):
        return (
            "This algorithm aim at correcting both systematic elevation errors and spatially-structured random errors.\n"
            "Bias-correction methods correspond to transformations that cannot be described as a 3D affine transformations."
        )

    def createInstance(self):
        return BiasCorrection()


class Coregistration(XdemProcessingAlgorithm):
    """
    This class is designed to correct elevation errors using affine coregistration methods.
    """

    def initAlgorithm(self, config=None):
        """
        - param TBA_DEM: The DEM requiring correction.
        - param REF_DEM: The reference DEM.
        - param MASK: An optional inlier mask used to define reliable data points (0 for outliers, 1 for inliers)
        - param METHOD: Specifies the coregistration method (e.g., "Nuth and Kääb (2011)", "Iterative closest point").
        - param BLOCKSIZE: Block size for blockwise execution.
        - param OUTPUT: The aligned DEM.
        """
        self.methods = {
            "Nuth and Kääb (2011)": xdem.coreg.NuthKaab(),
            "Minimization of dh": xdem.coreg.DhMinimize(),
            "Least Z-difference": xdem.coreg.LZD(),
            "Iterative closest point": xdem.coreg.ICP(),
            "Coherent point drift": xdem.coreg.CPD(),
            "Vertical shift": xdem.coreg.VerticalShift(),
        }

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="TBA_DEM",
                description="To be aligned DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="REF_DEM",
                description="Reference DEM",
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name="MASK", description="Inlier mask", defaultValue=None, optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name="METHOD",
                description="Method",
                options=self.methods,
                defaultValue="Nuth and Kääb (2011)",
                usesStaticStrings=True,
            )
        )

        parameter = QgsProcessingParameterNumber(
            name="BLOCKSIZE", description="Blocksize", optional=True
        )
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="OUTPUT", description="Aligned DEM"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loading layers from QGIS
        tba_dem_layer = self.parameterAsRasterLayer(parameters, "TBA_DEM", context)
        ref_dem_layer = self.parameterAsRasterLayer(parameters, "REF_DEM", context)

        # Extracting paths
        tba_dem_path = tba_dem_layer.dataProvider().dataSourceUri()
        ref_dem_path = ref_dem_layer.dataProvider().dataSourceUri()

        method_name = self.parameterAsString(parameters, "METHOD", context)
        block_size = self.parameterAsInt(parameters, "BLOCKSIZE", context)
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT", context)

        tba_dem = xdem.DEM(tba_dem_path)
        ref_dem = xdem.DEM(ref_dem_path)
        inlier_mask = self.load_mask(parameters, context, feedback)

        coreg = self.methods[method_name]

        # Configuring blockwise
        if block_size != 0:
            feedback.pushWarning("Currently, Blockwise only works with Nuth Kaab")
            blockwise = xdem.coreg.BlockwiseCoreg(
                coreg,
                block_size_fit=block_size,
                block_size_apply=block_size,
                parent_path=os.path.dirname(__file__),
            )
            blockwise.fit(ref_dem, tba_dem, inlier_mask)
            aligned_dem = blockwise.apply()  # Note: In xdem 0.2.4 BlockwiseCoreg.apply() will take a tba_dem as input.
        else:
            coreg.fit(ref_dem, tba_dem, inlier_mask)
            aligned_dem = coreg.apply(tba_dem)

        self.get_coreg_info(feedback, coreg)

        aligned_dem.to_file(output_path)

        return {"OUTPUT": output_path}

    def name(self):
        return "Coregistration"

    def groupId(self):
        return "Corrections"

    def tags(self):
        return self.methods

    def shortHelpString(self):
        return (
            "This algorithm enables the coregistration of two DEMs by applying 3D affine transformations.\n"
            "Affine transformations can include vertical and horizontal translations, rotations and reflections, and scalings."
        )

    def createInstance(self):
        return Coregistration()
