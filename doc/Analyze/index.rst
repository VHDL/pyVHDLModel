.. _analyze:

Analyze
#######

1. Dependency analysis

:meth:`Design.Analyze <pyVHDLModel.Design.Analyze>` can be called again, e.g. after documents or design units were added
to or removed from the design: it resets the previous analysis first (:meth:`~pyVHDLModel.Design.ResetAnalysis`). The
reset replaces the graphs and clears everything the analysis derived from the design units, while libraries, documents,
design units and their declarations are kept.

Dependency Analysis
*******************

1. Create Dependency Graph
==========================

Create unconnected vertices in the design's dependency graph for every VHDL library object and every design unit.

The vertex's ``ID`` field is set to a unique identifying string. |br|
The following patterns are used:

Libraries
   The normalized library name: ``library``.
Contexts
   The normalized library and context name: ``library.context``.
Entities
   The normalized library and entity name: ``library.entity``.
Architectures
   The normalized library, entity and architecture name in parenthesis: ``library.entity(architecture)``.
Packages
   The normalized library and package name: ``library.package``.
Package Bodies
   The normalized library and package name: ``library.package(body)``.

The vertex's ``Value`` field references to the library or design unit object respectively.

Each vertex has two attributes:

``"kind"``
   A kind attribute is set to an enumeration value of :py:class:`~pyVHDLModel.DependencyGraphVertexKind` representing
   vertex kind (type).
``"predefined"``
   A predefined attribute is set to ``True``, if the library or design unit is a VHDL predefined language entity from
   e.g. from ``std`` or ``ieee``.

Lastly, every vertex is assigned to a :py:attr:``~pyVHDLModel.DesignUnit.DesignUnit._dependencyVertex`` field. Thus,
there is a double reference from graph's vertex via ``Value`` to the DOM object as well as in reverse via
``_dependencyVertex`` to the representing vertex.

.. code-block:: vhdl

   predefinedLibraries = ("std", "ieee")

   for libraryIdentifier, library in self._libraries.items():
     dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}", value=library, graph=self._dependencyGraph)
     dependencyVertex["kind"] = DependencyGraphVertexKind.Library
     dependencyVertex["predefined"] = libraryIdentifier in predefinedLibraries
     library._dependencyVertex = dependencyVertex

     for contextIdentifier, context in library._contexts.items():
       dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{contextIdentifier}", value=context, graph=self._dependencyGraph)
       dependencyVertex["kind"] = DependencyGraphVertexKind.Context
       dependencyVertex["predefined"] = context._library._normalizedIdentifier in predefinedLibraries
       context._dependencyVertex = dependencyVertex


2. Create Compile Order Graph
=============================

3. Index Packages
=================

4. Index Entities
=================

5. Index Architectures
======================

6. Link Contexts
================

7. Link Architectures
=====================

8. Link Package Bodies
======================

9. Link Library References
==========================

10. Link Package References
===========================

11. Link Context References
===========================

12. Link Components
===================

13. Link Instantiations
=======================

14. Create Hierarchy Graph
==========================

15. Compute Compile Order
=========================


Object Analysis
***************

:meth:`Design.AnalyzeObjects <pyVHDLModel.Design.AnalyzeObjects>` runs after the dependency analysis, which linked the
use clauses and computed the compile order.

1. Resolve Type Marks
=====================

:meth:`Design.ResolveTypeMarks <pyVHDLModel.Design.ResolveTypeMarks>` iterates the design units in compile order and
their declarative regions. Each declaration resolves its type marks
(:meth:`ModelEntity.ResolveReferences <pyVHDLModel.Base.ModelEntity.ResolveReferences>`) by the region declaring it
(:meth:`DeclarationRegionMixin.ResolveTypeMark <pyVHDLModel.Regions.DeclarationRegionMixin.ResolveTypeMark>`). A
resolved type mark references its type or subtype (:attr:`Symbol.Reference <pyVHDLModel.Symbol.Symbol.Reference>`).

Type Attributes
---------------

A type mark can be an attribute name denoting a type: ``x'subtype``, ``A'element``, or ``T'base`` as the prefix of
another attribute. Such a name is a chain of names: the attribute name's prefix is a selected name, whose prefix is a
simple name. Each name resolves its prefix first (:meth:`Name.Denote <pyVHDLModel.Name.Name.Denote>`) and applies
itself to the declaration the prefix references. Only the type mark's symbol keeps a reference; the references of the
parts aren't stored.

