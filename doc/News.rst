.. _NEWS:

News
####

See :gh:`pyVHDLModel Release Pages <VHDL/pyVHDLModel/releases>` for detail release notes on every release.


Version 0.42.0 (2026)
*********************

.. topic:: :gh:`v0.42.0 - 31.10.2026 <VHDL/pyVHDLModel/releases/v0.42.0>`

   .. rubric:: New Features

   * Interface groups partition the generic clause, the port clause and the parameter list of a language construct:
     constructor parameters ``genericGroups``, ``portGroups`` and ``parameterGroups``, properties
     :data:`~pyVHDLModel.Regions.WithGenericsMixin.GenericGroups`,
     :data:`~pyVHDLModel.Regions.WithPortsMixin.PortGroups` and
     :data:`~pyVHDLModel.Regions.WithParametersMixin.ParameterGroups`. Each interface item refers to its group
     (:data:`~pyVHDLModel.Interface.InterfaceItemMixin.Group`). ``Add***Item()`` and ``Insert***Item()`` take an
     optional group; all mutators keep the partition.

   .. rubric:: Changes

   * Breaking change: :class:`~pyVHDLModel.Interface.GenericGroup`, :class:`~pyVHDLModel.Interface.PortGroup` and
     :class:`~pyVHDLModel.Interface.ParameterGroup` are non-owning views of a language construct's interface items: an
     item's parent stays the language construct, and a group has no mutators any more. A group rejects an empty or
     already grouped item list.
   * Breaking change: a language construct constructed without groups checks its interface items' types: an item of
     the wrong type raises :exc:`TypeError`, where it was accepted before.


Version 0.41.0 (2026)
*********************

.. topic:: :gh:`v0.41.0 - 31.10.2026 <VHDL/pyVHDLModel/releases/v0.41.0>`

   .. rubric:: New Features

   * A group of targets on the left-hand side of an assignment (``(carry, sum) := ...``) is
     :class:`~pyVHDLModel.Symbol.AggregateSymbol`.
   * Character literals of enumeration types are their own class:
     :class:`~pyVHDLModel.Expression.CharacterEnumerationLiteral` holds the bare character; the VHDL writer adds the
     apostrophes.
   * The condition operator ``??`` is :class:`~pyVHDLModel.Expression.ConditionExpression`.
   * Visitor: declarations, statements and context items report their semicolon as
     :meth:`~pyVHDLModel.Visitor.Visitor.VisitTerminator`.
   * VHDL writer: the reserved words and the name after ``end`` can be left out where VHDL allows it
     (``VHDLStyle(endKeyword=..., endName=...)``); the visitor reports :meth:`~pyVHDLModel.Visitor.Visitor.VisitEnd`.

   .. rubric:: Changes

   * The character literals of ``STD.bit`` and ``STD.character`` hold the bare character (``"0"``, was ``"'0'"``).

   .. rubric:: Bug Fixes

   * ``IEEE.std_ulogic``'s literals are written as character literals; ``STD.character``'s literal at position 92 is
     ``'\'``.

   .. rubric:: Documentation

   * The language model pages render their classes from the source (``condensed-class``) and name the current modules.


Version 0.40.0 (2026)
*********************

.. topic:: :gh:`v0.40.0 - 29.10.2026 <VHDL/pyVHDLModel/releases/v0.40.0>`

   .. rubric:: New Features

   * Mutation API, first part: generics, ports, parameters, declared items and statements can be added, inserted,
     moved and removed, with ownership checks and namespace updates; association items, context items, a document's
     design units, a design's documents and libraries too.
   * VHDL writer: :class:`~pyVHDLModel.Formatting.VHDL.VHDLWriter` writes the model as VHDL source text - from
     literals and expressions to design units, configurations and whole documents -, built on the visitor
     :class:`~pyVHDLModel.Visitor.Visitor`; formatting options are named after vhdl-style-guide's.
   * Warnings and mutation errors carry the model objects they are about.
   * A design can be analyzed again after it was changed; design units are looked up by library and name, or searched
     in all libraries.
   * Names, symbols, expressions, ranges, association items, object declarations and interface items can be copied.
   * A subprogram's signature - the type marks of its parameters and return value - tells overloads apart.
   * Bit string literals compute their value.

   .. rubric:: Changes

   * pyTooling 10.1 is required; Python 3.11 to 3.15 are supported.
   * Duplicate declarations are critical warnings.
   * A namespace keeps use-clause imports apart from its declarations.
   * The base-classes of the model are abstract.

   .. rubric:: Bug Fixes

   * Architecture keys, if-generate else branches, multi-identifier normalization, entity-instantiation errors,
     ``Context.ContextItems``, a second ``Design.Analyze()`` and entity namespaces after the analysis.

   .. rubric:: Documentation

   * New page :ref:`VHDL Writer <WRITER>`; the documentation is built with pyTooling.Sphinx.


