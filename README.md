# xDEM Plugin QGIS
This plugin allows you to perform processing on Digital Elevation Models (DEMs), it is based on the [xDEM](https://github.com/GlacioHack/xdem/tree/main) Python package. It is developed in collaboration between CNES (the French space agency) and Glacio Hack (a group of glaciology researchers).

## Installation
The plugin is available on the official QGIS portal, here are the installation steps:
1. In QGIS go to `Plugins` > `Manage and Install Plugins...` > `Not installed`.
2. Search for xDEM.
3. Click on `Install Plugin`.

If you need a specific version, you may download it directly from the [QGIS website](https://plugins.qgis.org/plugins/).
1. Search for xDEM.
2. Download the ZIP file corresponding to the desired version.
3. In QGIS, go to `Plugins` > `Manage and Install Plugins...` > `Install plugin from zip`.

It will take a few minutes for the dependencies to install properly, do not force QGIS to close.

Once installation is complete, xDEM will appear in the processing toolbox.

## Available processing
All the algorithms can be accessed through the QGIS Processing Toolbox in `xDEM`, they are organized into five sections.
- **Bias corrections**: For correction methods designed to correct both systematic elevation errors and spatially structured random errors.
- **Coregistration**: For affine transformations, these can include vertical and horizontal translations, rotations and scalings.
- **Terrain attributes**: To calculate derivatives of DEMs, such as curvatures.
- **Uncertainty**: To visualise potential errors resulting from corrections.
- **Workflows**: To run full pipelines and generate detailed reports.

## Documentation
- [xDEM](https://xdem.readthedocs.io/en/stable/index.html)
- [Developer guide](dev_guide.md)

## Autors
The original contribution was created by Antoine Ould [ould-a](https://github.com/ould-a),
the [xDEM developers](https://github.com/GlacioHack/xdem/blob/main/AUTHORS.md) also contributed to the development of the plugin.