.. code-block:: vhdl

   type T  is (a, b);
   type AT is array (natural range <>) of T;
   type R  is record
     f : AT;
   end record;
   signal rec : R;
   signal s2  : rec.f'subtype;

The same declarations as a pyVHDLModel instance, analyzed in a :class:`~pyTooling.Warning.WarningCollector`:

.. code-block:: python

   from pathlib                import Path

   from pyTooling.Warning      import WarningCollector

   from pyVHDLModel            import Design, Document
   from pyVHDLModel.DesignUnit import Architecture, Entity
   from pyVHDLModel.Expression import EnumerationLiteral
   from pyVHDLModel.Name       import AttributeName, SelectedName, SimpleName
   from pyVHDLModel.Object     import Signal
   from pyVHDLModel.Symbol     import EntitySymbol, SimpleSubtypeSymbol
   from pyVHDLModel.Type       import ArrayType, EnumeratedType, RecordType, RecordTypeElement

   typeT =    EnumeratedType("T", [EnumerationLiteral("a"), EnumerationLiteral("b")])
   typeAT =   ArrayType("AT", [SimpleSubtypeSymbol(SimpleName("natural"))], SimpleSubtypeSymbol(SimpleName("T")))
   typeR =    RecordType("R", [RecordTypeElement(["f"], SimpleSubtypeSymbol(SimpleName("AT")))])
   rec =      Signal(["rec"], SimpleSubtypeSymbol(SimpleName("R")))
   typeMark = SimpleSubtypeSymbol(AttributeName("subtype", SelectedName("f", SimpleName("rec"))))
   s2 =       Signal(["s2"], typeMark)

   entity =       Entity("e")
   architecture = Architecture("rtl", EntitySymbol(SimpleName("e")), declaredItems=[typeT, typeAT, typeR, rec, s2])

   design =   Design("design")
   design.LoadStdLibrary()
   document = Document(Path("e.vhdl"))
   document.AddDesignUnit(entity)
   document.AddDesignUnit(architecture)
   design.AddDocument(document, design.GetLibrary("lib"))

   with WarningCollector() as collector:
     design.Analyze()

   assert len(collector.Warnings) == 0
   assert typeMark.Reference is typeAT

:meth:`~pyVHDLModel.Design.Analyze` calls :meth:`~pyVHDLModel.Design.AnalyzeObjects`, which calls
:meth:`~pyVHDLModel.Design.ResolveTypeMarks`. The architecture's declarative region resolves the type mark of ``s2``
(``region`` is the architecture, ``place`` the signal ``s2``):

1. ``region.ResolveTypeMark(designUnit, s2, typeMark)``: the type mark's name is an attribute name, so it calls
   ``typeMark.Name.Denote(region, designUnit, s2, typeMark)`` on the attribute name ``rec.f'subtype``.
2. The attribute name calls ``Denote`` on its prefix, the selected name ``rec.f``.
3. The selected name calls ``Denote`` on its prefix, the simple name ``rec``. The simple name is looked up at the place
   (:meth:`region.LookupName(designUnit, s2, typeMark, name, ...)
   <pyVHDLModel.Regions.DeclarationRegionMixin.LookupName>`); the found declaration, the signal ``rec``, returns itself
   (:meth:`rec.DenoteBy(...) <pyVHDLModel.Base.ModelEntity.DenoteBy>`): **signal** ``rec``.
4. Back in the selected name: ``rec`` is an object, its subtype ``R`` is a record type, so the name returns the record
   element ``f`` (:attr:`R.ElementsByIdentifier["f"] <pyVHDLModel.Type.RecordType.ElementsByIdentifier>`):
   **record element** ``f``.
5. Back in the attribute name: ``'subtype`` (:attr:`AttributeName.PredefinedAttribute
   <pyVHDLModel.Name.AttributeName.PredefinedAttribute>`) of an object returns the object's subtype: **type** ``AT``.
6. The region sets the type mark's reference: ``typeMark.Reference`` is ``typeAT``.

A part, which can't be resolved, is reported where it fails as an
:exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning` and the type mark stays unresolved, e.g. ``Prefix 'rec' of type
mark 'rec.g'subtype' has no record element 'g'.``
