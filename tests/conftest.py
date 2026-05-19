import os
import xdem
import pytest
from qgis.core import QgsRasterLayer


@pytest.fixture
def ref_dem_layer():
    ref_dem_path = xdem.examples.get_path(
        "longyearbyen_ref_dem", output_dir=os.path.dirname(__file__)
    )
    layer = QgsRasterLayer(ref_dem_path)
    return layer


@pytest.fixture
def tba_dem_layer():
    tba_dem_path = xdem.examples.get_path(
        "longyearbyen_tba_dem", output_dir=os.path.dirname(__file__)
    )
    layer = QgsRasterLayer(tba_dem_path)
    return layer
