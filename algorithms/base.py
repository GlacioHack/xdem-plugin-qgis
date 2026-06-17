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

import inspect
import os
from typing import Literal, get_args, get_origin, get_type_hints

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon


class XdemProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This class represents the base class from which all xDEM algorithms inherit.
    """

    def flags(self):
        # Multithreading is disabled to prevent memory conflicts
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def displayName(self):
        return self.tr(self.name())

    def group(self):
        return self.tr(self.groupId())

    def icon(self):
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(plugin_dir, "img", "xdem_algos_logo.png")
        return QIcon(icon_path)

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def add_advanced_param(self, parameter):
        """
        Specify in QGIS that this setting is located in the Advanced section
        """
        parameter.setFlags(
            parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(parameter)

    def add_specific_parameters(self, func):
        """
        Scans the specified function and adds the parameters to QGIS based on their type.
        """
        # Function signature
        function_signature = inspect.signature(func)

        # Dict of the each param type
        parameter_types_dict = get_type_hints(func)

        for name, param in function_signature.parameters.items():
            # Get the type corresponding to the name
            param_type = parameter_types_dict.get(name)

            if name == "method":  # Deprecated
                continue

            elif param_type is bool:
                parameter = QgsProcessingParameterBoolean(
                    name=name,
                    description=name,
                    defaultValue=param.default,
                )
                self.add_advanced_param(parameter)

            elif param_type is int:
                parameter = QgsProcessingParameterNumber(
                    name=name,
                    description=name,
                    type=QgsProcessingParameterNumber.Integer,
                    defaultValue=param.default,
                )
                self.add_advanced_param(parameter)

            elif param_type is float:
                parameter = QgsProcessingParameterNumber(
                    name=name,
                    description=name,
                    type=QgsProcessingParameterNumber.Double,
                    defaultValue=param.default,
                )
                self.add_advanced_param(parameter)

            elif get_origin(param_type) is Literal:
                options = list(get_args(param_type))
                parameter = QgsProcessingParameterEnum(
                    name=name,
                    description=name,
                    options=options,
                    defaultValue=param.default,
                )
                self.add_advanced_param(parameter)

    def get_kwargs(self, func, parameters, context):
        """
        Scans the specified function and convert all arguments entered into QGIS.
        """
        # Function signature
        function_signature = inspect.signature(func)

        # Dict of the each param type
        parameter_types_dict = get_type_hints(func)

        # Parameters saved in a keyword arguments dict
        kwargs = {}

        for name, param in function_signature.parameters.items():
            # Get the type corresponding to the name
            param_type = parameter_types_dict.get(name, param.annotation)

            if name == "method":  # Deprecated
                continue

            if param_type is bool:
                kwargs[name] = self.parameterAsBoolean(parameters, name, context)

            elif param_type is int:
                kwargs[name] = self.parameterAsInt(parameters, name, context)

            elif param_type is float:
                kwargs[name] = self.parameterAsDouble(parameters, name, context)

            elif get_origin(param_type) is Literal:
                options = list(get_args(param_type))
                index = self.parameterAsEnum(parameters, name, context)
                kwargs[name] = options[index]

        return kwargs
