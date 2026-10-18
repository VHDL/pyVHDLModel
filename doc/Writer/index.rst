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


.. _WRITER/dispatch:

Dispatch
********

:meth:`~pyVHDLModel.Formatting.VHDL.VHDLWriter.Format` looks up a formatter method along the class hierarchy (MRO) of
the element. Thus, a parser's subclass of a model class is written like that model class.

An element without a formatter raises :exc:`~pyVHDLModel.Exception.VHDLWriterError`, so does an element without VHDL
notation, e.g. a string literal containing a control character. The writer never skips an element. The exception's
:attr:`~pyVHDLModel.Exception.VHDLWriterError.Element` property returns the offending element.

A symbol is written from its name, whether it's resolved or not.


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

