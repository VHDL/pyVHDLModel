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


