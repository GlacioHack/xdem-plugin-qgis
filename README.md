# xDEM Plugin QGIS
This plugin allows you to perform processing on Digital Elevation Models (DEMs), it is based on the xDEM Python package. It is developed in collaboration between CNES (the French space agency) and Glacio Hack (a group of glaciology researchers).

## Installation
For now, the plugin hasn't been released on QGIS, but you can already install it, here are the installation steps:
1. Locate the `plugins` directory where QGIS stores its installed plugins, corresponding to your current profile.
    - Go to `Settings` > `User profiles` > `Open active profile folder` > `python` > `plugins`.
2. Use `git clone https://github.com/GlacioHack/xdem-plugin-qgis.git` to install the plugin in this folder.
3. Restart QGIS.
4. Open the plugins menu and check the box to enable xDEM.

It will take a few minutes for the dependencies to install properly, do not force QGIS to close.

Once installation is complete, xDEM will appear in the processing toolbox.

## Available processing
All the algorithms can be accessed through the QGIS Processing Toolbox in `xDEM`, they are organized into four sections.
- **Bias corrections**: For correction methods designed to correct both systematic elevation errors and spatially structured random errors.
- **Coregistration**: For affine transformations, these can include vertical and horizontal translations, rotations and scalings.
- **Terrain attributes**: To calculate derivatives of DEMs, such as curvatures.
- **Uncertainty**: To visualise potential errors resulting from corrections.
- **Workflows**: To run full pipelines and generate detailed reports.

## Documentation
- [xDEM](https://xdem.readthedocs.io/en/stable/index.html)
- [Developer guide](doc/dev_guide.md)
