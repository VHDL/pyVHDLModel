.. _datastruct:

Data Structures
###############

Besides the document object model as a tree-like structure, pyVHDLModel has either lists, lookup dictionaries, direct
cross-references or dedicated data structure (tree, graph, …) for connecting multiple objects together.

Graphs
******

pyVHDLModel uses the graph implementation from :pyTool:mod:`pyTooling.Graph` as it provides an object oriented programming
interface to vertices and edges.

Dependency Graph
================

The dependency graph describes dependencies between:

* Sourcecode files
* VHDL libraries
* Contexts
* Packages
* Entities
* Architectures
* Packages
* Package Bodies
* Configurations

The relation can be:

* Defined in source file
* references
* implements
* instantiates
* needs to be analyzed before


Hierarchy Graph
===============

The hierarchy graph can be derived from dependency graph by:

1. copying all entity and architecture vertices
2. copying all implements dependency edges
3. copying all instantiates edges in reverse direction

The graph can then be scanned for a root vertices (no inbound edges). If only a single root vertex exists, this vertex
references the toplevel of the design.


Compile Order Graph
===================

The compile order can be derived from dependency graph by:

1. copying all document vertices
2. iterating all edges in the dependency graph.
   1. resolve the source and the destination to the referenced design units
   2. resolved further to the documents these design units are declared in
   3. resolve further which vertices correspond in the compile order graph
   4. if edges does not yet exist, add an edge between two documents in the compile order graph


.. toctree::
   :hidden:

   DependencyGraph
   HierarchyGraph
   CompileOrderGraph
