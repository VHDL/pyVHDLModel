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

The writer formats names, symbols, literals and association items. Expressions, declarations, design units and
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
control character. The writer never skips an element. The exception's
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

