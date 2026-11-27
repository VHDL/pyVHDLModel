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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""Tests for pyVHDLModel.IEEE.IeeeStdContext."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Name       import SelectedName, SimpleName
from pyVHDLModel.Symbol     import ContextReferenceSymbol, LibraryReferenceSymbol
from pyVHDLModel.DesignUnit import Context, ContextReference, LibraryClause, Package, UseClause
from pyVHDLModel.IEEE       import Ieee_Std_Context

from tests.unit.Visibility  import _constant, _design


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class IeeeStdContexts(Testcase):
	"""Context ``ieee.ieee_std_context`` (IEEE Std 1076-2008, 16.9)."""

	def test_ContextItems(self) -> None:
		"""``library IEEE;`` and the use clauses, in order, with the context as parent."""
		context = Ieee_Std_Context()

		self.assertIsInstance(context, Context)
		self.assertEqual("ieee_std_context", context.NormalizedIdentifier)
		self.assertIs(VHDLVersion.VHDL2008, context.VHDLVersion)
		self.assertIsInstance(context.ContextItems[0], LibraryClause)
		self.assertListEqual(
			["IEEE.STD_LOGIC_1164.all", "IEEE.NUMERIC_STD.all"],
			[str(item.Symbols[0].Name) for item in context.ContextItems[1:]]
		)
		for item in context.ContextItems:
			self.assertIs(context, item.Parent)

		for item in context.ContextItems[1:]:
			self.assertIsInstance(item, UseClause)

	def test_ContextReference(self) -> None:
		"""``library ieee; context ieee.ieee_std_context;`` makes ``unsigned`` of ``ieee.numeric_std`` visible."""
		constant = _constant("C", "unsigned")
		other =    _constant("V", "std_logic_vector")
		package =  Package(
			"p",
			[
				LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]),
				ContextReference([ContextReferenceSymbol(SelectedName("ieee_std_context", SimpleName("ieee")))])
			],
			declaredItems=[constant, other]
		)
		with WarningCollector() as collector:
			design = _design(package, analyze=False)
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee = design.Libraries["ieee"]
		self.assertIn("ieee_std_context", ieee.Contexts)
		self.assertIs(ieee.Packages["numeric_std"].Subtypes["unsigned"], constant.Subtype.Reference)
