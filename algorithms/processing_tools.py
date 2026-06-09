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

import io
from contextlib import redirect_stdout

import geoutils as gu
from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication


# Main processing class
class XdemProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This class represents the base class from which all xDEM algorithms inherit.
    """

    def flags(self):
        # Multithreading is disabled to prevent memory conflicts
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def get_dem_info(self, feedback, dem):
        """
        Returns information about the DEM in the logs
        """
        metadata = io.StringIO()
        with redirect_stdout(metadata):
            dem.info()
        feedback.pushInfo(metadata.getvalue())

    def get_coreg_info(self, feedback, coreg):
        """
        Returns information about corrections in the logs
        """
        metadata = io.StringIO()
        with redirect_stdout(metadata):
            coreg.info()
        feedback.pushInfo(metadata.getvalue())

    def load_mask(self, parameters, context, feedback):
        """
        Returns a gu.Raster mask layer if one is provided
        """
        inlier_mask_layer = self.parameterAsRasterLayer(parameters, "MASK", context)
        if inlier_mask_layer is not None:
            inlier_mask_path = inlier_mask_layer.dataProvider().dataSourceUri()
            inlier_mask = gu.Raster(inlier_mask_path, is_mask=True)
            feedback.pushInfo("Mask loaded")
            return inlier_mask
        else:
            return None
