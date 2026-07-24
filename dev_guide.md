# xDEM Plugin QGIS, Developer Guide
This guide provide the detailed documentation for developers.

## Project structure
```
xdem-plugin-qgis/
├── algorithms/
│   ├── base.py
│   ├── coreg.py
│   ├── terrain_attributes.py
│   ├── uncertainty.py
│   ├── workflows.py
├── img/
│   ├── xdem_logo.svg
├── tests/
│   ├── conftest.py
│   ├── test_processing.py
├── LICENSE
├── README.md
├── dev_guide.md
├── __init__.py
├── metadata.txt
├── xdem_installer.py
├── xdem_plugin.py
└── xdem_provider.py
```

## Developement environment
For Linux developers, it is recommended to use the stable [Flatpak](https://qgis.org/resources/installation-guide/#flatpak) version of QGIS instead of the apt version. This is a sandbox version that isolates QGIS and prevents interaction with the system's Python, avoiding version conflicts. You'll also need to make sure that pip is up to date, to do this, run this command in the QGIS Python console:

```python
import subprocess
subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"])
```

Once these prerequisites are met, you can proceed with the installation.

Use `git clone` for installation, here are the steps: 
1. Start QGIS and locate the `plugins` directory, corresponding to your current profile.
    - Go to `Settings` > `User profiles` > `Open active profile folder` > `python` > `plugins`.
2. Use `git clone https://github.com/GlacioHack/xdem-plugin-qgis.git` to install the xDEM plugin in this folder.
3. Restart QGIS.
4. Open the plugins menu and check the box to enable xDEM.

It will take a few minutes for the dependencies to install properly, do not force QGIS to close. The installation logs can be accessed via the menu bar in the `Log Message Panel`. There is a dedicated `xDEM` section, which displays the version loaded at startup and any potential installation errors.

A plugin that will be very helpful during development is [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/). By default, when changes are made to the plugin code, QGIS must be restarted. This extension allows plugins to be refreshed without closing the software.

## Version
The plugin version consists of four digits, the first three represent the compatible xDEM version, and the last digit represents the plugin version.
For example, if the plugin is version `0.2.3.1`, it works with xDEM `0.2.3`. To ensure compatibility, a version check is performed at each QGIS startup.

## Tests
The tests need to be run directly from QGIS, pytest is included in the libraries installed with the plugin.

To run the tests, go to the console, import pytest and run the following command by specifying the plugin directory.
```python
import pytest
pytest.main(["plugin_directory/tests", "-v"])
```
The tests will run just like a standard pytest execution, with progress updates and a final summary.

Currently, there are 3 tests:
- Terrain attributes
- Coregistration
- Workflows

These tests verify that the algorithms execute correctly and that their outputs are valid for QGIS.

## Process algorithms
Processing methods are divided into five categories, it's all in the `algorithms` folder.
- **Bias corrections**: For correction methods designed to correct both systematic elevation errors and spatially structured random errors.
- **Coregistration**: For affine transformations, these can include vertical and horizontal translations, rotations and scalings.
- **Terrain attributes**: To calculate derivatives of DEMs, such as curvatures.
- **Uncertainty**: To visualise potential errors resulting from corrections.
- **Workflows**: To run full pipelines and generate detailed reports.

Before getting into the logic behind xDEM processing, it is important to understand how QGIS process algorithms works.

Every processing must inherit from the class `QgsProcessingAlgorithm`, it is the main processing class. The two most important methods are:
1. `initAlgorithm()` this method initialize the GUI, it explicitly specifies which parameters need to be entered for the algorithm to work.
2. `processAlgorithm()` this method retrieves the parameters provided by the user and runs the process.

The xdem algorithms follow this logic. Here is a simplified version of the slope processing pipeline:
```python
class Slope(QgsProcessingAlgorithm):
    def initAlgorithm()
        # Input DEM
        self.addParameter(QgsProcessingParameterRasterLayer(name="INPUT", description="Dem"))

        # Output Slope
        self.addParameter(QgsProcessingParameterRasterDestination(name="OUTPUT", description="Slope"))

    def processAlgorithm(parameters)
        # Loading the layer from QGIS
        dem_layer = self.parameterAsRasterLayer(parameters, "INPUT")

        # Getting the slope output directory
        output_path = self.parameterAsOutputLayer(parameters, "OUTPUT")

        # Extracting the layer path
        dem_path = dem_layer.source()

        # Convert to a DEM object
        dem = xdem.DEM(dem_path)

        # Compute the slope
        slope = dem.slope()

        # Saving it
        slope.to_file(output_path)

        # Return the result in QGIS
        return {"OUTPUT": output_path}
```
