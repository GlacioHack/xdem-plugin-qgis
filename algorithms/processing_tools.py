import io
import geoutils as gu
from contextlib import redirect_stdout
from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication


# Generic functions


def dem_info(dem, feedback, stats: bool = False) -> None:
    """
    This function displays information and statistics about a DEM in the QGIS console.
    """

    metadata = io.StringIO()
    with redirect_stdout(metadata):
        dem.info(stats=stats)
    feedback.pushInfo(metadata.getvalue())


def coreg_info(coreg, feedback) -> None:
    """
    This function displays information about a Coreg in the QGIS console.
    """

    metadata = io.StringIO()
    with redirect_stdout(metadata):
        coreg.info()
    feedback.pushInfo(metadata.getvalue())


def load_mask(self, parameters, context, feedback) -> gu.Raster:
    """
    This function allows to load a mask (e.g., a TIF file) and return a gu.Raster object.
    """

    try:
        inlier_mask_layer = self.parameterAsLayer(parameters, "MASK", context)
        inlier_mask_path = inlier_mask_layer.dataProvider().dataSourceUri()
        inlier_mask = gu.Raster(inlier_mask_path, is_mask=True)
        feedback.pushInfo("Mask loaded")
        return inlier_mask
    except:
        feedback.pushWarning("Mask not provided")
        return None


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
