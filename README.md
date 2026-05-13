# xDEM Plugin QGIS
This plugin allows you to perform processing on Digital Elevation Models (DEMs), it is based on the xDEM Python package. A package developed in collaboration between CNES (the French space agency) and Glacio Hack (a group of glaciology researchers).

## Installation
For now, use `git clone` for installation, here are the steps:
1. Locate the `plugins` directory where QGIS stores its installed plugins, corresponding to your current profile.
    - Go to `Settings` > `User profiles` > `Open active profile folder`, from there, go to `python` > `plugins`.
2. Use `git clone https://github.com/GlacioHack/xdem-plugin-qgis.git` to install the xDEM plugin in this folder.
3. Restart QGIS.
4. Open the plugins menu and check the box to enable xDEM.

It will take a few minutes for the dependencies to install properly, do not force QGIS to close. A message confirming successful installation should appear.

## Available processing
All the algorithms can be accessed through the QGIS Processing Toolbox in `xDEM`, they are organized into four sections.
- **Corrections**: For coregistration, bias corrections and gap filling.
- **Terrain attributes**: To calculate derivatives of DEMs, such as curvatures.
- **Uncertainty**: To visualise potential errors resulting from corrections.
- **Workflows**: To run full pipelines and generate detailed reports.

## Documentation
- [xDEM package](https://xdem.readthedocs.io/en/stable/index.html)
- [Developer guide](doc/dev_guide.md)
