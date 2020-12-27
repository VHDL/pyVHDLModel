[![Sourcecode on GitHub](https://img.shields.io/badge/vhdl-pyVHDLModel-323131.svg?logo=github&longCache=true)](https://github.com/vhdl/pyVHDLModel)
[![License](https://img.shields.io/badge/code%20license-Apache%20License%2C%202.0-lightgrey?logo=GitHub)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/vhdl/pyVHDLModel?logo=GitHub&include_prereleases)](https://github.com/vhdl/pyVHDLModel/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/vhdl/pyVHDLModel?logo=GitHub&include_prereleases)](https://github.com/vhdl/pyVHDLModel/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/vhdl/pyVHDLModel?logo=GitHub&)](https://github.com/vhdl/pyVHDLModel/releases)
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyVHDLModel?logo=GitHub)](https://github.com/vhdl/pyVHDLModel/network/dependents)  
[![GitHub Workflow Build Status](https://img.shields.io/github/workflow/status/vhdl/pyVHDLModel/Test%20and%20Coverage?label=Build%20and%20Test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/vhdl/pyVHDLModel/actions?query=workflow%3A%22Test+and+Coverage%22)
[![Codacy - Quality](https://img.shields.io/codacy/grade/2286426d2b11417e90010427b7fed8e7?logo=Codacy)](https://www.codacy.com/manual/VHDL/pyVHDLModel)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/2286426d2b11417e90010427b7fed8e7?logo=Codacy)](https://www.codacy.com/manual/VHDL/pyVHDLModel)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/vhdl/pyVHDLModel?logo=Codecov)](https://codecov.io/gh/vhdl/pyVHDLModel)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyVHDLModel)](https://libraries.io/github/vhdl/pyVHDLModel/sourcerank)  
[![GitHub Workflow Release Status](https://img.shields.io/github/workflow/status/vhdl/pyVHDLModel/Release?label=Release&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/vhdl/pyVHDLModel/actions?query=workflow%3A%22Release%22)
[![PyPI](https://img.shields.io/pypi/v/pyVHDLModel?logo=PyPI&logoColor=FFFFFF)](https://pypi.org/project/pyVHDLModel/)
![PyPI - Status](https://img.shields.io/pypi/status/pyVHDLModel?logo=PyPI&logoColor=FFFFFF)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyVHDLModel?logo=PyPI&logoColor=FFFFFF)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyVHDLModel)](https://libraries.io/github/vhdl/pyVHDLModel)
[![Requires.io](https://img.shields.io/requires/github/VHDL/pyVHDLModel)](https://requires.io/github/VHDL/pyVHDLModel/requirements/?branch=main)  
[![Read the Docs](https://img.shields.io/github/workflow/status/vhdl/pyVHDLModel/Documentation?label=Documentation&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/vhdl/pyVHDLModel/actions?query=workflow%3A%22Documentation%22)

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
**pyVHDLModel Generators**
* High-level API for [GHDL's](https://github.com/ghdl/ghdl) `libghdl` offered via `pyghdl`.
* Code Document-Object-Model (Code-DOM) in [pyVHDLParser](https://github.com/Paebbels/pyVHDLParser).

**pyVHDLModel Consumers**
* Create graphical views of VHDL files or designs.  
	Possible candidates: [Symbolator](https://github.com/kevinpt/symbolator)
* Created a (re)formatted output of VHDL.


## License

This Python package (source code) is licensed under [Apache License 2.0](LICENSE.md).

<!-- The accompanying documentation is licensed under Creative Commons - Attribution-4.0 (CC-BY 4.0). -->

-------------------------
SPDX-License-Identifier: Apache-2.0
