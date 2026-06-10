# xDEM Plugin QGIS, Developer Guide
This guide provide the detailed documentation for developers.

## Project structure
```
xdem-plugin-qgis/
├── algorithms/
│   ├── base_processing.py
│   ├── corrections.py
│   ├── terrain_attributes.py
│   ├── uncertainty.py
│   ├── workflows.py
├── doc/
│   ├──dev_guide.md
├── img/
│   ├──xdem_logo.svg
├── tests/
│   ├── conftest.py
│   ├── test_processing.py
├── .gitignore
├── README.md
├── __init__.py
├── metadata.txt
├── xdem_installer.py
├── xdem_plugin.py
└── xdem_provider.py
```

## Developement environment
For developers, use `git clone` for installation, here are the steps: 
1. Locate the `plugins` directory where QGIS stores its installed plugins, corresponding to your current profile.
    - Go to `Settings` > `User profiles` > `Open active profile folder`, from there, go to `python` > `plugins`.
2. Use `git clone https://github.com/GlacioHack/xdem-plugin-qgis.git` to install the xDEM plugin in this folder.
3. Restart QGIS.
4. Open the plugins menu and check the box to enable xDEM.

It will take a few minutes for the dependencies to install properly, do not force QGIS to close.

A plugin that will be very helpful during development is [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/). By default, when changes are made to the plugin code, QGIS must be restarted. This extension allows plugins to be refreshed without closing the software.

## Tests
The tests need to be run directly from QGIS, pytest is included in the libraries installed with the plugin.

To run the tests, go to the console, import pytest and run the following command by specifying the plugin directory.
```python
import pytest

pytest.main(["plugin_directory/tests", "-v"])
```
The tests will run just like a standard pytest execution, with progress updates and a final summary.

## Process algorithms
Processing methods are divided into four categories, it's all in the `algorithms` folder.
- **corrections**
- **terrain attributes**
- **uncertainty**
- **workflows**

Before getting into the logic behind xDEM processing, it is important to understand how QGIS process algorithms works.

Every processing must inherit from the class `QgsProcessingAlgorithm`, it is the main processing class. The two most important methods are:
1. `initAlgorithm()` this method initialize the GUI, it explicitly specifies which parameters need to be entered for the algorithm to work.
2. `processAlgorithm()` this method retrieves the parameters provided by the user and runs the process.

The xdem algorithms follow this logic. Here is a simplified version of a slope processing:
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
        dem_path = dem_layer.dataProvider().dataSourceUri()

        # Convert to a DEM object
        dem = xdem.DEM(dem_path)

        # Compute the slope
        slope = dem.slope()

        # Saving it
        slope.to_file(output_path)

        # Return the result in QGIS
        return {"OUTPUT": output_path}
```
