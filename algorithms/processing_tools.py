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

    def load_mask(self, parameters, context, feedback):
        inlier_mask_layer = self.parameterAsRasterLayer(parameters, "MASK", context)
        if inlier_mask_layer is not None:
            inlier_mask_path = inlier_mask_layer.dataProvider().dataSourceUri()
            inlier_mask = gu.Raster(inlier_mask_path, is_mask=True)
            feedback.pushInfo("Mask loaded")
            return inlier_mask
        else:
            return None
