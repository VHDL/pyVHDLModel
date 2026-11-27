.. _NEWS:

News
####

See :gh:`pyVHDLModel Release Pages <VHDL/pyVHDLModel/releases>` for detail release notes on every release.


Version 0.45.0 (2026)
*********************

.. topic:: :gh:`v0.45.0 - unreleased <VHDL/pyVHDLModel/releases/v0.45.0>`

   .. rubric:: New Features

   * New class :class:`~pyVHDLModel.Subprogram.Operator`: a function whose designator is an operator symbol.
   * A full type declares its predefined operations (IEEE Std 1076-2008, 5) as
     :class:`~pyVHDLModel.Subprogram.PredefinedOperator` and :class:`~pyVHDLModel.Subprogram.PredefinedFunction`
     objects (:data:`~pyVHDLModel.Type.FullType.ImplicitOperations`): equality for every type except file and protected
     types; ordering, ``MINIMUM``, ``MAXIMUM`` and ``TO_STRING`` for scalar types; the arithmetic operators of integer,
     floating-point and physical types. The analysis indexes them after the type marks are resolved (see *Changes*).
   * Package ``std.standard`` declares what IEEE Std 1076-2008, 16.3 lists, in its order: new are the subtype
     ``delay_length``, the function ``now``, the type ``real_vector`` and the attribute ``foreign``. The types
     ``boolean`` and ``bit`` (:class:`~pyVHDLModel.STD.Boolean`, :class:`~pyVHDLModel.STD.Bit`) declare the logical
     operators, ``bit`` also the condition operator ``??`` and the matching relational operators.
   * Package ``std.textio`` declares what IEEE Std 1076-2008, 16.4 lists, in its order: the types ``text`` and
     ``side``, the subtype ``width``, the function ``justify``, the files ``input`` and ``output``, and the procedures
     ``readline``, ``read``, ``sread``, ``oread``, ``hread``, ``writeline``, ``tee``, ``write``, ``owrite`` and
     ``hwrite`` with all their overloads. The aliases (``bread``, ``swrite``, ...) aren't declared yet.
   * Package ``std.env`` declares what IEEE Std 1076-2008, 16.5 lists: the procedures ``stop`` and ``finish``, each
     with and without a ``STATUS`` parameter, and the function ``resolution_limit``.
   * A one-dimensional array type declares, depending on its element type, the concatenation operator ``&``, the
     ordering operators and ``MINIMUM``/``MAXIMUM`` (discrete elements), ``MINIMUM``/``MAXIMUM`` of its elements
     (scalar elements), the logical, shift and logical reduction operators (``bit``, ``boolean``), the matching
     operators ``?=``/``?/=`` (``bit``) and ``TO_STRING`` (elements of a character type with only character literals).
     The new :class:`~pyVHDLModel.Type.MatchingOperatorsMixin` marks the element types with matching operators.
   * Package ``ieee.math_real`` declares what IEEE Std 1076-2008, 16.8.2 lists: the constant ``copyrightnotice``, the
     mathematical constants (``math_e``, ``math_pi``, ...), the functions and operators ``"mod"`` and ``"**"`` on
     ``real``, and the procedure ``uniform``.
   * Package ``ieee.math_complex`` (:class:`~pyVHDLModel.IEEE.MathComplex.Math_Complex`) declares what IEEE Std
     1076-2008, 16.8.3 lists, in its order: the record types ``complex`` and ``complex_polar``, the subtypes
     ``positive_real`` and ``principal_value``, the constants ``math_cbase_1``, ``math_cbase_j`` and ``math_czero``, and
     58 operators and functions, e.g. ``"+"`` of two complex numbers or of a complex number and a ``real``.
   * Package ``ieee.numeric_std`` (:class:`~pyVHDLModel.IEEE.NumericStd.Numeric_Std`) declares what the VHDL-2008
     package lists, in its order: the constant ``CopyRightNotice``, the subtypes ``u_unsigned`` and ``u_signed``, 232
     functions (arithmetic, relational, matching, shift, conversion and logical operators and functions) and 18
     procedures (``read``, ``write``, ``oread``, ``hread``, ``owrite``, ``hwrite``). The aliases (``to_bstring``,
     ``bread``, ...) aren't declared yet. Its declarations have the package as parent.
   * Package ``ieee.numeric_bit`` (:class:`~pyVHDLModel.IEEE.NumericBit.Numeric_Bit`) declares what the VHDL-2008
     package lists, in its order: the constant ``CopyRightNotice``, the types ``unsigned`` and ``signed``, 218
     functions (arithmetic, relational, matching, shift, conversion and logical operators and functions) and 18
     procedures (``read``, ``write``, ``oread``, ``hread``, ``owrite``, ``hwrite``). The aliases (``rising_edge``,
     ``to_bstring``, ``bread``, ...) aren't declared yet. Its declarations have the package as parent.
   * Package ``ieee.std_logic_1164`` declares what IEEE Std 1076-2008, 16.7 lists, in its order: the types
     ``std_ulogic`` (:class:`~pyVHDLModel.IEEE.StdLogic1164.StdULogic`, with the matching relational operators) and
     ``std_ulogic_vector``, the function ``resolved``, the subtypes ``std_logic``, ``std_logic_vector``, ``x01``,
     ``x01z``, ``ux01``, ``ux01z``, the logical and shift operators, the conversion functions, ``"??"``,
     ``rising_edge``, ``falling_edge``, ``is_x``, ``to_ostring``, ``to_hstring`` and the ``read``/``write`` procedures.
     The aliases (``to_slv``, ``to_bstring``, ``bread``, ...) aren't declared yet.
   * Package ``ieee.numeric_std_unsigned`` (:class:`~pyVHDLModel.IEEE.NumericStdUnsigned.Numeric_Std_Unsigned`)
     declares what the VHDL-2008 package lists, in its order: the constant ``CopyRightNotice`` and 79 functions
     (arithmetic, relational, matching, shift and conversion operators and functions on ``std_ulogic_vector``). The
     aliases (``to_slv``, ``to_sulv``, ...) aren't declared yet. Its declarations have the package as parent.
   * Package ``ieee.numeric_bit_unsigned`` (:class:`~pyVHDLModel.IEEE.NumericBitUnsigned.Numeric_Bit_Unsigned`)
     declares what the VHDL-2008 package lists, in its order: the constant ``CopyRightNotice`` and 81 functions
     (arithmetic, relational, matching, shift and conversion operators and functions on ``bit_vector``). The aliases
     (``to_bit_vector``, ``to_bv``) aren't declared yet. Its declarations have the package as parent.
   * Package ``ieee.fixed_float_types`` (:class:`~pyVHDLModel.IEEE.FixedFloatTypes.Fixed_Float_Types`) declares the
     enumerated types ``fixed_round_style_type``, ``fixed_overflow_style_type`` and ``round_type``.
   * Package ``ieee.fixed_generic_pkg`` (:class:`~pyVHDLModel.IEEE.FixedGenericPkg.Fixed_Generic_Pkg`) declares the
     generics ``fixed_round_style``, ``fixed_overflow_style``, ``fixed_guard_bits`` and ``no_warning``, the constant
     ``CopyRightNotice``, the types ``unresolved_ufixed`` and ``unresolved_sfixed``, the aliases ``u_ufixed`` and
     ``u_sfixed``, the subtypes ``ufixed`` and ``sfixed``, the arithmetic operators and functions (``divide``,
     ``reciprocal``, ``remainder``, ``modulo``, ``add_carry``, ``scalb``, ``is_negative``), the relational and matching
     operators, ``std_match``, ``maximum``, ``minimum``, the shift operators, ``shift_left``, ``shift_right``, the
     logical operators, the conversion functions, ``resize``, ``saturate``, ``to_01``, ``is_x``, the ``read``/``write``
     procedures, ``to_string`` and ``from_string`` with their octal and hexadecimal variants: 401 declarations in the
     package's order. The aliases of subprograms (``to_stdlogicvector``, ``bread``, ``to_bstring``, ...) aren't declared
     yet.
   * Package ``ieee.fixed_pkg`` (:class:`~pyVHDLModel.IEEE.FixedPkg.Fixed_Pkg`) instantiates ``ieee.fixed_generic_pkg``
     with the generic map of IEEE Std 1076-2008, 16.10: a use clause ``use ieee.fixed_pkg.all;`` makes ``ufixed``,
     ``to_ufixed``, ... visible. New base class :class:`~pyVHDLModel.Predefined.PredefinedPackageInstantiation` for
     predefined package instantiations.
   * An interface package (:class:`~pyVHDLModel.Interface.GenericPackageInterfaceItem`) holds its uninstantiated
     package (:data:`~pyVHDLModel.Interface.InterfacePackage.PackageReference`) and the form of its generic map aspect
     (:class:`~pyVHDLModel.Interface.InterfacePackageGenericMap`: ``<>``, ``default`` or associations). The analysis
     links the package, and a use clause naming the interface package (``use fixed_pkg.all;``) imports the declarations
     of the generic package.
   * Package ``ieee.float_generic_pkg`` (:class:`~pyVHDLModel.IEEE.FloatGenericPkg.Float_Generic_Pkg`) declares the
     generics (``float_exponent_width`` ... ``no_warning`` and the package generic ``fixed_pkg``), the constant
     ``CopyRightNotice``, the use clause ``use fixed_pkg.all;``, the type ``unresolved_float``, the subtypes ``float``,
     ``float32``, ``float64``, ``float128`` (and their unresolved forms and aliases), the type ``valid_fpstate``, the
     deferred constant ``fphdlsynth_or_real``, ``classfp``, the arithmetic operators and functions, the comparison
     functions and relational operators, ``resize``, the conversion functions, ``to_01``, ``is_x``, ``break_number``,
     ``normalize``, the operators with ``real`` and ``integer`` operands, the logical operators, ``copysign``,
     ``scalb``, ``logb``, ``nextafter``, the special values (``zerofp``, ``nanfp``, ...), the ``read``/``write``
     procedures, ``to_string`` and ``from_string`` with their octal and hexadecimal variants: 247 declarations in the
     package's order. The aliases of subprograms (``to_stdlogicvector``, ``bread``, ``to_bstring``, ...) aren't declared
     yet.
   * Package ``ieee.float_pkg`` (:class:`~pyVHDLModel.IEEE.FloatPkg.Float_Pkg`) instantiates ``ieee.float_generic_pkg``
     with the generic map of IEEE Std 1076-2008, 16.11, ``fixed_pkg => IEEE.fixed_pkg`` included: a use clause
     ``use ieee.float_pkg.all;`` makes ``float32``, ``to_float``, ... visible.
   * Library ``ieee`` declares the contexts ``ieee_std_context``
     (:class:`~pyVHDLModel.IEEE.IeeeStdContext.Ieee_Std_Context`) and ``ieee_bit_context``
     (:class:`~pyVHDLModel.IEEE.IeeeBitContext.Ieee_Bit_Context`) of IEEE Std 1076-2008, 16.9.
     New base class :class:`~pyVHDLModel.Predefined.PredefinedContext` and
     :meth:`PredefinedLibrary.AddContexts() <pyVHDLModel.Predefined.PredefinedLibrary.AddContexts>`.
   * Synopsys package ``ieee.std_logic_unsigned`` (:class:`~pyVHDLModel.IEEE.StdLogicUnsigned.Std_Logic_Unsigned`,
     loaded with :data:`IEEEFlavor.Synopsys <pyVHDLModel.IEEEFlavor.Synopsys>`) declares its 33 operators and functions
     (arithmetic and relational operators on ``std_logic_vector``, ``shl``, ``shr``, ``conv_integer``). The module
     carries Synopsys' copyright notice, as the package requires for derivative work.
   * Synopsys package ``ieee.std_logic_signed`` (:class:`~pyVHDLModel.IEEE.StdLogicSigned.Std_Logic_Signed`) declares
     its 35 operators and functions (as ``std_logic_unsigned``, and the unary ``"-"`` and ``"abs"``), with Synopsys'
     copyright notice.
   * Synopsys package ``ieee.std_logic_misc`` (:class:`~pyVHDLModel.IEEE.StdLogicMisc.Std_Logic_Misc`) declares the
     types ``strength`` and ``minomax`` and its 29 functions (``strength_map``, ``drive``, ``sense``, the conversions to
     ``bit``/``bit_vector``, the reduction functions ``and_reduce`` ..., ``fun_buf3s`` ...), with Synopsys' copyright
     notice.
   * Synopsys package ``ieee.std_logic_textio`` (:class:`~pyVHDLModel.IEEE.StdLogicTextIO.Std_Logic_TextIO_Synopsys`)
     declares its 21 procedures (``read``, ``write`` of ``std_ulogic``, ``std_ulogic_vector`` and ``std_logic_vector``,
     ``hread``, ``hwrite``, ``oread``, ``owrite``), with Synopsys' copyright notice.
   * Synopsys package ``ieee.std_logic_arith`` (:class:`~pyVHDLModel.IEEE.StdLogicArith.Std_Logic_Arith_Synopsys`)
     declares the types ``unsigned`` and ``signed``, the subtype ``small_int`` and its 134 functions (arithmetic and
     relational operators, ``shl``, ``shr``, the ``conv_*`` conversions, ``ext``, ``sxt``), with Synopsys' copyright
     notice.
   * Mentor Graphics package ``ieee.std_logic_arith``
     (:class:`~pyVHDLModel.IEEE.StdLogicArith.Std_Logic_Arith_MentorGraphics`, loaded with
     :data:`IEEEFlavor.MentorGraphics <pyVHDLModel.IEEEFlavor.MentorGraphics>`) declares its use clause
     ``use ieee.std_logic_1164.all;``, the types ``signed`` and ``unsigned`` and 139 functions (conversions,
     arithmetic, shift and logical operators, the comparison functions ``eq`` ... ``ge``), with Mentor Graphics'
     copyright notice.
   * VITAL package ``ieee.VITAL_Timing`` (:class:`~pyVHDLModel.IEEE.VITALTiming.VITAL_Timing`, loaded with
     :data:`IEEEFlavor.WithVITAL <pyVHDLModel.IEEEFlavor.WithVITAL>`) declares its types (transitions, delays, maps,
     records of timing, period, glitch, path and skew data, table and edge symbols), constants (zero delays, default
     maps, initial values), the attributes ``VITAL_Level0`` and ``VITAL_Level1`` and ``VitalTimingDataInit``.

   .. rubric:: Changes

   * Breaking change: the predefined libraries, packages and package bodies take the VHDL version of their declarations
     as parameter ``vhdlVersion`` (default ``VHDLVersion.VHDL2008``, the only supported version so far), also
     :meth:`~pyVHDLModel.Design.LoadStdLibrary` and :meth:`~pyVHDLModel.Design.LoadIEEELibrary`, whose virtual
     documents get it too. Read-only property ``VHDLVersion``. It is the first parameter: ``Ieee(flavor)`` and
     ``LoadIEEELibrary(flavor)`` need ``flavor=flavor`` now, and the parameter ``identifier`` of
     :class:`~pyVHDLModel.Predefined.PredefinedPackage` (``packageIdentifier`` of
     :class:`~pyVHDLModel.Predefined.PredefinedPackageBody`) is the second one.
   * pyTooling 10.3 is required.
   * :data:`VHDLVersion.IsAMS <pyVHDLModel.VHDLVersion.IsAMS>` compares the enumeration members by identity instead of
     building a tuple per call.
   * Adding a declared item finds clashing declarations by an index of the declared items by name instead of visiting
     every declaration of the region: filling a package with n declarations took quadratic time.
   * :mod:`pyVHDLModel.IEEE` is a package with one module per VHDL package, e.g.
     :mod:`~pyVHDLModel.IEEE.StdLogic1164` for ``ieee.std_logic_1164``. The classes are importable from
     :mod:`pyVHDLModel.IEEE` as before.
   * Breaking change: :meth:`~pyVHDLModel.Base.ModelEntity.IterateImplicitDeclarations` yields the implied
     declarations (enumeration literals, physical units), no longer (key, declaration) pairs. A namespace takes the key
     from the new property ``NormalizedDesignator`` of
     :class:`~pyVHDLModel.Type.PhysicalUnit` and :class:`~pyVHDLModel.Subprogram.Subprogram` (as
     :class:`~pyVHDLModel.Expression.EnumerationLiteral` already had).
   * Breaking change: :meth:`Package.IterateDeclarations() <pyVHDLModel.DesignUnit.Package.IterateDeclarations>` and
     :meth:`~pyVHDLModel.DesignUnit.Package.IterateMemberDeclarations` yield the declared items, no longer (key,
     declaration) pairs, and no implied declarations: :meth:`~pyVHDLModel.Namespace.Namespace.AddImports` (new) imports
     a declaration by its identifiers with the declarations it implies;
     :meth:`~pyVHDLModel.DesignUnit.Package.IterateMemberImplicitDeclarations` (new) iterates those a member brings
     along.
   * The analysis indexes the implicit operations of the full types after the type marks are resolved
     (:meth:`~pyVHDLModel.Design.IndexImplicitOperations`, new): a namespace holds them in
     :data:`~pyVHDLModel.Namespace.Namespace.ImplicitOperations` (new), and a use clause naming a type, or a subtype as
     package member, imports them. Before, indexing a type declaration created them, before the use clauses were linked.
   * The analysis resolves the type marks of the implicit operations naming ``BOOLEAN``, ``INTEGER`` or ``STRING`` to
     the types of ``std.standard`` (IEEE Std 1076-2008, 9.2), whatever is visible at the type declaration
     (:meth:`~pyVHDLModel.Type.FullType.ResolveImplicitOperationTypeMarks`, new). Before, they had no reference.
     :meth:`~pyVHDLModel.Design.IndexImplicitOperations` raises :exc:`~pyVHDLModel.Exception.LibraryNotFoundError`
     without library ``std``.
   * An implicit operation is hidden by an explicitly declared homograph in the type's declarative region (IEEE Std
     1076-2008, 12.3), e.g. the implicit ``"="`` of ``unresolved_unsigned`` by the one ``ieee.numeric_std`` declares: a
     lookup doesn't find it, a use clause doesn't import it (:attr:`~pyVHDLModel.Namespace.Namespace.HiddenOperations`,
     new). New :meth:`~pyVHDLModel.Subprogram.SubprogramSignature.HasSameTypeProfile` compares the base types of two
     signatures (4.5.1).

   .. rubric:: Bug Fixes

   * ``std.standard`` named three types wrongly: ``severityLevel`` is ``severity_level``, ``open_file_kind`` is
     ``file_open_kind`` and ``open_file_status`` is ``file_open_status``.
   * The range of ``real`` in ``std.standard`` was -5.0 to 5.0; it's the range of an IEEE 754 double now.
   * The type ``line`` was declared in ``std.standard`` as an access to ``character``; it's declared in ``std.textio``
     as an access to ``string``.
   * The declarations of ``std.standard`` had no parent; their parent is the package.
   * :data:`Subtype.Range <pyVHDLModel.Type.Subtype.Range>` was always ``None`` for a subtype read by pyGHDL: it
     returned a field no constructor parameter set. It returns the range constraint of the subtype indication now.

   .. rubric:: Documentation

   * The documentation builds with pyTooling.Sphinx 1.1 (its prolog provides the docutils substitution files) and
     sphinx_design 0.8.


