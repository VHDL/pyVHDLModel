.. _vhdlmodel-obj:

Object Declarations
###################

.. contents:: Table of Content
   :local:

.. #rubric:: Class Hierarchy

.. #inheritance-diagram:: pyVHDLModel.SyntaxModel.Constant pyVHDLModel.SyntaxModel.DeferredConstant pyVHDLModel.SyntaxModel.GenericConstantInterfaceItem pyVHDLModel.SyntaxModel.ParameterConstantInterfaceItem pyVHDLModel.SyntaxModel.Variable pyVHDLModel.SyntaxModel.ParameterVariableInterfaceItem pyVHDLModel.SyntaxModel.Signal pyVHDLModel.SyntaxModel.PortSignalInterfaceItem pyVHDLModel.SyntaxModel.ParameterSignalInterfaceItem pyVHDLModel.SyntaxModel.File pyVHDLModel.SyntaxModel.ParameterFileInterfaceItem
   :parts: 1



.. _vhdlmodel-constants:

Constants
=========

VHDL defines regular constants as an object. In addition, deferred constants are
supported in package declarations. Often generics to e.g. packages or entities
are constants. Also most *in* parameters to subprograms are constants.

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.Constant pyVHDLModel.SyntaxModel.DeferredConstant pyVHDLModel.SyntaxModel.GenericConstantInterfaceItem pyVHDLModel.SyntaxModel.ParameterConstantInterfaceItem
   :parts: 1



.. _vhdlmodel-constant:

Constant
--------

A constant represents immutable data. This data (value) must be assigned via a
default expression. If a constant's value is delayed in calculation, it's called
a deferred constant. See :ref:`vhdlmodel-deferredconstant` in next section.


**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.Constant`:

.. code-block:: Python

   @export
   class Constant(BaseConstant):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     @property
     def DefaultExpression(self) -> BaseExpression:



.. _vhdlmodel-deferredconstant:

Deferred Constant
-----------------

If a constant's value is delayed in calculation, it's a deferred constant. Such
a deferred constant has a reference to the *regular* constant of the same name.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.DeferredConstant`:

.. code-block:: Python

   @export
   class DeferredConstant(BaseConstant):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def ConstantReference(self) -> Constant:



.. _vhdlmodel-obj-genericconstant:

Generic Constant
----------------

A generic without object class or a generic constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-genericconstant` for details.

.. _vhdlmodel-obj-parameterconstant:

Constant as Parameter
---------------------

A subprogram parameter without object class of mode *in* or a parameter constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-parameterconstant` for details.



.. _vhdlmodel-variables:

Variables
=========

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.Variable pyVHDLModel.SyntaxModel.ParameterVariableInterfaceItem
   :parts: 1

.. _vhdlmodel-variable:

Variable
--------

A variable represents mutable data in sequential regions. Assignments to
variables have no delay. The initial value can be assigned via a default
expression.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.Variable`:

.. code-block:: Python

   @export
   class Variable(Object):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:



.. _vhdlmodel-obj-parametervariable:

Variable as Parameter
---------------------

A subprogram parameter without object class of mode *out* or a parameter variable is a *regular* variable.

.. seealso::

   See :ref:`vhdlmodel-parametervariable` for details.


.. _vhdlmodel-sharedvariable:

Shared Variable
===============

.. todo::

   Write documentation.

.. _vhdlmodel-signals:

Signals
=======

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.Signal pyVHDLModel.SyntaxModel.PortSignalInterfaceItem pyVHDLModel.SyntaxModel.ParameterSignalInterfaceItem
   :parts: 1

.. _vhdlmodel-signal:

Signal
------

A signal represents mutable data in concurrent regions. Assignments to signals
are delayed until next wait statement is executed. The initial value can be
assigned via a default expression.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.Signal`:

.. code-block:: Python

   @export
   class Signal(Object):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:



.. _vhdlmodel-obj-portsignal:

Signal as Port
--------------

A port signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-portsignal` for details.

.. _vhdlmodel-obj-parametersignal:

Signal as Parameter
-------------------

A parameter signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-parametersignal` for details.

.. _vhdlmodel-files:

Files
=====

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.File pyVHDLModel.SyntaxModel.ParameterFileInterfaceItem
   :parts: 1

.. _vhdlmodel-file:

File
----

.. todo::

   Write documentation.

.. _vhdlmodel-obj-parameterfile:

File as Parameter
-----------------

A parameter file is a *regular* file.

.. seealso::

   See :ref:`vhdlmodel-parameterfile` for details.
