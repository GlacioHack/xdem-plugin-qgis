import importlib
import os
import shutil
import sys

from pip._internal.cli.main import main as pip_main


class XdemInstaller:
    """
    The xdem installer.
    It downloads the packages and places them in the plugin folder.
    Then it also manages the packages shared with QGIS.
    And finally, it adds the libs folder to the path.
    """

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.libs_folder = os.path.join(self.plugin_dir, "xdem_libs")

        self.required_packages = [
            "cerberus",
            "matplotlib",
            "pytest",
            "scikit-learn",
            "weasyprint",
            "xdem",
        ]

        self.shared_packages = [
            "geopandas",
            "numpy",
            "pandas",
            "pyproj",
            "rasterio",
            "shapely",
        ]

    def get_python_version(self):
        """
        This function return the major and minor python version.
        """

        major_version = sys.version_info.major
        minor_version = sys.version_info.minor

        version = [major_version, minor_version]

        return version

    def exist_in_qgis(self, package):
        """
        This function check if a specified package exist in qgis.
        """

        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False

    def install_packages(self):
        for package in self.required_packages:
            pip_main(["install", "--target", self.libs_folder, package])

    def clean_shared_packages(self):
        """
        This function clean the libs folder by removing the packages already present in qgis.
        It avoids version conflicts.
        """

        for xdem_package in os.listdir(self.libs_folder):
            for shared_package in self.shared_packages:
                if self.exist_in_qgis(shared_package):
                    if xdem_package.startswith(shared_package):
                        target_package = os.path.join(self.libs_folder, xdem_package)
                        shutil.rmtree(target_package)

    def install(self):
        """
        This function check if xdem is already installed, if not it proceed with the install.
        """

        if self.exist_in_qgis("xdem"):
            return True
        else:
            if not self.get_python_version() >= [3, 10]:
                raise Exception(
                    "Python version lower than 3.10, unable to install xdem"
                )
            else:
                pass
            if not os.path.isdir(self.libs_folder):
                os.makedirs(self.libs_folder, exist_ok=True)
                self.install_packages()
                self.clean_shared_packages()

            if self.libs_folder not in sys.path:
                sys.path.insert(0, self.libs_folder)

            return self.exist_in_qgis("xdem")
