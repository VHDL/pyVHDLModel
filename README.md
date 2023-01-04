<p align="center">
  <a title="vhdl.github.io/pyVHDLModel" href="https://vhdl.github.io/pyVHDLModel"><img height="80px" src="doc/_static/logo.svg"/></a>
</p>

[![Sourcecode on GitHub](https://img.shields.io/badge/VHDL-pyVHDLModel-29b6f6.svg?longCache=true&style=flat-square&logo=GitHub&labelColor=0277bd)](https://github.com/vhdl/pyVHDLModel)
[![Sourcecode License](https://img.shields.io/pypi/l/pyVHDLModel?longCache=true&style=flat-square&logo=Apache&label=code)](LICENSE.md)
[![Documentation](https://img.shields.io/website?longCache=true&style=flat-square&label=vhdl.github.io%2FpyVHDLModel&logo=GitHub&logoColor=fff&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url=https%3A%2F%2Fvhdl.github.io%2FpyVHDLModel%2Findex.html)](https://vhdl.github.io/pyVHDLModel/)
[![Documentation License](https://img.shields.io/badge/doc-CC--BY%204.0-green?longCache=true&style=flat-square&logo=CreativeCommons&logoColor=fff)](LICENSE.md)
[![Gitter](https://img.shields.io/badge/chat-on%20gitter-4db797.svg?longCache=true&style=flat-square&logo=gitter&logoColor=e8ecef)](https://gitter.im/hdl/community)  
[![PyPI](https://img.shields.io/pypi/v/pyVHDLModel?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyVHDLModel/)
![PyPI - Status](https://img.shields.io/pypi/status/pyVHDLModel?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyVHDLModel?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/actions/workflow/status/vhdl/pyVHDLModel/Pipeline.yml?branch=main&longCache=true&style=flat-square&label=Build%20and%20test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/VHDL/pyVHDLModel/actions/workflows/Pipeline.yml)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyVHDLModel?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff)](https://libraries.io/github/vhdl/pyVHDLModel)
[![Codacy - Quality](https://img.shields.io/codacy/grade/2286426d2b11417e90010427b7fed8e7?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/VHDL/pyVHDLModel)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/2286426d2b11417e90010427b7fed8e7?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/VHDL/pyVHDLModel)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/vhdl/pyVHDLModel?longCache=true&style=flat-square&logo=Codecov)](https://codecov.io/gh/vhdl/pyVHDLModel)

<!--
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyVHDLModel?longCache=true&style=flat-square&logo=GitHub)](https://github.com/vhdl/pyVHDLModel/network/dependents)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyVHDLModel?longCache=true&style=flat-square)](https://libraries.io/github/vhdl/pyVHDLModel/sourcerank)
-->

An abstract VHDL language model written in Python.


# Main Goals

This package provides a unified abstract language model for VHDL.
Projects reading from source files can derive own classes and implement additional logic to create a concrete language
model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can build higher level features and services
on such a model, while supporting multiple frontends.


# Use Cases

## pyVHDLModel Generators

* High-level API for [GHDL's](https://GitHub.com/ghdl/ghdl) `libghdl` offered via `pyghdl`.
* Code Document-Object-Model (Code-DOM) in [pyVHDLParser](https://GitHub.com/Paebbels/pyVHDLParser).

## pyVHDLModel Consumers

* Create graphical views of VHDL files or designs.  
	Possible candidates: [Symbolator](https://GitHub.com/kevinpt/symbolator)
* Created a (re)formatted output of VHDL.


# Examples

## List all Entities with Generics and Ports

The following tiny example is based on GHDL's [`pyGHDL.dom`](https://GitHub.com/ghdl/ghdl/tree/master/pyGHDL/dom) package implementing
pyVHDLModel.

```python
from pathlib import Path
from pyGHDL.dom.NonStandard import Design, Document

sourceFile = Path("example.vhdl")

design = Design()
library = design.GetLibrary("lib")
document = Document(sourceFile)
design.AddDocument(document, library)

for entity in document.Entities.values():
  print(f"{entity.Identifier}")
  print("  generics:")
  for generic in entity.GenericItems:
    identifiers = ", ".join([str(i) for i in generic.Identifiers])
    print(f"  - {identifiers} : {generic.Mode!s} {generic.Subtype}")
  print("  ports:")
  for port in entity.PortItems:
    identifiers = ", ".join([str(i) for i in port.Identifiers])
    print(f"  - {identifiers} : {port.Mode!s} {port.Subtype}")
```


# Contributors

* [Patrick Lehmann](https://GitHub.com/Paebbels) (Maintainer)
* [Unai Martinez-Corral](https://GitHub.com/umarcor)
* [and more...](https://GitHub.com/VHDL/pyVHDLModel/graphs/contributors)


# License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).

-------------------------
SPDX-License-Identifier: Apache-2.0
