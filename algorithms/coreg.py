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


import io
import os
from contextlib import redirect_stdout

import geoutils as gu
import xdem
from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from .base import XdemProcessingAlgorithm


class Coreg(XdemProcessingAlgorithm):
    def initAlgorithm(self, config=None):
        """
        Display parameters in the QGIS UI
        """
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
            QgsProcessingParameterRasterLayer(
                name="mask",
                description="Inlier mask",
                optional=True,
            )
        )

        # Blockwise only for coregistration
        if self.groupId() == "Coregistration":
            parameter = QgsProcessingParameterNumber(
                name="blocksize",
                description="blocksize",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=None,
            )
            self.advanced_param(parameter)

        self.coreg = self.coreg_class()

        # Generate parameters specific to each coreg init
        self.generate_parameters(self.coreg.__init__)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                name="output", description=(f"Output - {self.name()}")
            )
        )

    def coreg_info(self, feedback, coreg):
        """
        Capture the core.info output and display it in the log
        """
        metadata = io.StringIO()
        with redirect_stdout(metadata):
            coreg.info()
        feedback.pushInfo(metadata.getvalue())

    def processAlgorithm(self, parameters, context, feedback):
        tba_layer = self.parameterAsRasterLayer(parameters, "tba_dem", context)
        ref_layer = self.parameterAsRasterLayer(parameters, "ref_dem", context)
        inlier_mask_layer = self.parameterAsRasterLayer(parameters, "mask", context)
        block_size = self.parameterAsInt(parameters, "blocksize", context)
        output_path = self.parameterAsOutputLayer(parameters, "output", context)

        ref_dem = xdem.DEM(ref_layer.source())
        tba_dem = xdem.DEM(tba_layer.source())

        if inlier_mask_layer:
            inlier_mask = gu.Raster(inlier_mask_layer.source(), is_mask=True)
        else:
            inlier_mask = None

        # Get all the specific parameters entered in the UI
        kwargs = self.get_kwargs(self.coreg.__init__, parameters, context)

        # Instantiate coreg with these parameters
        coreg = self.coreg(**kwargs)

        if block_size:
            blockwise = xdem.coreg.BlockwiseCoreg(
                coreg,
                block_size_fit=block_size,
                block_size_apply=block_size,
                parent_path=os.path.dirname(output_path),
            )
            blockwise.fit(
                reference_elev=ref_dem,
                to_be_aligned_elev=tba_dem,
                inlier_mask=inlier_mask,
            )
            aligned_dem = blockwise.apply()

        else:
            coreg.fit(
                reference_elev=ref_dem,
                to_be_aligned_elev=tba_dem,
                inlier_mask=inlier_mask,
            )
            aligned_dem = coreg.apply(tba_dem)

        self.coreg_info(feedback, coreg)

        aligned_dem.to_file(output_path)

        return {"output": output_path}


# Coregistration
class CPDCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.CPD

    def name(self):
        return "Coherent point drift"

    def groupId(self):
        return "Coregistration"

    def createInstance(self):
        return CPDCoreg()


class ICPCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.ICP

    def name(self):
        return "Iterative closest point"

    def groupId(self):
        return "Coregistration"

    def shortHelpString(self):
        return "Iterative closest point (ICP) coregistration is an iterative point cloud registration method, it aims at iteratively minimizing the distance between closest neighbours by applying sequential rigid transformations."

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/coregistration.html#iterative-closest-point"

    def createInstance(self):
        return ICPCoreg()


class LZDCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.LZD

    def name(self):
        return "Least Z-difference"

    def groupId(self):
        return "Coregistration"

    def shortHelpString(self):
        return "Least Z-difference (LZD) coregistration is an iterative point-grid registration method from Rosenholm and Torlegård (1988)."

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/coregistration.html#least-z-difference"

    def createInstance(self):
        return LZDCoreg()


class DhMinimizeCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.DhMinimize

    def name(self):
        return "Minimization of DH"

    def groupId(self):
        return "Coregistration"

    def createInstance(self):
        return DhMinimizeCoreg()


class NuthKaabCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.NuthKaab

    def name(self):
        return "Nuth and Kääb (2011)"

    def groupId(self):
        return "Coregistration"

    def shortHelpString(self):
        return (
            "The Nuth and Kääb (2011) coregistration approach estimates a horizontal translation iteratively by solving a cosine equation between the terrain slope, aspect and the elevation differences. \n"
            "The iteration stops if it reaches the maximum number of iteration limit, or if the iterative shift amplitude falls below a specified tolerance."
        )

    def helpUrl(self):
        return "https://xdem.readthedocs.io/en/stable/coregistration.html#nuth-and-kaab-2011"

    def createInstance(self):
        return NuthKaabCoreg()


class VerticalShiftCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.VerticalShift

    def name(self):
        return "Vertical shift"

    def groupId(self):
        return "Coregistration"

    def createInstance(self):
        return VerticalShiftCoreg()


# Bias correction
class DerampCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.Deramp

    def name(self):
        return "Deramping"

    def groupId(self):
        return "Bias correction"

    def createInstance(self):
        return DerampCoreg()


class DirectionalBiasCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.DirectionalBias

    def name(self):
        return "Directional bias"

    def groupId(self):
        return "Bias correction"

    def createInstance(self):
        return DirectionalBiasCoreg()


class TerrainBiasCoreg(Coreg):
    def coreg_class(self):
        return xdem.coreg.TerrainBias

    def name(self):
        return "Terrain bias"

    def groupId(self):
        return "Bias correction"

    def createInstance(self):
        return TerrainBiasCoreg()
