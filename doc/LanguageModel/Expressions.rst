.. _vhdlmodel-expr:

Literals and Expressions
########################

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.NullLiteral
                         pyVHDLModel.Expression.EnumerationLiteral
                         pyVHDLModel.Expression.CharacterEnumerationLiteral
                         pyVHDLModel.Expression.IntegerLiteral
                         pyVHDLModel.Expression.FloatingPointLiteral
                         pyVHDLModel.Expression.PhysicalIntegerLiteral
                         pyVHDLModel.Expression.PhysicalFloatingLiteral
                         pyVHDLModel.Expression.CharacterLiteral
                         pyVHDLModel.Expression.StringLiteral
                         pyVHDLModel.Expression.BinaryBitStringLiteral
                         pyVHDLModel.Expression.OctalBitStringLiteral
                         pyVHDLModel.Expression.DecimalBitStringLiteral
                         pyVHDLModel.Expression.HexadecimalBitStringLiteral
   :parts: 1

.. _vhdlmodel-literals:

Literals
********

.. _vhdlmodel-enumerationliteral:

Enumeration Literal
===================

.. todo::

   Write documentation.



.. _vhdlmodel-integerliteral:

Integer Literal
===============

.. todo::

   Write documentation.



.. _vhdlmodel-realliteral:

Floating Point Literal
======================

.. todo::

   Write documentation.



.. _vhdlmodel-physicalliteral:

Physical Literal
================

.. todo::

   Write documentation.



.. _vhdlmodel-expressions:

Expressions
***********

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.UnaryExpression
                         pyVHDLModel.Expression.AddingExpression
                         pyVHDLModel.Expression.MultiplyingExpression
                         pyVHDLModel.Expression.LogicalExpression
                         pyVHDLModel.Expression.RelationalExpression
                         pyVHDLModel.Expression.ShiftExpression
                         pyVHDLModel.Expression.RangeExpression
                         pyVHDLModel.Expression.TernaryExpression
                         pyVHDLModel.Expression.QualifiedExpression
                         pyVHDLModel.Expression.FunctionCall
                         pyVHDLModel.Expression.SubtypeAllocation
                         pyVHDLModel.Expression.QualifiedExpressionAllocation
                         pyVHDLModel.Expression.Aggregate
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-unary:

Unary Expressions
=================

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.InverseExpression
                         pyVHDLModel.Expression.IdentityExpression
                         pyVHDLModel.Expression.NegationExpression
                         pyVHDLModel.Expression.AbsoluteExpression
                         pyVHDLModel.Expression.ConditionExpression
                         pyVHDLModel.Expression.UnaryAndExpression
                         pyVHDLModel.Expression.UnaryNandExpression
                         pyVHDLModel.Expression.UnaryOrExpression
                         pyVHDLModel.Expression.UnaryNorExpression
                         pyVHDLModel.Expression.UnaryXorExpression
                         pyVHDLModel.Expression.UnaryXnorExpression
                         pyVHDLModel.Expression.TypeConversion
                         pyVHDLModel.Expression.SubExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-binary:

Binary Expressions
==================

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.AddingExpression
                         pyVHDLModel.Expression.MultiplyingExpression
                         pyVHDLModel.Expression.LogicalExpression
                         pyVHDLModel.Expression.RelationalExpression
                         pyVHDLModel.Expression.ShiftExpression
                         pyVHDLModel.Expression.RangeExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-addingexpression:

Adding Expressions
------------------

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.AdditionExpression
                         pyVHDLModel.Expression.SubtractionExpression
                         pyVHDLModel.Expression.ConcatenationExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-multiplyingexpressions:

Multiplying Expressions
-----------------------

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.MultiplyExpression
                         pyVHDLModel.Expression.DivisionExpression
                         pyVHDLModel.Expression.RemainderExpression
                         pyVHDLModel.Expression.ModuloExpression
                         pyVHDLModel.Expression.ExponentiationExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-logicalexpressions:

Logical Expressions
-------------------

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.AndExpression
                         pyVHDLModel.Expression.NandExpression
                         pyVHDLModel.Expression.OrExpression
                         pyVHDLModel.Expression.NorExpression
                         pyVHDLModel.Expression.XorExpression
                         pyVHDLModel.Expression.XnorExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-relationalexpressions:

Relational Expressions
----------------------

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.EqualExpression
                         pyVHDLModel.Expression.UnequalExpression
                         pyVHDLModel.Expression.GreaterThanExpression
                         pyVHDLModel.Expression.GreaterEqualExpression
                         pyVHDLModel.Expression.LessThanExpression
                         pyVHDLModel.Expression.LessEqualExpression
                         pyVHDLModel.Expression.MatchingEqualExpression
                         pyVHDLModel.Expression.MatchingUnequalExpression
                         pyVHDLModel.Expression.MatchingGreaterThanExpression
                         pyVHDLModel.Expression.MatchingGreaterEqualExpression
                         pyVHDLModel.Expression.MatchingLessThanExpression
                         pyVHDLModel.Expression.MatchingLessEqualExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-shiftingexpressions:

Shifting Expressions
--------------------

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.ShiftRightLogicExpression
                         pyVHDLModel.Expression.ShiftLeftLogicExpression
                         pyVHDLModel.Expression.ShiftRightArithmeticExpression
                         pyVHDLModel.Expression.ShiftLeftArithmeticExpression
                         pyVHDLModel.Expression.RotateRightExpression
                         pyVHDLModel.Expression.RotateLeftExpression
   :parts: 1

.. todo::

   Write documentation.



.. _vhdlmodel-ternary:

Ternary Expressions
===================

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Expression.WhenElseExpression
   :parts: 1

.. todo::

   Write documentation.