Version 0.44.0 (2026)
*********************

.. topic:: :gh:`v0.44.0 - 10.11.2026 <VHDL/pyVHDLModel/releases/v0.44.0>`

   .. rubric:: New Features

   * Record element constraints (IEEE Std 1076-2008, 6.3) are model entities: an array element constraint
     (:class:`~pyVHDLModel.Symbol.ArrayElementConstraint`, one range per dimension: ``data(7 downto 0)``,
     ``m(0 to 1, 0 to 7)``) or a nested record constraint (:class:`~pyVHDLModel.Symbol.RecordElementConstraint`:
     ``inner(field(3 downto 0))``). Both can be copied, walked by a visitor (events ``VisitArrayElementConstraint``,
     ``VisitRecordElementConstraint``) and written by the VHDL writer.

   .. rubric:: Changes

   * Breaking change: :data:`RecordConstraint.Constraints <pyVHDLModel.Symbol.RecordConstraint.Constraints>` and the
     ``constraints`` parameter of :class:`~pyVHDLModel.Symbol.ConstrainedRecordSubtypeSymbol` map each record element to
     its element constraint (was a range); ``None`` isn't accepted. The index constraint events of a record element are
     raised for its :class:`~pyVHDLModel.Symbol.ArrayElementConstraint` (was the constrained record subtype symbol); the
     record constraint events take the constrained record subtype symbol or the record element constraint (parameter
     ``element``, was ``symbol``).


