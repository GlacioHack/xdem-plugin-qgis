from qgis.core import Qgis
from .xdem_installer import XdemInstaller


def classFactory(iface):
    installer = XdemInstaller()
    if installer.install():
        iface.messageBar().pushMessage(
            "xDEM dependencies successfully loaded", level=Qgis.Info
        )
        from .xdem_plugin import XdemPlugin

        return XdemPlugin()
    else:
        iface.messageBar().pushMessage(
            "xDEM dependencies could not be loaded", level=Qgis.Critical
        )
