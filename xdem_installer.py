import importlib
import os
import shutil
import subprocess
import sys


class XdemInstaller:
    """
    The xdem python installer.
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
        Get the major and minor python version.
        """

        version = [sys.version_info.major, sys.version_info.minor]

        return version

    def exist_in_qgis(self, package):
        """
        Check if a specified package exist in qgis.
        """

        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False

    def install_packages(self):
        for package in self.required_packages:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    self.libs_folder,
                    package,
                ]
            )

    def clean_shared_packages(self):
        """
        Clean the libs folder by removing the packages already present in qgis.
        """

        for xdem_package in os.listdir(self.libs_folder):
            for shared_package in self.shared_packages:
                if self.exist_in_qgis(shared_package):
                    if xdem_package.startswith(shared_package):
                        target_package = os.path.join(self.libs_folder, xdem_package)
                        shutil.rmtree(target_package)

    def run(self) -> bool:
        """
        Check if xdem is already installed, if not it proceed with the install.
        """

        if not self.exist_in_qgis("xdem"):
            if not self.get_python_version() >= [3, 10]:
                raise Exception(
                    "Unable to install xdem, python version lower than 3.10."
                )

            if not os.path.isdir(self.libs_folder):
                os.makedirs(self.libs_folder, exist_ok=True)
                self.install_packages()
                self.clean_shared_packages()

            if self.libs_folder not in sys.path:
                sys.path.insert(0, self.libs_folder)

            if not self.exist_in_qgis("xdem"):
                shutil.rmtree(self.libs_folder)
                return False
        return True
