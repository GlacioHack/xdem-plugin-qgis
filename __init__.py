# Initialisation script
from qgis.core import Qgis


def classFactory(iface):
    from .xdem_installer import XdemInstaller

    installer = XdemInstaller()

    if installer.run():
        iface.messageBar().pushMessage("xDEM loaded", level=Qgis.Info)

        from .xdem_plugin import XdemPlugin

        return XdemPlugin()
