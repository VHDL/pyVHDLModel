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
types (:ref:`WRITER/declarations`), context items, design units and documents (:ref:`WRITER/designunits`),
concurrent signal assignments, concurrent procedure calls, concurrent assertions, processes, instantiations, block
statements and generate statements (:ref:`WRITER/concurrent`), and sequential statements (:ref:`WRITER/sequential`).


.. _WRITER/visitor:

Visitor
*******

The writer is a :class:`~pyVHDLModel.Visitor.Visitor`. A model element walks itself
(:meth:`~pyVHDLModel.Base.ModelEntity.Visit`): it reports ``Visit<Class>`` to the visitor, walks its children in source
order and reports ``Depart<Class>``. A token between two parts, which is not a model element itself, is reported by an
event named after the token, e.g. ``VisitArrow`` for ``=>``. A separator is reported by an event named after the list
it separates, so the writer can lay out each kind of list on its own (see :ref:`WRITER/separators`). A part of an
element, which is not a model element itself, is reported by an event pair named after its production in
IEEE Std 1076-2008, e.g. ``VisitGenericClause`` and ``DepartGenericClause`` around the generics of a component. The
writer appends the text of each event to a buffer, which :meth:`~pyVHDLModel.Formatting.VHDL.VHDLWriter.Format`
returns. A parser's subclass of a model class inherits the walk of that model class, so it's written like that model
class.

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


.. _WRITER/style/lists:

List Layout
===========

Each construct with a parenthesized list has its own list style: an
:class:`~pyVHDLModel.Formatting.VHDL.InterfaceListStyle` for an interface list (separated by semicolons) or an
:class:`~pyVHDLModel.Formatting.VHDL.AssociationListStyle` for an association list (separated by commas).

.. list-table::
   :header-rows: 1

   * - Option
     - Construct
     - Default
   * - ``genericClause``
     - generic clauses of entities, components, packages and block statements
     - one generic per line
   * - ``portClause``
     - port clauses of entities, components and block statements
     - one port per line
   * - ``subprogramGenericClause``
     - generic clauses of procedures and functions
     - one generic per line
   * - ``parameterList``
     - formal parameter lists of procedures, functions, generic procedures and generic functions
     - one parameter per line
   * - ``genericMap``
     - generic map aspects of instantiations, block statements, binding indications, package instantiations and
       subprogram instantiations
     - one association per line
   * - ``portMap``
     - port map aspects of instantiations, block statements and binding indications
     - one association per line
   * - ``procedureCall``
     - actual parameter parts of concurrent and sequential procedure calls
     - a single line
   * - ``functionCall``
     - association lists of function calls (:class:`~pyVHDLModel.Name.ParenthesisName`, also an indexed or slice name)
     - a single line

The first four options take an :class:`~pyVHDLModel.Formatting.VHDL.InterfaceListStyle`, the last four an
:class:`~pyVHDLModel.Formatting.VHDL.AssociationListStyle`. Their options are vhdl-style-guide's options of the
subprogram specification rules ``function_019``/``procedure_013`` and of the procedure call rule
``procedure_call_003``, each with the values :attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Add` (``add_new_line``) and
:attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Remove` (``remove_new_line``):