Version 0.7.0 - 0.39.0 (2020 - 2026)
************************************

.. only:: html

   April 2026 - Generic, Port, and Parameter Groups
   ================================================

.. only:: latex

   .. rubric:: Generic, Port, and Parameter Groups

* Link components in architectures and components nested in concurrent statements.
* Added grouping of generics, ports and parameters.


.. only:: html

   Nov. 2025 - Raise Warnings
   ==========================

.. only:: latex

   .. rubric:: Raise Warnings

* Handle bit-string literals
* Raise Warnings instead of Exceptions.


.. only:: html

   Feb. 2025 - Blackboxes
   ======================

.. only:: latex

   .. rubric:: Blackboxes

* Support handling of blackboxes for component instantiations.
* Added dummy packages for Synopsys and Mentor Graphics "IEEE" packages.


.. only:: html

   Sept. 2024 - Unary Operators
   ============================

.. only:: latex

   .. rubric:: Unary Operators

* Added more unary operators.
* Added more doc-strings


.. only:: html

   Jan. 2023 - Dependency, Hierarchy, Compile Order Analysis
   =========================================================

.. only:: latex

   .. rubric:: Dependency, Hierarchy, Compile Order Analysis

* Enhanced analysis of cross references.
* Enhanced dependency graphs:

  * Hierarchy graph and toplevel detection
  * Compile order computation

* Transformation from single module to >15 modules.
* Improved code coverage and test cases.


.. only:: html

   Dec. 2022 - Added Documentation Property
   ========================================

.. only:: latex

   .. rubric:: Added Documentation Property

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is now able to collect and associate (documentation) comments to language
  constructs. This enhancement adds a ``Documentation`` property to many classes similar to a *doc-string* in Python.
* New -style of symbols merging a ``Name`` and a ``Symbol`` class.
* Finding relations between packages and its bodies, entities and its architectures.
* References to libraries, packages and contexts.
* Dependency graph for packages, contexts, and entities.

  * Package graph.
  * Hierarchy graph.
  * Compile order.


.. only:: html

   Jul. 2021 - First adoption and enhancements
   ===========================================

.. only:: latex

   .. rubric:: First adoption and enhancements

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is the first big adopter with `pyGHDL.dom <https://ghdl.github.io/ghdl/pyGHDL/pyGHDL.dom.html>`__
  to generate a network of instantiated classes derived from ``pyVHDLModel``. |br|
  It uses `pyGHDL <https://ghdl.github.io/ghdl/using/pyGHDL/index.html>`__ as a backend (GHDL build as shared object and
  loaded into CPython via C-binding API (``ctypes``).


.. only:: html

   Jun. 2021 - Model and documentation enhancements
   ================================================

.. only:: latex

   .. rubric:: Model and documentation enhancements

* Made generic, port, and parameter items a subclass of the matching object classes.
* Added missing object representations for language features.

  * Finalized literals, expressions and types.
  * Added properties to empty placeholder classes.

* Corrected class hierarchy according to LRM.
* Enhanced class documentation and cross references.
* New documentation chapter for literals and expressions.
* Added inheritance diagrams as overviews to documentation sections.
* Added condensed code snippets outlining the main interface of a model's object.
* New Single-File GitHub Action workflow (pipeline) including tests, documentation, packaging and publishing.
* Added Dependabot configuration file.
* Removed 2 dependencies to patched Sphinx extensions (now fixed in Sphinx).
* ...

.. only:: html

   Jan. 2021 - Documentation enhancements
   ======================================

.. only:: latex

   .. rubric:: Documentation enhancements

* Enhanced class documentation.
* Changed test runner to ``pytest``.
* Dependency check and license clearance. |br|
  See :ref:`DEP` for details.


.. only:: html

   Dec. 2020 - Split from pyVHDLParser
   ===================================

.. only:: latex

   .. rubric:: Split from pyVHDLParser

* `pyVHDLModel` was split from `pyVHDLParser <https://GitHub.com/Paebbels/pyVHDLParser>`__ (v0.6.0) as an independent Python package.
