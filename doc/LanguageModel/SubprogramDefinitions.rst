.. _vhdlmodel-subprog:

Subprogram Declarations
#######################

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Subprogram.Procedure
                         pyVHDLModel.Subprogram.ProcedureMethod
                         pyVHDLModel.Interface.GenericProcedureInterfaceItem
                         pyVHDLModel.Subprogram.Function
                         pyVHDLModel.Subprogram.FunctionMethod
                         pyVHDLModel.Interface.GenericFunctionInterfaceItem
   :parts: 1

.. _vhdlmodel-procedures:

Procedures
**********

.. inheritance-diagram:: pyVHDLModel.Subprogram.Procedure
                         pyVHDLModel.Subprogram.ProcedureMethod
                         pyVHDLModel.Interface.GenericProcedureInterfaceItem
   :parts: 1



.. _vhdlmodel-procedure:

Procedure
=========

**Condensed definition of class** :class:`~pyVHDLModel.Subprogram.Procedure`:

.. condensed-class:: pyVHDLModel.Subprogram.Procedure


.. _vhdlmodel-procedureinstantiation:

Procedure Instantiation
=======================

.. todo::

   Write documentation.



.. _vhdlmodel-proceduremethod:

Procedure as Method
===================

**Condensed definition of class** :class:`~pyVHDLModel.Subprogram.ProcedureMethod`:

.. condensed-class:: pyVHDLModel.Subprogram.ProcedureMethod


.. _vhdlmodel-sub-genericprocedure:

Generic Procedure
=================

A generic procedure is a *regular* procedure.

.. seealso::

   See :ref:`vhdlmodel-genericprocedure` for details.



.. _vhdlmodel-functions:

Functions
*********

.. inheritance-diagram:: pyVHDLModel.Subprogram.Function
                         pyVHDLModel.Subprogram.FunctionMethod
                         pyVHDLModel.Interface.GenericFunctionInterfaceItem
   :parts: 1



.. _vhdlmodel-function:

Function
========

**Condensed definition of class** :class:`~pyVHDLModel.Subprogram.Function`:

.. condensed-class:: pyVHDLModel.Subprogram.Function


.. _vhdlmodel-functioninstantiation:

Function Instantiation
======================

.. todo::

   Write documentation.



.. _vhdlmodel-functionmethod:

Function as Method
==================

**Condensed definition of class** :class:`~pyVHDLModel.Subprogram.FunctionMethod`:

.. condensed-class:: pyVHDLModel.Subprogram.FunctionMethod


.. _vhdlmodel-sub-genericfunction:

Generic Function
================

A generic function is a *regular* function.

.. seealso::

   See :ref:`vhdlmodel-genericfunction` for details.


.. _vhdlmodel-signature:

Signatures
**********

A subprogram's signature (:attr:`Subprogram.Signature <pyVHDLModel.Subprogram.Subprogram.Signature>`) holds the type
marks of its parameters - one per parameter identifier - and of a function's return value; the overloads of a
subprogram differ in it. Its string form is VHDL's notation of a signature (IEEE Std 1076-2019, 4.5.3), e.g.
``[unsigned, positive, positive return natural]``. A type mark's name is given as written
(:attr:`SubtypeSymbol.TypeMark <pyVHDLModel.Symbol.SubtypeSymbol.TypeMark>`): the model doesn't resolve type marks yet.
The signature's parent is its subprogram, which keeps the signature until its parameter list changes.

Two signatures are equal and have the same hash, if their type marks have the same normalized (lower case) names; the
parent isn't compared. So a signature can be used as dictionary key or set member to tell overloads apart. A changed
parameter list gives the subprogram a new signature; a signature already used as key keeps its profile.

.. condensed-class:: pyVHDLModel.Subprogram.SubprogramSignature
