# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |                                                    #
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |                                                    #
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |                                                    #
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|                                                    #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
This module contains an abstract document language model for PSL in VHDL.
"""
from pyTooling.Decorators import export

from pyVHDLModel.Base import ModelEntity, NamedEntityMixin
from pyVHDLModel.DesignUnit import PrimaryUnit


@export
class PSLEntity(ModelEntity):
	pass


@export
class PSLPrimaryUnit(PrimaryUnit):
	pass


@export
class VerificationUnit(PSLPrimaryUnit):
	def __init__(self, identifier: str):
		super().__init__(identifier)


@export
class VerificationProperty(PSLPrimaryUnit):
	def __init__(self, identifier: str):
		super().__init__(identifier)


@export
class VerificationMode(PSLPrimaryUnit):
	def __init__(self, identifier: str):
		super().__init__(identifier)


@export
class DefaultClock(PSLEntity, NamedEntityMixin):

	def __init__(self, identifier: str):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
