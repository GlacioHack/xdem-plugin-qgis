from qgis.core import QgsApplication
from .xdem_provider import XdemProvider


class XdemPlugin(object):
    def __init__(self):
        self.provider = None

    def initProcessing(self):
        self.provider = XdemProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
