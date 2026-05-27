# Copyright (c) 2026 xDEM developers
#
# This file is part of the xDEM project:
# https://github.com/glaciohack/xdem
# https://github.com/GlacioHack/xdem-plugin-qgis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from qgis.core import QgsProcessingProvider

from .algorithms.corrections import *
from .algorithms.terrain_attributes import *
from .algorithms.uncertainty import *
from .algorithms.workflows import *


class XdemProvider(QgsProcessingProvider):
    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):  # Displayed in QGIS in alphabetical order
        # Corrections
        self.addAlgorithm(BiasCorrection())
        self.addAlgorithm(Coregistration())
        self.addAlgorithm(GapFilling())

        # Terrain attributes
        self.addAlgorithm(Aspect())
        self.addAlgorithm(FlowlineCurvature())
        self.addAlgorithm(FractalRoughness())
        self.addAlgorithm(GetTerrainAttributes())
        self.addAlgorithm(Hillshade())
        self.addAlgorithm(MaxCurvature())
        self.addAlgorithm(MinCurvature())
        self.addAlgorithm(PlanformCurvature())
        self.addAlgorithm(ProfileCurvature())
        self.addAlgorithm(Roughness())
        self.addAlgorithm(Rugosity())
        self.addAlgorithm(Slope())
        self.addAlgorithm(TangentialCurvature())
        self.addAlgorithm(TerrainRuggednessIndex())
        self.addAlgorithm(TextureShading())
        self.addAlgorithm(TopographicPositionIndex())

        # Uncertainty
        self.addAlgorithm(Heteroscedasticity())

        # Workflows
        self.addAlgorithm(AccuracyWorkflow())
        self.addAlgorithm(TopoWorkflow())

    def id(self):
        return "XDEM"

    def name(self):
        return self.tr("xDEM")

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def longName(self):
        return self.name()
