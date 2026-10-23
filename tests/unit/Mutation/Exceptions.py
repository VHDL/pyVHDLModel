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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Tests for the class hierarchy of the errors raised by the mutators.
"""
from pyTooling.Exceptions  import AlreadyInHierarchyError, DuplicateElementError
from pyTooling.Testing     import Testcase

from pyVHDLModel.Exception import VHDLModelException, AlreadyInDesignError, NotAChildError, DuplicateGenericError
from pyVHDLModel.Exception import DuplicatePortError, DuplicateParameterError, DuplicateDeclarationError
from pyVHDLModel.Exception import DuplicateTypeError, DuplicateSubtypeError, DuplicateConstantError
from pyVHDLModel.Exception import DuplicateSignalError, DuplicateVariableError, DuplicateFileError
from pyVHDLModel.Exception import DuplicateComponentError, DuplicateSubprogramError
from pyVHDLModel.Exception import NotInNamespaceError, DuplicateDocumentError, DuplicateDesignUnitError
from pyVHDLModel.Exception import ElementInUseError, LibraryInUseError


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Exceptions(Testcase):
	def test_AlreadyInDesignError(self) -> None:
		self.assertTrue(issubclass(AlreadyInDesignError, VHDLModelException))
		self.assertTrue(issubclass(AlreadyInDesignError, AlreadyInHierarchyError))

	def test_NotAChildError(self) -> None:
		self.assertTrue(issubclass(NotAChildError, VHDLModelException))

	def test_DuplicateGenericError(self) -> None:
		self.assertTrue(issubclass(DuplicateGenericError, VHDLModelException))
		self.assertTrue(issubclass(DuplicateGenericError, DuplicateElementError))

	def test_DuplicatePortError(self) -> None:
		self.assertTrue(issubclass(DuplicatePortError, VHDLModelException))
		self.assertTrue(issubclass(DuplicatePortError, DuplicateElementError))

	def test_DuplicateParameterError(self) -> None:
		self.assertTrue(issubclass(DuplicateParameterError, VHDLModelException))
		self.assertTrue(issubclass(DuplicateParameterError, DuplicateElementError))

	def test_NotInNamespaceError(self) -> None:
		self.assertTrue(issubclass(NotInNamespaceError, VHDLModelException))
		self.assertTrue(issubclass(NotInNamespaceError, KeyError))

	def test_NotInNamespaceError_Message(self) -> None:
		"""The message isn't quoted like a :exc:`KeyError`'s."""
		ex = NotInNamespaceError("Namespace 'rtl' has no element 'bits'.")

		self.assertEqual("Namespace 'rtl' has no element 'bits'.", str(ex))

	def test_DuplicateDeclarationError(self) -> None:
		self.assertTrue(issubclass(DuplicateDeclarationError, VHDLModelException))
		self.assertTrue(issubclass(DuplicateDeclarationError, DuplicateElementError))

	def test_DuplicateDeclarationError_Kinds(self) -> None:
		self.assertTrue(issubclass(DuplicateTypeError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateSubtypeError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateConstantError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateSignalError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateVariableError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateFileError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateComponentError, DuplicateDeclarationError))
		self.assertTrue(issubclass(DuplicateSubprogramError, DuplicateDeclarationError))

	def test_DuplicateDocumentError(self) -> None:
		self.assertTrue(issubclass(DuplicateDocumentError, VHDLModelException))
		self.assertTrue(issubclass(DuplicateDocumentError, DuplicateElementError))

	def test_DuplicateDesignUnitError(self) -> None:
		self.assertTrue(issubclass(DuplicateDesignUnitError, VHDLModelException))
		self.assertTrue(issubclass(DuplicateDesignUnitError, DuplicateElementError))

	def test_LibraryInUseError(self) -> None:
		self.assertTrue(issubclass(LibraryInUseError, VHDLModelException))
		self.assertTrue(issubclass(LibraryInUseError, ElementInUseError))
