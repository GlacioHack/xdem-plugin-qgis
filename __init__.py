from .xdem_installer import XdemInstaller


def classFactory(iface):
    installer = XdemInstaller()

    if installer.run():
        from .xdem_plugin import XdemPlugin

        return XdemPlugin()
    else:
        raise Exception("Unable to install xdem")
