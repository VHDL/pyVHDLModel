.. _GettingStarted:

Getting Started
###############

*pyVHDLModel* is a VHDL language model without any parser. There are currently two parsers available that can serve as a
frontend to pyVHDLModel. These parsers can generate a VHDL language model instance from VHDL source files:

* pyVHDLParser (currently broken)
* GHDL


pyVHDLParser
************

The pyVHDLParser is a token-stream based parser creating a code document object model (CodeDOM) derived from
pyVHDLModel. Actually, pyVHDlModel was originally part of that parser, until it got refactored into this standalone
package so multiple frontends (parsers) and backends (analysis tools) can use this VHDL language model as a common API.

.. warning:: Currently, pyVHDLParser is not aligned with latest updates in pyVHDLModel.


GHDL as Parser
**************

The free and open-source VHDL-2008 simulator **GHDL** offers a Python binding, so Python code can access ``libghdl``.
This binding layer is exposed in the ``pyGHDL.libghdl`` package. In addition, GHDL offers a ``pyGHDL.dom`` package
implementing derived classes of pyVHDLModel. Each derived class adds translation methods (``.parse(iirNode)``) from
GHDL's internal data structure IIR to the code document object model (CodeDOM) of pyVHDLModel.


Installation and Setup
======================

To use pyVHDLModel a tool offering a parser like GHDL is required. GHDL itself offers multiple options for installation.
In addition it has multiple backends. For the usage with pyVHDLModel, an ``mcode`` backend is preferred, as it's faster
and doesn't write ``*.o`` files to the disk. As most Python installation are nowadays 64-bit, an ``mcode 64-bit``
variant of GHDL would be best.

On Windows - Native
"""""""""""""""""""

Assuming a 64-bit Windows installation and a 64-bit CPython (`python.org <https://www.python.org/downloads/>`__)
installation, it's suggested to install:

* `GHDL 3.0.0-dev - MinGW64 - mcode - standalone <https://github.com/ghdl/ghdl/releases/download/nightly/MINGW64-mcode-standalone.zip>`__
* `GHDL 3.0.0-dev - UCRT64 - mcode - standalone <https://github.com/ghdl/ghdl/releases/download/nightly/UCRT64-mcode-standalone.zip>`__

As development of Python packages ``pyGHDL.dom`` and ``pyVHDLModel`` are under quick development cycles, a GHDL
``nightly`` build is suggested compared to the stable releases (once a year). These nightly builds are provided as ZIP
files on GitHub: https://github.com/ghdl/ghdl/releases/tag/nightly (or use links from above).

At next, unpack the ZIP files content to e.g. :file:`C:\\Tools\\GHDL\\3.0.0-dev` (GHDL installation directory). This ZIP
file brings the GHDL synthesis and simulation tool as well as :file:`libghdl-3_0_0_dev.dll` needed as a parser frontend.


On Windows - MSYS2
""""""""""""""""""

Assuming a 64-bit Windows installation and an `MSYS2 <https://www.msys2.org/>`__ installation in :file:`C:\msys64`.


.. rubric:: MSYS2 Prepartions and GHDL/libghdl Installation

Start either the MinGW64 or UCRT64 environment and then use :command:`pacman` to install GHDL. The following steps are
explained for UCRT64, but can be applied to MinGW64 similarly.

.. admonition:: Bash

   .. code-block:: bash

      # Update MSYS2 to latest package releases
      pacman -Suyy

      # If the core system was updated, a second run might be required.
      pacman -Suyy

      # Search for available GHDL packages
      pacman -Ss ghdl
      # mingw32/mingw-w64-i686-ghdl-mcode 2.0.0.r870.g1cc85c578-1 (mingw-w64-i686-eda) [Installiert]
      #     GHDL: the open-source analyzer, compiler, simulator and (experimental) synthesizer for VHDL (mcode backend) (mingw-w64)
      # mingw64/mingw-w64-x86_64-ghdl-llvm 2.0.0.r870.g1cc85c578-1 (mingw-w64-x86_64-eda) [Installiert]
      #     GHDL: the open-source analyzer, compiler, simulator and (experimental) synthesizer for VHDL (LLVM backend) (mingw-w64)
      # ucrt64/mingw-w64-ucrt-x86_64-ghdl-llvm 2.0.0.r870.g1cc85c578-1 (mingw-w64-ucrt-x86_64-eda) [Installiert]
      #     GHDL: the open-source analyzer, compiler, simulator and (experimental) synthesizer for VHDL (LLVM backend) (mingw-w64)

      # Note: The GHDL version is 870 commits after 2.0.0 release and has Git hash "1cc85c578" (without prefix 'g')

      # Install GHDL for UCRT64
      pacman -S ucrt64/mingw-w64-ucrt-x86_64-ghdl-llvm

.. rubric:: Installing pyGHDL

