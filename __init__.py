# Initialisation script


def classFactory(iface):
    from .xdem_installer import XdemInstaller

    installer = XdemInstaller()

    if installer.run():
        from .xdem_plugin import XdemPlugin

        return XdemPlugin()

    else:
        raise Exception(
            "Unable to load the plugin, please check the logs, section 'xDEM'"
        )
