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
Shared helpers for the tests of the VHDL writer (:mod:`pyVHDLModel.Formatting.VHDL`).

GHDL serves as oracle: written VHDL source text must pass ``ghdl -a --std=08``.
"""
from pathlib    import Path
from shutil     import which
from subprocess import CompletedProcess, run as subprocess_run
from tempfile   import TemporaryDirectory

from pyVHDLModel.Name   import SimpleName
from pyVHDLModel.Symbol import SimpleObjectOrFunctionCallSymbol


_GHDL = which("ghdl")  #: Path to the GHDL executable, or ``None`` if GHDL is not on PATH.


def _object(name: str) -> SimpleObjectOrFunctionCallSymbol:
	"""Reference to an object (or a parameterless function call) by a simple name, as used in expressions."""
	return SimpleObjectOrFunctionCallSymbol(SimpleName(name))


def _analyze(source: str) -> CompletedProcess:
	"""Analyze VHDL source text with GHDL (VHDL-2008) in a temporary directory."""
	with TemporaryDirectory() as directory:
		path = Path(directory) / "oracle.vhdl"
		path.write_text(source, encoding="latin-1")
		return subprocess_run(
			[_GHDL, "-a", "--std=08", f"--workdir={directory}", str(path)],
			capture_output=True,
			text=True,
			cwd=directory
		)
