[![Sourcecode on GitHub](https://img.shields.io/badge/vhdl-pyVHDLModel-323131.svg?logo=github&longCache=true)](https://github.com/vhdl/pyVHDLModel)
[![License](https://img.shields.io/badge/code%20license-Apache%20License%2C%202.0-lightgrey?logo=GitHub)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/vhdl/pyVHDLModel?logo=GitHub&include_prereleases)](https://github.com/vhdl/pyVHDLModel/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/vhdl/pyVHDLModel?logo=GitHub&include_prereleases)](https://github.com/vhdl/pyVHDLModel/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/vhdl/pyVHDLModel?logo=GitHub&)](https://github.com/vhdl/pyVHDLModel/releases)  
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/vhdl/pyVHDLModel/Test,%20Coverage%20and%20Release?label=Workflow&logo=GitHub)](https://github.com/vhdl/pyVHDLModel/actions?query=workflow%3A%22Test%2C+Coverage+and+Release%22)
[![PyPI](https://img.shields.io/pypi/v/pyVHDLModel?logo=PyPI)](https://pypi.org/project/pyVHDLModel/)
![PyPI - Status](https://img.shields.io/pypi/status/pyVHDLModel?logo=PyPI)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyVHDLModel?logo=PyPI)
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyVHDLModel)](https://github.com/vhdl/pyVHDLModel/network/dependents)  
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyVHDLModel)](https://libraries.io/github/vhdl/pyVHDLModel)
[![Requires.io](https://img.shields.io/requires/github/vhdl/pyVHDLModel)](https://requires.io/github/vhdl/pyVHDLModel/requirements/?branch=master)  
[![Codacy - Quality](https://img.shields.io/codacy/grade/2286426d2b11417e90010427b7fed8e7?logo=Codacy)](https://www.codacy.com/manual/vhdl/pyVHDLModel)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/2286426d2b11417e90010427b7fed8e7?logo=Codacy)](https://www.codacy.com/manual/vhdl/pyVHDLModel)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/vhdl/pyVHDLModel?logo=Codecov)](https://codecov.io/gh/vhdl/pyVHDLModel)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyVHDLModel)](https://libraries.io/github/vhdl/pyVHDLModel/sourcerank)  
[![Read the Docs](https://img.shields.io/readthedocs/pyvhdlmodel)](https://pyVHDLModel.readthedocs.io/en/latest/)

# pyVHDLModel

An abstract VHDL language model written in Python.

## Main Goals
This package provides a unified abstract language model for VHDL. Projects reading
from source files can derive own classes and implement additional logic to create
a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can
build higher level features and services on such a model, while supporting multiple
frontends.


## Use Cases
* High-level API for GHDL's `libghdl` offered via `pyghdl`.
* Code Document-Object-Model (Code-DOM) in `pyVHDLParser`.




## License

This Python package (source code) is licensed under [Apache License 2.0](LICENSE.md).

<!-- The accompanying documentation is licensed under Creative Commons - Attribution-4.0 (CC-BY 4.0). -->

-------------------------
SPDX-License-Identifier: Apache-2.0