Version 0.43.0 (2026)
*********************

.. topic:: :gh:`v0.43.0 - 10.11.2026 <VHDL/pyVHDLModel/releases/v0.43.0>`

   .. rubric:: New Features

   * Statements, branches, case alternatives, enumeration literals, component and block configurations carry a
     documentation comment: constructor parameter ``documentation``, property
     :data:`~pyVHDLModel.Base.DocumentedEntityMixin.Documentation`. Breaking change: it sits before ``parent``, so pass
     ``parent`` by keyword; on enumeration literals it follows ``parent``.
   * Visibility (IEEE Std 1076-2008, clause 12): :meth:`Namespace.Lookup() <pyVHDLModel.Namespace.Namespace.Lookup>`
     returns the declarations directly visible at a place (:class:`~pyVHDLModel.Namespace.LookupResult`): hiding by
     declarations of the region and enclosing regions, overloaded subprograms, subprogram aliases and enumeration
     literals, conflicting imports, declaration order, incomplete types.
   * Use clauses import every declaration of a package (``use lib.pkg.all;``), all declarations of one name, incl. the
     literals or units of a type (``use lib.pkg.item;``), the package (``use lib.pkg;``) or units of a library
     (``use work.all;``); also in declarative parts (architecture, block, process, subprogram, package, generate) and
     through context references, also nested ones. A missing package member or primary unit, a prefix, which isn't a
     visible package, and an uninstantiated generic package are an :exc:`~pyVHDLModel.Exception.UnresolvedNameWarning`.
     The declarations a use clause takes from a package: :meth:`Package.IterateDeclarations()
     <pyVHDLModel.DesignUnit.Package.IterateDeclarations>`, :meth:`Package.IterateMemberDeclarations()
     <pyVHDLModel.DesignUnit.Package.IterateMemberDeclarations>`; a package instantiation iterates those of its generic
     package.
     Whether a library's name is visible in a design unit: :meth:`DesignUnit.IsLibraryVisible()
     <pyVHDLModel.DesignUnit.DesignUnit.IsLibraryVisible>`.
     A declarative region and the regions nested in it: :meth:`IterateDeclarationRegions()
     <pyVHDLModel.Regions.DeclarativeRegionMixin.IterateDeclarationRegions>`; whether an item precedes another one in
     it: :meth:`~pyVHDLModel.Regions.DeclarativeRegionMixin.Precedes`.
   * Every model entity tells whether it's an overloadable declaration
     (:data:`~pyVHDLModel.Base.ModelEntity.IsOverloadable`: subprograms, enumeration literals, aliases which may denote
     one of them) and which declarations it implies
     (:meth:`~pyVHDLModel.Base.ModelEntity.IterateImplicitDeclarations`: the literals of an enumerated type, the units
     of a physical type).
   * Enumeration literals and physical units of a region's types are declarations of the region
     (:data:`Namespace.ImplicitDeclarations <pyVHDLModel.Namespace.Namespace.ImplicitDeclarations>`). An enumeration
     literal is indexed by :data:`EnumerationLiteral.NormalizedDesignator
     <pyVHDLModel.Expression.EnumerationLiteral.NormalizedDesignator>` (a character literal with its apostrophes).
   * Aliases, attribute declarations and packages declared in a region are added to its namespace.
   * :meth:`Design.ResolveTypeMarks() <pyVHDLModel.Design.ResolveTypeMarks>` resolves the type marks of all
     declarations (objects, interface items, record elements, array, access and file types, subtypes, subprograms,
     attributes, aliases, components), incl. the predefined packages and expanded names (``work.pkg.T``), and sets a
     subtype's base type. :meth:`~pyVHDLModel.Design.Analyze` runs it as the first step of
     :meth:`~pyVHDLModel.Design.AnalyzeObjects`. An unresolved type mark is an
     :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`, an incomplete type without a full type declaration an
     :exc:`~pyVHDLModel.Exception.IncompleteTypeWarning`. Expanded names may name an enclosing region (``q.T`` in
     ``q``); a component's generics are visible to its ports; an incomplete type used by anything else than an access
     type and an unresolvable alias name are reported.
   * Type attributes as type marks: ``x'subtype`` (an object's subtype), ``A'element`` (an array's element subtype) and
     ``T'base`` as the prefix of another attribute. The prefix may be an object alias, a record element (``r.f``) or a
     declaration of a package (``p.c``, ``work.p.c``); a port or parameter used in its own interface list is reported.
     Each part of the name resolves to the declaration it references (:meth:`Name.Denote()
     <pyVHDLModel.Name.Name.Denote>`, :meth:`ModelEntity.DenoteBy() <pyVHDLModel.Base.ModelEntity.DenoteBy>`); see
     :ref:`analyze` for an example.
   * :class:`~pyVHDLModel.Name.PredefinedAttribute` enumerates the predefined attributes up to VHDL-2019 (IEEE Std
     1076-2019, 16.2); an attribute name references its member (:data:`AttributeName.PredefinedAttribute
     <pyVHDLModel.Name.AttributeName.PredefinedAttribute>`, ``None`` for a user-defined attribute).
   * :data:`RecordType.ElementsByIdentifier <pyVHDLModel.Type.RecordType.ElementsByIdentifier>` indexes a record's
     elements by each identifier; :data:`BaseType.BaseType <pyVHDLModel.Type.BaseType.BaseType>` returns a type itself
     (a subtype the base type of its type mark).
   * :class:`~pyVHDLModel.Symbol.LoopSymbol` references a loop statement by its label
     (:data:`~pyVHDLModel.Symbol.LoopSymbol.Loop`).

   .. rubric:: Changes

   * pyTooling 10.2 is required.
   * Breaking change: :data:`Namespace.Imports <pyVHDLModel.Namespace.Namespace.Imports>` is a read-only property
     (was a method) of a list of :class:`~pyVHDLModel.Namespace.Import` (declaration and use clause) per identifier;
     :meth:`~pyVHDLModel.Namespace.Namespace.AddImport` takes the use clause.
   * Breaking change: :data:`Namespace.Elements <pyVHDLModel.Namespace.Namespace.Elements>` is a read-only property
     (was a method).
   * Breaking change: a physical type's units are :class:`~pyVHDLModel.Type.PhysicalUnit` declarations:
     :attr:`PhysicalType.PrimaryUnit <pyVHDLModel.Type.PhysicalType.PrimaryUnit>` returns the primary unit, which has no
     value (was its name; formatted, it's still the name), :attr:`PhysicalType.SecondaryUnits
     <pyVHDLModel.Type.PhysicalType.SecondaryUnits>` the list of secondary units (was (name, value) pairs); a secondary
     unit's value has the unit as parent (was the physical type). The constructor takes the primary unit and the
     secondary units (parameter ``secondaryUnits``, was ``units``) as :class:`~pyVHDLModel.Type.PhysicalUnit` (was a
     name and (name, value) pairs), so a unit keeps its documentation comment.
   * Aliases without a subtype indication, which may denote a subprogram, are overloadable; aliases, attribute
     declarations and packages declared in a region are checked for duplicate declarations.
   * A package instantiation, which isn't linked to its generic package, raises
     :exc:`~pyVHDLModel.Exception.PackageInstantiationNotLinkedError` (was
     :exc:`~pyVHDLModel.Exception.VHDLModelException`, from which it derives), with the common base
     :exc:`~pyVHDLModel.Exception.InstantiationNotLinkedError` for all instantiations of generic language entities.
   * ``FindComponent``, ``FindSubtype`` and ``FindObject`` follow the visibility rules: a declaration of an enclosing
     region hides an import of an inner region; the message always lists the searched namespaces.
   * Breaking change: :meth:`Design.Analyze() <pyVHDLModel.Design.Analyze>` analyzes the types and objects too
     (:meth:`~pyVHDLModel.Design.AnalyzeObjects`, which resolves the type marks). A design with an unresolvable type
     mark or alias name, or an incomplete type without full type declaration, reports it as a critical warning:
     collect them with a :class:`~pyTooling.Warning.WarningCollector`, else ``Analyze()`` raises
     :exc:`~pyTooling.Warning.UnhandledCriticalWarningError`.
   * Breaking change: the prototype ``Design.ImportObjects()`` and ``CreateTypeAndObjectGraph()`` are removed; use
     clauses (:meth:`~pyVHDLModel.Design.Analyze`) and :meth:`~pyVHDLModel.Design.AnalyzeObjects` replace them.
   * A protected type and its body chain their namespace to the enclosing region's namespace.
   * Breaking change: :exc:`~pyVHDLModel.Exception.ArchitectureExistsInLibraryError` doesn't take the entity anymore;
     its ``Entity`` property is removed, use ``Architecture.Entity``.
   * :exc:`~pyVHDLModel.Exception.NotAChildError` derives from :exc:`pyTooling.Exceptions.NotAChildError` too.
   * Breaking change: every port interface item is a :class:`~pyVHDLModel.Interface.PortInterfaceItemMixin`; the mixin
     carries no mode and has no initializer parameter (like the generic and parameter mixins).
   * A name is the parent of its prefix.
   * Symbols are model entities: :class:`~pyVHDLModel.Symbol.Symbol` derives from
     :class:`~pyVHDLModel.Base.ModelEntity`. A symbol's parent is the model entity using it, e.g. a statement, an
     expression or a declaration; a symbol is the parent of its name, an aggregate symbol of its targets. The symbol
     classes take an optional keyword-only ``parent`` and declare their fields as slots. A constrained subtype symbol is
     the parent of its constraint ranges and record element symbols, an array type of its index ranges and element
     subtype.
   * Breaking change: ``ModelElementUnion`` (:mod:`pyVHDLModel.Base`) is removed; use
     :class:`~pyVHDLModel.Base.ModelEntity`.
   * :class:`~pyVHDLModel.DesignUnit.Context` inherits ``LibraryReferences``, ``PackageReferences`` and
     ``ContextReferences`` from :class:`~pyVHDLModel.DesignUnit.DesignUnit`.
   * Instantiations annotate their generic and port maps with :class:`~pyVHDLModel.Association.GenericAssociationItem`
     and :class:`~pyVHDLModel.Association.PortAssociationItem`.
   * A component declaration is a declarative region (IEEE Std 1076-2008, 12.1) with its own namespace, nested in the
     enclosing region's namespace: its generics and ports are indexed, also by :meth:`~pyVHDLModel.Design.Analyze`, a
     duplicate identifier is a :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`, the generic and port mutators
     keep the namespace, and generic subprograms of a component overload each other (was
     :exc:`~pyVHDLModel.Exception.DuplicateGenericError`). For it, :class:`~pyVHDLModel.Regions.DeclarationRegionMixin`
     is split into :class:`~pyVHDLModel.Regions.DeclarativeRegionMixin` (namespace and name lookup), which a component
     derives from, and :class:`~pyVHDLModel.Regions.DeclarativePartMixin` (declared items and their mutators); it
     combines both.
   * Enumerations state their member values as number literals (Flags: powers of two) instead of ``auto()``; the values
     are unchanged.
   * Breaking change: ``pyVHDLModel`` no longer imports ``Obj``, ``MultipleNamedEntityMixin``, ``GenerateStatement`` and
     ``GenerateBranch`` (unused there); import them from their modules (:mod:`pyVHDLModel.Object`,
     :mod:`pyVHDLModel.Base`, :mod:`pyVHDLModel.Concurrent`).
   * Linking errors are raised as specific exceptions derived from :exc:`~pyVHDLModel.Exception.VHDLModelException`
     (were plain ``VHDLModelException``), grouped by common bases: :exc:`~pyVHDLModel.Exception.LibraryNotVisibleError`
     (no library clause makes the library visible), :exc:`~pyVHDLModel.Exception.LibraryNotInDesignError` (the library
     doesn't exist in the design), :exc:`~pyVHDLModel.Exception.DesignUnitNotFoundError` (a design unit is missing in
     its library), :exc:`~pyVHDLModel.Exception.NotLinkedError` and :exc:`~pyVHDLModel.Exception.NotComputedError` (an
     analysis step didn't run). The messages are unchanged, except for a package body without its package:
     ``Package body 'p' has no package in library 'l'.`` ``LibraryNotInDesignError`` and ``DesignUnitNotFoundError``
     derive from :exc:`pyTooling.Exceptions.ElementNotFoundError` too, so they are a :exc:`LookupError`.
   * The errors on a library or design unit, which already exists (e.g. ``LibraryExistsInDesignError``,
     ``EntityExistsInLibraryError``), derive from :exc:`pyTooling.Exceptions.DuplicateElementError` too,
     ``LibraryRegisteredToForeignDesignError`` from :exc:`pyTooling.Exceptions.AlreadyInHierarchyError`.
   * A package or context not found for a use clause, a context reference or a package instantiation raises
     :exc:`~pyVHDLModel.Exception.PackageNotFoundError` or :exc:`~pyVHDLModel.Exception.ContextNotFoundError`, caused by
     the failed lookup; the message is unchanged.
   * No plain ``VHDLModelException`` is raised anymore. More common bases:
     :exc:`~pyVHDLModel.Exception.UnknownKindError` (a symbol or secondary unit of unknown kind) and
     :exc:`~pyVHDLModel.Exception.IEEEFlavorError` (an unknown or conflicting ``ieee`` flavor). A duplicate design unit
     in a document raises :exc:`~pyVHDLModel.Exception.DuplicateDesignUnitError`, a second architecture of an entity
     :exc:`~pyVHDLModel.Exception.ArchitectureExistsInLibraryError`; single conditions have their own error
     (:exc:`~pyVHDLModel.Exception.AmbiguousTopLevelError`, :exc:`~pyVHDLModel.Exception.NotAGenericPackageError`,
     :exc:`~pyVHDLModel.Exception.AncestorNotFoundError`, ...). Failed library and entity lookups are the cause of their
     error. ``UnknownKindError`` derives from :exc:`pyTooling.Exceptions.UnknownKindError`, ``AmbiguousTopLevelError``
     from :exc:`pyTooling.Exceptions.AmbiguousError`; the message of the latter ends with a period. Every common base
     derives from :exc:`~pyVHDLModel.Exception.VHDLModelException`.
   * Breaking change: the exceptions, which built their message from their arguments, take the message as the first,
     positional-only parameter and the descriptive values as keyword-only parameters, e.g.
     ``LibraryNotFoundError(message, /, *, libraryName)`` or
     ``EntityExistsInLibraryError(message, /, *, entity, library)``; the raising code builds the message. Fields,
     properties and messages are unchanged.

   .. rubric:: Bug Fixes

   * The symbols of use clauses in contexts and of ``.all``/member use clauses reference their package; context
     reference symbols their context (was an extra attribute).
   * A context reference to a context with a use clause of a package named like its library (``use foo.foo.all;``)
     raised ``Referenced package 'foo' already exists``.
   * A use clause of a context declaration naming a package (``use lib.pkg;``), units of a library (``use lib.all;``,
     ``use lib.unit;``) or a package by a simple name (``use pkg.all;``) raised ``AttributeError``. A context
     declaration links its use clauses as a design unit does; :meth:`~pyVHDLModel.Design.LinkContexts` needs
     :meth:`~pyVHDLModel.Design.LinkPackageInstances` before.
   * :meth:`Design.AnalyzeDependencies() <pyVHDLModel.Design.AnalyzeDependencies>` indexes the architectures and the
     package bodies after linking them. Before, an architecture was indexed before it was linked to its entity, so a
     declaration duplicating a declaration or a port of the entity wasn't reported, and package bodies were indexed
     once by the type-mark resolution, so a repeated analysis didn't report a body declaration duplicating one of its
     package.
   * Adding an architecture, which already exists in the library, raised ``KeyError`` instead of
     :exc:`~pyVHDLModel.Exception.ArchitectureExistsInLibraryError`, if the library didn't hold its entity.
   * A design unit kept a context item of an unknown kind in ``ContextItems`` only, a context declaration raised a plain
     :exc:`~pyVHDLModel.Exception.VHDLModelException` for it; both raise :exc:`TypeError` now.
   * :data:`~pyVHDLModel.Regions.WithGenericsMixin.GenericCount`, :data:`~pyVHDLModel.Regions.WithPortsMixin.PortCount`
     and :data:`~pyVHDLModel.Regions.WithParametersMixin.ParameterCount` counted interface items instead of the declared
     generics, ports and parameters: ``port (a, b : in bit)`` gave 1. They count the identifiers now (2).
   * Breaking change: next and exit statements dropped their loop label and their own statement label (``lbl : next
     outer when c;``). :class:`~pyVHDLModel.Sequential.LoopControlStatement` takes ``loopLabel`` as a
     :class:`~pyVHDLModel.Symbol.LoopSymbol` (was ``str``, ignored) and a ``label``;
     :data:`~pyVHDLModel.Sequential.LoopControlStatement.LoopReference` returns the symbol. The visitor walks the
     symbol, the VHDL writer writes it.

   .. rubric:: Documentation

   * The glossary explains the VHDL terms declarative part, declarative region, design unit, normalized, primary unit
     and secondary unit, with the defining clause of IEEE Std 1076-2008; the normalized identifier, label and designator
     properties refer to it.
   * Cross-references to renamed or misnamed targets, the alignment of field lists and the summaries of computed
     properties are fixed.
   * Test doc-strings have a one-line summary, so pyTooling's pytest plugin reports them.
   * New ReST role ``vhdlcode`` in ``doc/prolog.inc`` (like ``pycode``) for VHDL code with syntax highlighting; the
     rewritten test doc-strings use it, and ``pycode`` for Python fragments.


Version 0.42.0 (2026)
*********************

.. topic:: :gh:`v0.42.0 - 31.10.2026 <VHDL/pyVHDLModel/releases/v0.42.0>`

   .. rubric:: New Features

   * Interface groups partition the generic clause, the port clause and the parameter list of a language construct:
     constructor parameters ``genericGroups``, ``portGroups`` and ``parameterGroups``, properties
     :data:`~pyVHDLModel.Regions.WithGenericsMixin.GenericGroups`,
     :data:`~pyVHDLModel.Regions.WithPortsMixin.PortGroups` and
     :data:`~pyVHDLModel.Regions.WithParametersMixin.ParameterGroups`. Each interface item refers to its group
     (:data:`~pyVHDLModel.Interface.InterfaceItemMixin.Group`). ``Add***Item()`` and ``Insert***Item()`` take an
     optional group; all mutators keep the partition.

   .. rubric:: Changes

   * Breaking change: :class:`~pyVHDLModel.Interface.GenericGroup`, :class:`~pyVHDLModel.Interface.PortGroup` and
     :class:`~pyVHDLModel.Interface.ParameterGroup` are non-owning views of a language construct's interface items: an
     item's parent stays the language construct, and a group has no mutators any more. A group rejects an empty or
     already grouped item list.
   * Breaking change: a language construct constructed without groups checks its interface items' types: an item of
     the wrong type raises :exc:`TypeError`, where it was accepted before.


Version 0.41.0 (2026)
*********************

.. topic:: :gh:`v0.41.0 - 31.10.2026 <VHDL/pyVHDLModel/releases/v0.41.0>`

   .. rubric:: New Features

   * A group of targets on the left-hand side of an assignment (``(carry, sum) := ...``) is
     :class:`~pyVHDLModel.Symbol.AggregateSymbol`.
   * Character literals of enumeration types are their own class:
     :class:`~pyVHDLModel.Expression.CharacterEnumerationLiteral` holds the bare character; the VHDL writer adds the
     apostrophes.
   * The condition operator ``??`` is :class:`~pyVHDLModel.Expression.ConditionExpression`.
   * Visitor: declarations, statements and context items report their semicolon as
     :meth:`~pyVHDLModel.Visitor.Visitor.VisitTerminator`.
   * VHDL writer: the reserved words and the name after ``end`` can be left out where VHDL allows it
     (``VHDLStyle(endKeyword=..., endName=...)``); the visitor reports :meth:`~pyVHDLModel.Visitor.Visitor.VisitEnd`.

   .. rubric:: Changes

   * The character literals of ``STD.bit`` and ``STD.character`` hold the bare character (``"0"``, was ``"'0'"``).

   .. rubric:: Bug Fixes

   * ``IEEE.std_ulogic``'s literals are written as character literals; ``STD.character``'s literal at position 92 is
     ``'\'``.

   .. rubric:: Documentation

   * The language model pages render their classes from the source (``condensed-class``) and name the current modules.


Version 0.40.0 (2026)
*********************

.. topic:: :gh:`v0.40.0 - 29.10.2026 <VHDL/pyVHDLModel/releases/v0.40.0>`

   .. rubric:: New Features

   * Mutation API, first part: generics, ports, parameters, declared items and statements can be added, inserted,
     moved and removed, with ownership checks and namespace updates; association items, context items, a document's
     design units, a design's documents and libraries too.
   * VHDL writer: :class:`~pyVHDLModel.Formatting.VHDL.VHDLWriter` writes the model as VHDL source text - from
     literals and expressions to design units, configurations and whole documents -, built on the visitor
     :class:`~pyVHDLModel.Visitor.Visitor`; formatting options are named after vhdl-style-guide's.
   * Warnings and mutation errors carry the model objects they are about.
   * A design can be analyzed again after it was changed; design units are looked up by library and name, or searched
     in all libraries.
   * Names, symbols, expressions, ranges, association items, object declarations and interface items can be copied.
   * A subprogram's signature - the type marks of its parameters and return value - tells overloads apart.
   * Bit string literals compute their value.

   .. rubric:: Changes

   * pyTooling 10.1 is required; Python 3.11 to 3.15 are supported.
   * Duplicate declarations are critical warnings.
   * A namespace keeps use-clause imports apart from its declarations.
   * The base-classes of the model are abstract.

   .. rubric:: Bug Fixes

   * Architecture keys, if-generate else branches, multi-identifier normalization, entity-instantiation errors,
     ``Context.ContextItems``, a second ``Design.Analyze()`` and entity namespaces after the analysis.

   .. rubric:: Documentation

   * New page :ref:`VHDL Writer <WRITER>`; the documentation is built with pyTooling.Sphinx.


Version 0.7.0 - 0.39.0 (2020 - 2026)
************************************

.. only:: html

   April 2026 - Generic, Port, and Parameter Groups
   ================================================

.. only:: latex

   .. rubric:: Generic, Port, and Parameter Groups

* Link components in architectures and components nested in concurrent statements.
* Added grouping of generics, ports and parameters.


.. only:: html

   Nov. 2025 - Raise Warnings
   ==========================

.. only:: latex

   .. rubric:: Raise Warnings

* Handle bit-string literals
* Raise Warnings instead of Exceptions.


.. only:: html

   Feb. 2025 - Blackboxes
   ======================

.. only:: latex

   .. rubric:: Blackboxes

* Support handling of blackboxes for component instantiations.
* Added dummy packages for Synopsys and Mentor Graphics "IEEE" packages.


.. only:: html

   Sept. 2024 - Unary Operators
   ============================

.. only:: latex

   .. rubric:: Unary Operators

* Added more unary operators.
* Added more doc-strings


.. only:: html

   Jan. 2023 - Dependency, Hierarchy, Compile Order Analysis
   =========================================================

.. only:: latex

   .. rubric:: Dependency, Hierarchy, Compile Order Analysis

* Enhanced analysis of cross references.
* Enhanced dependency graphs:

  * Hierarchy graph and toplevel detection
  * Compile order computation

* Transformation from single module to >15 modules.
* Improved code coverage and test cases.


.. only:: html

   Dec. 2022 - Added Documentation Property
   ========================================

.. only:: latex

   .. rubric:: Added Documentation Property

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is now able to collect and associate (documentation) comments to language
  constructs. This enhancement adds a ``Documentation`` property to many classes similar to a *doc-string* in Python.
* New -style of symbols merging a ``Name`` and a ``Symbol`` class.
* Finding relations between packages and its bodies, entities and its architectures.
* References to libraries, packages and contexts.
* Dependency graph for packages, contexts, and entities.

  * Package graph.
  * Hierarchy graph.
  * Compile order.


.. only:: html

   Jul. 2021 - First adoption and enhancements
   ===========================================

.. only:: latex

   .. rubric:: First adoption and enhancements

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is the first big adopter with `pyGHDL.dom <https://ghdl.github.io/ghdl/pyGHDL/pyGHDL.dom.html>`__
  to generate a network of instantiated classes derived from ``pyVHDLModel``. |br|
  It uses `pyGHDL <https://ghdl.github.io/ghdl/using/pyGHDL/index.html>`__ as a backend (GHDL build as shared object and
  loaded into CPython via C-binding API (``ctypes``).


.. only:: html

   Jun. 2021 - Model and documentation enhancements
   ================================================

.. only:: latex

   .. rubric:: Model and documentation enhancements

* Made generic, port, and parameter items a subclass of the matching object classes.
* Added missing object representations for language features.

  * Finalized literals, expressions and types.
  * Added properties to empty placeholder classes.

* Corrected class hierarchy according to LRM.
* Enhanced class documentation and cross references.
* New documentation chapter for literals and expressions.
* Added inheritance diagrams as overviews to documentation sections.
* Added condensed code snippets outlining the main interface of a model's object.
* New Single-File GitHub Action workflow (pipeline) including tests, documentation, packaging and publishing.
* Added Dependabot configuration file.
* Removed 2 dependencies to patched Sphinx extensions (now fixed in Sphinx).
* ...

.. only:: html

   Jan. 2021 - Documentation enhancements
   ======================================

.. only:: latex

   .. rubric:: Documentation enhancements

* Enhanced class documentation.
* Changed test runner to ``pytest``.
* Dependency check and license clearance. |br|
  See :ref:`DEP` for details.


.. only:: html

   Dec. 2020 - Split from pyVHDLParser
   ===================================

.. only:: latex

   .. rubric:: Split from pyVHDLParser

* `pyVHDLModel` was split from `pyVHDLParser <https://GitHub.com/Paebbels/pyVHDLParser>`__ (v0.6.0) as an independent Python package.
