import os
import sys
import shutil
import importlib
from pip._internal.cli.main import main as pip_main
from qgis.core import Qgis
from qgis.utils import iface

# Path Configuration
PLUGIN_DIR = os.path.dirname(__file__)
LIBS_FOLDER_NAME = "xdem_libs"
LIBS_DIR = os.path.join(PLUGIN_DIR, LIBS_FOLDER_NAME)

# Packages Configuration
REQUIRED_PACKAGES = [
    "cerberus",
    "matplotlib",
    "pytest",
    "scikit-learn",
    "weasyprint",
    "xdem",
]
SHARED_PACKAGES = ["geopandas", "numpy", "pandas", "pyproj", "rasterio", "shapely"]


def exist_in_qgis(package):
    """
    Function that checks if a package is present in QGIS by attempting to import it.
    """

    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False


def clean_shared_packages():
    """
    Function that removes shared packages if they exist in QGIS.
    """

    for xdem_package in os.listdir(LIBS_DIR):
        for shared_package in SHARED_PACKAGES:
            if exist_in_qgis(shared_package):
                if xdem_package == shared_package or xdem_package.startswith(
                    shared_package
                ):
                    target_package = os.path.join(LIBS_DIR, xdem_package)
                    shutil.rmtree(target_package)


def install_package():
    """
    Function that installs packages in the plugin directory.
    """

    for package in REQUIRED_PACKAGES:
        pip_main(["install", "--target", LIBS_DIR, package])
    iface.messageBar().pushMessage(
        "xDEM dependencies successfully installed", level=Qgis.Info
    )


def check_xdem():
    """
    Function that checks if xdem is present, if not, it proceeds with the installation.
    """

    try:
        import xdem

        return xdem
    except ImportError:
        pass

    if not os.path.isdir(LIBS_DIR):
        os.makedirs(LIBS_DIR, exist_ok=True)
        install_package()

    clean_shared_packages()

    if LIBS_DIR not in sys.path:
        sys.path.insert(0, LIBS_DIR)

    try:
        import xdem

        return xdem
    except ImportError:
        iface.messageBar().pushMessage(
            "xDEM dependencies could not be installed", level=Qgis.Critical
        )
        shutil.rmtree(LIBS_DIR)
        return None


# xDEM install variable
xdem_package = check_xdem()