At next, pyGHDL matching the currently installed GHDL version must be installed. At best, pyGHDL matches the exact Git
hash of GHDL, so there is no discrepancy between the libghdl binary and the DLL binding layer in ``pyGHDL.libghdl``.

Assuming *Git for Windows* is installed and available in PowerShell, the following command will install pyGHDL via PIP:

.. admonition:: PowerShell

   .. code-block:: powershell

      # Install pyGHDL
      pip install git+https://github.com/ghdl/ghdl.git@$(ghdl version hash).


On Windows from Sources
"""""""""""""""""""""""

Assuming a 64-bit Windows installation, a 64-bit CPython (`python.org <https://www.python.org/downloads/>`__)
installation as well as an `MSYS2 <https://www.msys2.org/>`__ installation in :file:`C:\msys64`.

.. rubric:: MSYS2 Prepartions

Start either the MinGW64 or UCRT64 environment and then use :command:`pacman` to install build dependencies. The
following steps are explained for UCRT64, but can be applied to MinGW64 similarly.

.. admonition:: Bash

   .. code-block:: bash

      # Update MSYS2 to latest package releases
      pacman -Suyy

      # If the core system was updated, a second run might be required.
      pacman -Suyy

      # Install system dependencies
      pacman -S git
      pacman -S make
      pacman -S diffutils

      # Install GHDL build dependencies (GCC with Ada support)
      pacman -S ucrt64/mingw-w64-ucrt-x86_64-gcc-ada

.. rubric:: Building GHDL and libghdl

The next steps will clone GHDL from GitHub, configure the software, build the binaries, run the testsuite and install
all needed result files into the installation directory.

.. admonition:: Bash

   .. code-block:: bash

      # Clone GHDL repository
      mkdir -p /c/Tools/GHDL
      cd /c/Tools/GHDL
      git clone https://github.com/ghdl/ghdl.git sources

      # Create build directory and configure GHDL
      mkdir -p sources/build
      cd sources/build
      ../configure --prefix=/c/Tools/GHDL/3.0.0-dev

      # Build GHDL, run testsuite and install to ``prefix``
      make
      make install

The directory structure will look like this:

.. code-block::

   ├── Tools
   │   ├── GHDL
   │   │   ├── 3.0.0-dev
   │   │   │   ├── bin
   │   │   │   ├── include
   │   │   │   ├── lib
   │   │   │   │   ├── ghdl
   │   │   ├── sources
   │   │   │   ├── ...
   │   │   │   ├── pyGHDL
   │   │   │   ├── src
   │   │   │   ├── ...

In the next steps, some files from MSYS2/UCRT64 need to be copied into the installation directory, so
:file:`libghdl-3_0_0_dev.dll` can be used independently from MSYS2 environments.

.. rubric:: Installing pyGHDL

As a final setup step, pyGHDL needs to be installed via PIP by executing some commands in PowerShell. The dependencies
of pyGHDL will take care of installing all necessary requirements like pyVHDLModel.

.. admonition:: PowerShell

   .. code-block:: powershell

      cd C:\Tools\GHDL\sources
      pip install .


.. rubric:: Updating GHDL and libghdl

If GHDL gets updated through new commits, start the UCRT64 console and execute these instructions to build a latest
:file:`libghdl-3_0_0_dev.dll`:

.. admonition:: Bash

   .. code-block:: bash

      # Update Git reository
      cd /c/Tools/GHDL/sources/build
      git pull

      # Recompile GHDL
      make

      # Overwrite file in installation directory
      make install

.. rubric:: Updating pyGHDL

TBD

On Linux
""""""""

.. todo:: Write how to get started on Linux with libghdl.


On Mac
""""""

.. todo:: Write how to get started on Mac with libghdl.


Using libghdl with Python
=========================

An environment variable :envvar:`GHDL_PREFIX=C:\\Tools\\GHDL\\3.0.0-dev\\lib\\ghdl` is needed for libghdl. The path is
constructed from installation path plus ``lib\\ghdl``.

.. admonition:: GettingStarted.py

   .. code-block:: Python

      from pathlib import Path
      from pyGHDL.dom.NonStandard import Design, Document

      fileList = (
        ("libStopWatch", Path("Counter.vhdl")),  # a list of 2-element tuples; library name and pat to the VHDL file
        ...                                      # just for this example to simply loop all files
      )

      design = Design()
      design.LoadDefaultLibraries()    # loads std.* and ieee.* (dummies for now to calculate dependencies)
      for libName, file in fileList:
        library = design.GetLibrary(libName)
        document = Document(file)
        design.AddDocument(document, library)

      # Analyzing dependencies and computing graphs
      design.Analyze()

      # Accessing the TopLevel
      design.TopLevel

      # Accessing graphs
      design.DependencyGraph
      design.HierarchyGraph
      design.CompileOrderGraph
