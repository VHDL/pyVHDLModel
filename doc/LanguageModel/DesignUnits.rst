.. _vhdlmodel-desuni:

Design Units
############

A VHDL design (see :ref:`vhdlmodel-design`) is assembled from *design units*. VHDL distinguishes
between *primary* and *secondary* design units.

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.DesignUnit.Architecture
                         pyVHDLModel.DesignUnit.Context
                         pyVHDLModel.DesignUnit.Configuration
                         pyVHDLModel.DesignUnit.Entity
                         pyVHDLModel.DesignUnit.Package
                         pyVHDLModel.DesignUnit.PackageBody
   :parts: 1

.. _vhdlmodel-primary:

Primary Units
*************

.. _vhdlmodel-context:

Context
=======

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.Context`:

.. condensed-class:: pyVHDLModel.DesignUnit.Context


.. _vhdlmodel-configuration:

Configuration
=============

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.Configuration`:

.. condensed-class:: pyVHDLModel.DesignUnit.Configuration


.. _vhdlmodel-entity:

Entity
======

An ``Entity`` represents a VHDL entity declaration. Libraries and package
references declared ahead an entity are consumed by that entity and made
available as lists. An entities also provides lists of generic and port items.
The list of declared items (e.g. objects) also contains defined items (e.g.
types). An entity's list of statements is called body items.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.Entity`:

.. condensed-class:: pyVHDLModel.DesignUnit.Entity


.. _vhdlmodel-package:

Package
=======

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.Package`:

.. condensed-class:: pyVHDLModel.DesignUnit.Package


.. _vhdlmodel-secondary:

Secondary Units
***************

.. _vhdlmodel-architecture:

Architecture
============

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.Architecture`:

.. condensed-class:: pyVHDLModel.DesignUnit.Architecture


.. _vhdlmodel-packagebody:

Package Body
============

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.DesignUnit.PackageBody`:

.. condensed-class:: pyVHDLModel.DesignUnit.PackageBody
