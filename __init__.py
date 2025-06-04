# Re-export classes for compatibility - explicit imports to avoid PyLance confusion with wildcards

# Re-export main classes
from pyVHDLModel.pyVHDLModel import Document, Design, Library, VHDLVersion, __version__

# Re-export DesignUnit classes (required for BaseDocument compatibility)
from pyVHDLModel.DesignUnit import (
    Entity,
    Architecture,
    Package,
    PackageBody,
    Context,
    Configuration
)

# Re-export Interface classes
from pyVHDLModel.Interface import (
    GenericConstantInterfaceItem,
    PortSignalInterfaceItem,
    PortGroup
)

# Re-export Base classes
from pyVHDLModel.Base import Mode

# Re-export Expression classes
from pyVHDLModel.Expression import (
    IntegerLiteral,
    EnumerationLiteral,
    StringLiteral
)

# Re-export Symbol classes
from pyVHDLModel.Symbol import SimpleSubtypeSymbol

# Re-export Name classes
from pyVHDLModel.Name import SimpleName