``interfaceElement`` / ``associationElement``
   Line break before each element, the first one after the left parenthesis included (``interface_element`` /
   ``association_element``). Default: :attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Add`, one element per line.

``interfaceListSemicolon`` / ``associationListComma``
   Line break before the separator between two elements (``interface_list_semicolon`` / ``association_list_comma``).
   Default: :attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Remove`, the separator ends the line;
   :attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Add` starts the next line with it.

``lastCloseParen``
   Line break before the right parenthesis (``last_close_paren``). Default:
   :attr:`~pyVHDLModel.Formatting.VHDL.NewLine.Add`, on its own line.

The procedure call and function call styles are ``AssociationListStyle(NewLine.Remove, NewLine.Remove,
NewLine.Remove)``. See vhdl-style-guide's :ref:`vsg:configuring-subprogram-specification-statement-rules` and
:ref:`vsg:configuring-procedure-call-statement-rules`.

.. code-block:: Python

   from pyVHDLModel.Formatting.VHDL import InterfaceListStyle, NewLine, VHDLStyle, VHDLWriter

   writer = VHDLWriter(VHDLStyle(
     genericClause=InterfaceListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove),
     portClause=InterfaceListStyle(NewLine.Remove, NewLine.Add)
   ))

.. code-block:: VHDL

   component counter is
     generic (BITS : positive := 8; type T);
     port (clk, rst : in bit
       ; q : out T
     );
   end component counter;


.. _WRITER/separators:

Separators and Parentheses
**************************

Each list reports the separator between two of its items by an event named after the list:

.. list-table::
   :header-rows: 1

   * - Event
     - Separator
     - Lists
     - Written as
   * - ``VisitInterfaceListSeparator``
     - ``;``
     - generic clause, port clause, formal parameter list
     - by the construct's list style (:ref:`WRITER/style/lists`), by default ``;`` and a new line
   * - ``VisitAssociationListSeparator``
     - ``,``
     - associations of a parenthesis name, generic and port map aspects, actual parameters of a procedure call
     - by the construct's list style, by default ``,`` and a new line in a map aspect, otherwise ``,`` and a space
   * - ``VisitElementSeparator``
     - ``,``
     - indices of an indexed name, element associations of an aggregate, index and record constraints, literals of an
       enumerated type, index ranges of an array type
     - ``,`` and a space
   * - ``VisitNameListSeparator``
     - ``,``
     - entity name list of an attribute specification, names of a library clause, use clause or context reference,
       instantiation list, sensitivity list of a process or wait statement
     - ``,`` and a space
   * - ``VisitWaveformSeparator``
     - ``,``
     - waveform elements of a waveform
     - ``,`` and a space
   * - ``VisitSelectedAlternativeSeparator``
     - ``,``
     - alternatives of selected waveforms and selected expressions
     - ``,`` and a space

The parentheses of a list are written at the events of its element or part, e.g. ``VisitIndexList`` and
``DepartIndexList`` around the indices of an indexed name, ``VisitAssociationList`` and ``DepartAssociationList`` around
the associations of a parenthesis name, or ``VisitGenericClause`` and ``DepartGenericClause``. ``VisitLeftParenthesis``
and ``VisitRightParenthesis`` enclose a single item, which is no list: the operand of a type conversion or the
architecture name of an entity aspect.


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
   By default, each item of a generic clause or a port clause is written on its own line
   (:ref:`WRITER/style/lists`); the items are separated by semicolons.
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
   an empty subprogram body (e.g. in a package body or an architecture). A subprogram body has a declarative part and a
   statement part. By default, each parameter is written on its own line. A generic clause of a subprogram is followed
   by the reserved word ``parameter`` before the parameter list. Generic procedures and functions are written in a
   generic clause like any other generic. A method of a protected type is written like a procedure or function.

Subprogram instantiations
   Procedure and function instantiations are written with their generic map aspect, by default one association per
   line.

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
``begin``.

A configuration writes its block configuration, nested block configurations and component configurations, each ending
with ``end for;``. A binding indication (``use entity work.sub(rtl)``) and its map aspects are indented one level deeper
than its component configuration; by default, each association of a map aspect is written on its own line.


.. _WRITER/concurrent:

Concurrent Statements
*********************

A concurrent statement is written on its own line, starting with its label, if any (``mux : ...``).

Signal assignments
   Simple, conditional and selected signal assignments are written on one line. The waveform elements of a waveform
   are separated by commas, a delay follows the reserved word ``after``. The alternatives of a conditional signal
   assignment are separated by the reserved word ``else``, the alternatives of a selected signal assignment by
   commas; choices are separated by vertical lines (``when 1 | 2 to 3``).

Procedure calls and assertions
   A concurrent procedure call is written with its parameter associations in parentheses, if it has any; an assertion
   with its report and severity, if given.

Processes
   A process is written with its sensitivity list, if any, the reserved word ``is``, its declared items, ``begin`` and
   its statements. A sensitivity list consisting of a single :class:`~pyVHDLModel.Name.AllName` without prefix is
   written as ``process (all)``.

.. code-block:: VHDL

   count : process (clk, rst) is
     variable value : natural := 0;
   begin
   end process count;

Instantiations
   Component, entity and configuration instantiations are written with the reserved word ``component``, ``entity`` or
   ``configuration``, followed by their generic and port map aspects, by default one association per line. An
   instantiation without label raises :exc:`~pyVHDLModel.Exception.VHDLWriterError`.

Block statements
   A block statement writes its block header (generic clause, generic map aspect, port clause, port map aspect), its
   declared items, ``begin`` and its statements; each map aspect of the header ends with a semicolon.

Generate statements
   If-generate, case-generate and for-generate statements are written with their branches or alternatives and
   ``end generate``. A branch or alternative with declared items writes ``begin`` before its statements; alternative
   labels are written before the condition or the choices (``elsif middle : BITS > 4 generate``). A block or generate
   statement without label raises :exc:`~pyVHDLModel.Exception.VHDLWriterError`.

.. code-block:: VHDL

   gen : case MODE generate
     when 0 | 1 to 2 =>
       q <= a;
     when others =>
       signal t : bit;
     begin
       q <= t;
   end generate gen;


.. _WRITER/sequential:

Sequential Statements
*********************

A sequential statement is written on its own line in the statement part of a process or subprogram body, starting
with its label, if any.

Assignments
   Simple, conditional and selected signal and variable assignments, force assignments (``q <= force '1';``) and
   release assignments (``q <= release;``). The alternatives are written as for concurrent signal assignments.

Other statements
   Procedure calls, report statements, assertions, null statements, return statements with and without value, and wait
   statements with their sensitivity clause (``on``), condition clause (``until``) and timeout clause (``for``), if
   given.

Compound statements
   If statements with their branches, case statements with their alternatives, and loops (for, while and without
   iteration scheme) write the statements they contain on their own lines, indented one level deeper, and end with
   ``end if``, ``end case`` or ``end loop`` and the label, if any. Next and exit statements are written with their
   condition, if any; the model keeps no loop label for them, so none is written.

.. code-block:: VHDL

   p : process is
     variable v : natural := 0;
   begin
     increment : v := v + 1;
     q <= d after 1 ns;
     outer : for i in 0 to 3 loop
       next when skip;
       if v = 0 then
         null;
       end if;
     end loop outer;
     wait on d until d = '1' for 10 ns;
   end process p;
