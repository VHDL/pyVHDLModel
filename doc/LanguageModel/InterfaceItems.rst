.. _vhdlmodel-inter:

Interface Items
###############

Interface items are used in generic, port and parameter declarations.

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Interface.GenericConstantInterfaceItem
                         pyVHDLModel.Interface.GenericTypeInterfaceItem
                         pyVHDLModel.Interface.GenericProcedureInterfaceItem
                         pyVHDLModel.Interface.GenericFunctionInterfaceItem
                         pyVHDLModel.Interface.GenericPackageInterfaceItem
                         pyVHDLModel.Interface.PortSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.PortViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterConstantInterfaceItem
                         pyVHDLModel.Interface.ParameterVariableInterfaceItem
                         pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterFileInterfaceItem
   :parts: 1


.. _vhdlmodel-generics:

Generic Interface Items
=======================

All items of a generic clause derive from :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`. Generic procedures
and functions also derive from :class:`~pyVHDLModel.Interface.GenericSubprogramInterfaceItemMixin`.

.. _vhdlmodel-genericconstant:

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericConstantInterfaceItem`:

.. code-block:: Python

   @export
   class GenericConstantInterfaceItem(Constant, GenericInterfaceItemMixin, InterfaceItemWithModeMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-generictype:

GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericTypeInterfaceItem`:

.. code-block:: Python

   @export
   class GenericTypeInterfaceItem(Type, GenericInterfaceItemMixin):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntityMixin
     @property
     def Identifier(self) -> str:

     @property
     def NormalizedIdentifier(self) -> str:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:


.. _vhdlmodel-genericprocedure:

GenericProcedureInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericProcedureInterfaceItem`:

.. code-block:: Python

   @export
   class GenericProcedureInterfaceItem(Procedure, GenericSubprogramInterfaceItemMixin):
     # inherited from Subprogram
     @property
     def Parent(self) -> ModelEntity:

     @property
     def IsPure(self) -> bool:

     # inherited from NamedEntityMixin
     @property
     def Identifier(self) -> str:

     @property
     def NormalizedIdentifier(self) -> str:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithGenericsMixin
     @property
     def GenericItems(self) -> list[GenericInterfaceItemMixin]:

     @property
     def GenericCount(self) -> int:

     # inherited from WithParametersMixin
     @property
     def ParameterItems(self) -> list[ParameterInterfaceItemMixin]:

     @property
     def ParameterCount(self) -> int:

     # inherited from SequentialDeclarationRegionMixin
     @property
     def DeclaredItems(self) -> list:

     @property
     def Namespace(self) -> Namespace:

     @property
     def Types(self) -> dict[str, FullType]:

     @property
     def Subtypes(self) -> dict[str, Subtype]:

     @property
     def Constants(self) -> dict[str, Constant]:

     @property
     def Variables(self) -> dict[str, Variable]:

     @property
     def Files(self) -> dict[str, File]:

     @property
     def Functions(self) -> dict[str, list[Function]]:

     @property
     def Procedures(self) -> dict[str, list[Procedure]]:

     # inherited from SequentialStatementsMixin
     @property
     def Statements(self) -> list[SequentialStatement]:


.. _vhdlmodel-genericfunction:

GenericFunctionInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericFunctionInterfaceItem`:

.. code-block:: Python

   @export
   class GenericFunctionInterfaceItem(Function, GenericSubprogramInterfaceItemMixin):
     # inherited from Function
     @property
     def ReturnType(self) -> SubtypeSymbol:

     # inherited from Subprogram
     @property
     def Parent(self) -> ModelEntity:

     @property
     def IsPure(self) -> bool:

     # inherited from NamedEntityMixin
     @property
     def Identifier(self) -> str:

     @property
     def NormalizedIdentifier(self) -> str:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithGenericsMixin
     @property
     def GenericItems(self) -> list[GenericInterfaceItemMixin]:

     @property
     def GenericCount(self) -> int:

     # inherited from WithParametersMixin
     @property
     def ParameterItems(self) -> list[ParameterInterfaceItemMixin]:

     @property
     def ParameterCount(self) -> int:

     # inherited from SequentialDeclarationRegionMixin
     @property
     def DeclaredItems(self) -> list:

     @property
     def Namespace(self) -> Namespace:

     @property
     def Types(self) -> dict[str, FullType]:

     @property
     def Subtypes(self) -> dict[str, Subtype]:

     @property
     def Constants(self) -> dict[str, Constant]:

     @property
     def Variables(self) -> dict[str, Variable]:

     @property
     def Files(self) -> dict[str, File]:

     @property
     def Functions(self) -> dict[str, list[Function]]:

     @property
     def Procedures(self) -> dict[str, list[Procedure]]:

     # inherited from SequentialStatementsMixin
     @property
     def Statements(self) -> list[SequentialStatement]:


.. _vhdlmodel-genericpackage:

GenericPackageInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericPackageInterfaceItem`:

.. code-block:: Python

   @export
   class GenericPackageInterfaceItem(InterfacePackage, GenericInterfaceItemMixin):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntityMixin
     @property
     def Identifier(self) -> str:

     @property
     def NormalizedIdentifier(self) -> str:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:


.. _vhdlmodel-ports:

Port Interface Items
====================

.. _vhdlmodel-portsignal:

PortSignalInterfaceItem
-----------------------

``PortSignalInterfaceItem`` is an abstract base-class for :class:`~pyVHDLModel.Interface.PortSimpleSignalInterfaceItem`
(``port (p : in bit);``) and :class:`~pyVHDLModel.Interface.PortViewSignalInterfaceItem` (``port (p : view MyView);``,
VHDL-2019 mode views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-portsimplesignal:

PortSimpleSignalInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.PortSimpleSignalInterfaceItem`:

.. code-block:: Python

   @export
   class PortSimpleSignalInterfaceItem(PortSignalInterfaceItem, InterfaceItemWithModeMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-portviewsignal:

PortViewSignalInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.PortViewSignalInterfaceItem`:

.. code-block:: Python

   @export
   class PortViewSignalInterfaceItem(PortSignalInterfaceItem):
     # defined in PortViewSignalInterfaceItem
     @property
     def ModeViewIndication(self) -> ModeViewSymbol:

     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:


.. _vhdlmodel-parameters:

Parameter Interface Items
=========================

.. _vhdlmodel-parameterconstant:

ParameterConstantInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterConstantInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-parametervariable:

ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterVariableInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-parametersignal:

ParameterSignalInterfaceItem
----------------------------

``ParameterSignalInterfaceItem`` is an abstract base-class for
:class:`~pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem` (``procedure p(signal s : in bit);``) and
:class:`~pyVHDLModel.Interface.ParameterViewSignalInterfaceItem` (``procedure p(signal s : view MyView);``, VHDL-2019
mode views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-parametersimplesignal:

ParameterSimpleSignalInterfaceItem
----------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterSimpleSignalInterfaceItem(ParameterSignalInterfaceItem, InterfaceItemWithModeMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-parameterviewsignal:

ParameterViewSignalInterfaceItem
--------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterViewSignalInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterViewSignalInterfaceItem(ParameterSignalInterfaceItem):
     # defined in ParameterViewSignalInterfaceItem
     @property
     def ModeViewIndication(self) -> ModeViewSymbol:

     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> Nullable[ExpressionUnion]:


.. _vhdlmodel-parameterfile:

ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterFileInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterFileInterfaceItem(File, ParameterInterfaceItemMixin):
     # inherited from Obj
     @property
     def Subtype(self) -> Symbol:

     @property
     def ObjectVertex(self) -> Nullable[Vertex]:

     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from MultipleNamedEntityMixin
     @property
     def Identifiers(self) -> tuple[str]:

     @property
     def NormalizedIdentifiers(self) -> tuple[str]:

     # inherited from DocumentedEntityMixin
     @property
     def Documentation(self) -> Nullable[str]:
