.. _vhdlmodel:

VHDL Language Model
###################

.. topic:: Design Goal

   * Clearly named classes that model the semantics of VHDL.
   * All language constructs (statements, declarations, specifications, …) have
     their own classes. |br| These classes are arranged in a logical hierarchy,
     with a single common base-class.
   * Child objects shall have a reference to their parent.
   * Comments will be associated with a particular code object.
   * Easy modifications of the object tree.

.. rubric:: Elements of the Language Model

.. toctree::
   :maxdepth: 1

   Miscellaneous
   Enumerations
   DesignUnits
   InterfaceItems
   SubprogramDefinitions
   TypeDefinitions
   ObjectDeclarations
   ConcurrentStatements
   SequentialStatements
   Expressions
