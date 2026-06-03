# xDEM Plugin QGIS
This plugin allows you to perform processing on Digital Elevation Models (DEMs), it is based on the xDEM Python package. A package developed in collaboration between CNES (the French space agency) and Glacio Hack (a group of glaciology researchers).

## Installation
For now, download the .zip from github, here are the installation steps:
1. In QGIS go to `Plugins` > `Manage and Install Plugins...` > `Install from ZIP`
2. Select the downloaded file
3. Click on `Install Plugin`

It will take a few minutes for the dependencies to install properly, do not force QGIS to close.

## Available processing
All the algorithms can be accessed through the QGIS Processing Toolbox in `xDEM`, they are organized into four sections.
- **Corrections**: For coregistration, bias corrections and gap filling.
- **Terrain attributes**: To calculate derivatives of DEMs, such as curvatures.
- **Uncertainty**: To visualise potential errors resulting from corrections.
- **Workflows**: To run full pipelines and generate detailed reports.

## Documentation
- [xDEM](https://xdem.readthedocs.io/en/stable/index.html)
- [Developer guide](doc/dev_guide.md)
