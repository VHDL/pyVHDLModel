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

The writer formats names, symbols, literals, expressions, association items, subtype indications, object
declarations, interface items, component declarations, mode view declarations, type and subtype declarations, alias
declarations, attribute declarations and attribute specifications, subprograms, subprogram instantiations and protected
types (:ref:`WRITER/declarations`), context items, design units and documents (:ref:`WRITER/designunits`). Statements
follow.


.. _WRITER/visitor:

Visitor
*******

The writer is a :class:`~pyVHDLModel.Visitor.Visitor`. A model element walks itself
(:meth:`~pyVHDLModel.Base.ModelEntity.Visit`): it reports ``Visit<Class>`` to the visitor, walks its children in source
order and reports ``Depart<Class>``. A token between two parts, which is not a model element itself, is reported by an
event named after the token, e.g. ``VisitArrow`` for ``=>`` or ``VisitComma`` for ``,``. A part of an element, which is
not a model element itself, is reported by an event pair named after its production in IEEE Std 1076-2008, e.g.
``VisitGenericClause`` and ``DepartGenericClause`` around the generics of a component. The writer appends the text of
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
   Letter case of reserved words - the members of :class:`~pyVHDLModel.Base.ReservedWord`, which the writer writes
   them from: :attr:`~pyVHDLModel.Formatting.VHDL.KeywordCase.Lower` (default) or
   :attr:`~pyVHDLModel.Formatting.VHDL.KeywordCase.Upper`. Identifiers keep their letter case. See vhdl-style-guide's
   :ref:`vsg:configuring-uppercase-and-lowercase-rules`.

``indentStyle``
   Indentation style, as vhdl-style-guide's option ``indent_style``:
   :attr:`~pyVHDLModel.Formatting.VHDL.IndentStyle.Spaces` (default, ``spaces``) or
   :attr:`~pyVHDLModel.Formatting.VHDL.IndentStyle.SmartTabs` (``smart_tabs``: one tab per indentation level). See
   vhdl-style-guide's :ref:`vsg:configuring-indent-rules`.

``indentSize``
   Number of spaces per indentation level, as vhdl-style-guide's option ``indent_size`` (default: ``2``). It applies to
   :attr:`~pyVHDLModel.Formatting.VHDL.IndentStyle.Spaces`.

.. code-block:: Python

   from pyVHDLModel.Formatting.VHDL import IndentStyle, KeywordCase, VHDLStyle, VHDLWriter

   writer = VHDLWriter(VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs))


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


.. _WRITER/declarations:

Declarations
************

A declaration is written on its own line, indented by its nesting level, and ends with a newline. A declaration
containing other items (e.g. a component declaration) writes each item on its own line, indented one level deeper, and
ends with ``end``, the reserved word of the declaration and its identifier:

.. code-block:: VHDL

   component counter is
     generic (
       BITS : positive := 8;
       type T
     );
     port (
       clk, rst : in bit;
       q : out T
     );
   end component counter;

Subtype indications
   A constrained subtype symbol is written with its constraint: a range constraint
   (:class:`~pyVHDLModel.Symbol.ConstrainedScalarSubtypeSymbol`, ``integer range 0 to 7``), an index constraint
   (:class:`~pyVHDLModel.Symbol.ConstrainedArraySubtypeSymbol`, ``bit_vector(7 downto 0)``) or a record constraint
   (:class:`~pyVHDLModel.Symbol.ConstrainedRecordSubtypeSymbol`, ``frame_t(data(7 downto 0))``).

Object declarations
   Constants, deferred constants, variables, shared variables, signals and files are written with their identifiers,
   their subtype indication and, if present, their default expression. The model has no file open information, so a
   file declaration is written without one.

Interface items
   Each item of a generic clause or a port clause is written on its own line; the items are separated by semicolons.
   A clause without items is not written. Generic constants and ports are written without an object class reserved word
   (``BITS : positive``, ``clk : in bit``), parameters with one (``signal clk : in bit``). An item with
   :attr:`Mode.Default <pyVHDLModel.Base.Mode.Default>` is written without a mode. Ports and parameters with a mode view
   (VHDL-2019) are written with the reserved word ``view`` (``link : view master``).

Mode view declarations
   A mode view declaration (VHDL-2019) is written with one element per line. An element without a mode raises
   :exc:`~pyVHDLModel.Exception.VHDLWriterError`.

Type and subtype declarations
   Enumerated, integer, floating-point, physical, array, record, access, file and incomplete type declarations
   (:class:`~pyVHDLModel.Type.AnonymousType`, ``type node;``) and subtype declarations. A physical type writes its
   units and a record type its element declarations one per line. An index of an array type, which is a
   :class:`~pyVHDLModel.Symbol.SimpleSubtypeSymbol`, is an unbounded index (``natural range <>``); any other index is a
   range. The model's resolution function of a subtype declaration is not written.

Alias and attribute declarations
   Alias declarations with and without subtype indication, attribute declarations and attribute specifications. The
   entity class :attr:`EntityClass.Others <pyVHDLModel.Declaration.EntityClass.Others>` has no VHDL notation and raises
   :exc:`~pyVHDLModel.Exception.VHDLWriterError`.

Subprograms
   The model doesn't distinguish a subprogram declaration from a subprogram body. A procedure or function with declared
   items or statements is written as a subprogram body. One without them is written as a subprogram declaration
   (``procedure reset;``), if its parent is a package declaration, a protected type declaration or none, otherwise as
   an empty subprogram body (e.g. in a package body or an architecture). A subprogram
   body has a declarative part and a statement part; statements have no walk yet, so a subprogram with statements raises
   :exc:`NotImplementedError`. Each parameter is written on its own line. A generic clause of a subprogram is followed
   by the reserved word ``parameter`` before the parameter list. Generic procedures and functions are written in a
   generic clause like any other generic. A method of a protected type is written like a procedure or function.

Subprogram instantiations
   Procedure and function instantiations are written with their generic map aspect, one association per line.

Protected types
   A protected type declaration writes its methods, a protected type body its declared items, one per line.

.. code-block:: VHDL

   function maximum generic (
     type T
   ) parameter (
     constant a, b : T
   ) return T;

Documentation comments of the model (:attr:`~pyVHDLModel.Base.DocumentedEntityMixin.Documentation`) are not written.


.. _WRITER/designunits:

Design Units
************

:meth:`~pyVHDLModel.Formatting.VHDL.VHDLWriter.Format` of a :class:`~pyVHDLModel.Document` writes all its design units
in the document's order, separated by a blank line. Each design unit is preceded by its context items (library clauses,
use clauses and context references), followed by a blank line.

.. code-block:: VHDL

   library ieee;
   use ieee.std_logic_1164.all;

   entity counter is
     generic (
       BITS : positive := 8
     );
     port (
       clk : in std_logic;
       count : out natural
     );
   end entity counter;

   architecture rtl of counter is
     signal value : natural := 0;
   begin
   end architecture rtl;

Entities, architectures, packages, package bodies, package instantiations, context declarations and configurations are
written with ``end``, the reserved words of the design unit and its identifier. An entity without statements has no
``begin``. Concurrent statements have no walk yet, so an entity or architecture with statements raises
:exc:`NotImplementedError`.

A configuration writes its block configuration, nested block configurations and component configurations, each ending
with ``end for;``. A binding indication (``use entity work.sub(rtl)``) and its map aspects are indented one level deeper
than its component configuration; each association of a map aspect is written on its own line.
