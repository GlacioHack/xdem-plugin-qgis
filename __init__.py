def classFactory(iface):
    from .xdem_installer import xdem_package
    from .xdem_plugin import XdemPlugin

    return XdemPlugin()
