.. _WRITER:

VHDL Writer
###########

:class:`~pyVHDLModel.Formatting.VHDL.VHDLWriter` writes elements of a VHDL language model as VHDL source text. It works
on models built by hand as well as on models created by a parser like ``pyGHDL.dom``.

.. code-block:: Python

   from pyVHDLModel.Association     import ParameterAssociationItem
   from pyVHDLModel.Expression      import IntegerLiteral
   from pyVHDLModel.Formatting.VHDL import VHDLWriter
   from pyVHDLModel.Name            import SimpleName, ParenthesisName
   from pyVHDLModel.Symbol          import IndexedObjectOrFunctionCallSymbol, SimpleObjectOrFunctionCallSymbol

   call = IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("resize"), [
     ParameterAssociationItem(None, SimpleObjectOrFunctionCallSymbol(SimpleName("count"))),
     ParameterAssociationItem(SimpleName("new_size"), IntegerLiteral(8))
   ]))

   writer = VHDLWriter()
   print(writer.Format(call))   # resize(count, new_size => 8)

Writing is a re-format, not a round-trip: comments, blank lines, the letter case of reserved words and the notation of
abstract literals (e.g. ``16#FF#`` becomes ``255``) are not preserved.

.. rubric:: Supported language constructs

The writer formats names, symbols, literals, expressions and association items. Declarations, design units and
statements follow.


.. _WRITER/visitor:

Visitor
*******

The writer is a :class:`~pyVHDLModel.Visitor.Visitor`. A model element walks itself
(:meth:`~pyVHDLModel.Base.ModelEntity.Visit`): it reports ``Visit<Class>`` to the visitor, walks its children in source
order and reports ``Depart<Class>``. A token between two parts, which is not a model element itself, is reported by an
event named after the token, e.g. ``VisitArrow`` for ``=>`` or ``VisitComma`` for ``,``. The writer appends the text of
each event to a buffer, which :meth:`~pyVHDLModel.Formatting.VHDL.VHDLWriter.Format` returns. A parser's subclass of a
model class inherits the walk of that model class, so it's written like that model class.

An element of a class without a walk of its own raises :exc:`NotImplementedError` when it is visited. The writer raises
:exc:`~pyVHDLModel.Exception.VHDLWriterError` for an element without VHDL notation, e.g. a string literal containing a
control character or an aggregate with a single positional element. The writer never skips an element. The exception's
:attr:`~pyVHDLModel.Exception.VHDLWriterError.Element` property returns the offending element.

A symbol is written from its name, whether it's resolved or not.

Every event of :class:`~pyVHDLModel.Visitor.Visitor` does nothing, so another visitor overrides only the events it
needs:

.. code-block:: Python

   from typing              import List

   from pyVHDLModel.Name    import SimpleName
   from pyVHDLModel.Visitor import Visitor

   class SimpleNameCollector(Visitor):
     _identifiers: List[str]

     def __init__(self) -> None:
       super().__init__()
       self._identifiers = []

     def VisitSimpleName(self, name: SimpleName) -> None:
       self._identifiers.append(name.Identifier)


.. _WRITER/style:

Formatting Options
******************

:class:`~pyVHDLModel.Formatting.VHDL.VHDLStyle` holds the formatting options passed to the writer.

``keywordCase``
   Letter case of reserved words: :attr:`~pyVHDLModel.Formatting.VHDL.KeywordCase.Lower` (default) or
   :attr:`~pyVHDLModel.Formatting.VHDL.KeywordCase.Upper`. Identifiers keep their letter case.

.. code-block:: Python

   from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter

   writer = VHDLWriter(VHDLStyle(KeywordCase.Upper))


.. _WRITER/parentheses:

Parentheses
***********

The model represents an expression as a tree, so it needs no parentheses. The writer adds the parentheses VHDL's
grammar requires (IEEE Std 1076-2008, clauses 9.1 and 9.2). Parentheses from the source, represented by
:class:`~pyVHDLModel.Expression.SubExpression`, are kept. Each operator class names its precedence level
(:class:`~pyVHDLModel.Expression.OperatorPrecedence`) in the class variable ``_PRECEDENCE``.

.. code-block:: Python

   from pyVHDLModel.Expression      import AdditionExpression, MultiplyExpression
   from pyVHDLModel.Formatting.VHDL import VHDLWriter
   from pyVHDLModel.Name            import SimpleName
   from pyVHDLModel.Symbol          import SimpleObjectOrFunctionCallSymbol

   def obj(name: str) -> SimpleObjectOrFunctionCallSymbol:
     return SimpleObjectOrFunctionCallSymbol(SimpleName(name))

   expression = MultiplyExpression(AdditionExpression(obj("a"), obj("b")), obj("c"))
   print(VHDLWriter().Format(expression))   # (a + b) * c

.. list-table:: Precedence levels (:class:`~pyVHDLModel.Expression.OperatorPrecedence`), loosest first
   :header-rows: 1

   * - Level
     - Operators
     - Operands without parentheses
   * - ``Logical``
     - ``and``, ``or``, ``xor``, ``xnor``, ``nand``, ``nor``
     - relations; a chain of the same operator, except ``nand`` and ``nor``
   * - ``Relational``
     - ``=``, ``/=``, ``<``, ``<=``, ``>``, ``>=``, ``?=``, ``?/=``, ``?<``, ``?<=``, ``?>``, ``?>=``
     - shift expressions
   * - ``Shift``
     - ``sll``, ``srl``, ``sla``, ``sra``, ``rol``, ``ror``
     - simple expressions
   * - ``Adding``
     - ``+``, ``-``, ``&``, and the signs ``+``, ``-``
     - left: simple expression; right: term; a sign's operand: term
   * - ``Multiplying``
     - ``*``, ``/``, ``mod``, ``rem``
     - left: term; right: factor
   * - ``Miscellaneous``
     - ``**``, ``abs``, ``not``, unary logical operators
     - primaries

Examples:

* ``(a + b) * c`` and ``a + b * c``
* ``a - (b - c)`` and ``a - b - c``
* ``a ** (b ** c)``, because ``a ** b ** c`` is illegal
* ``(a and b) or c``, because different logical operators can't be mixed
* ``a + (-b)``, because a sign can only start a simple expression; a negative number literal is written with a sign,
  too: ``a - (-1)``
