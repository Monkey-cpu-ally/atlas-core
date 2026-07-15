"""ATLAS Core Runtime package.

This package starts, coordinates, monitors, and shuts down AtlasOS services.
"""

from .kernel import AtlasKernel, KernelStatus
from .service_registry import ServiceEntry, ServiceRegistry

__all__ = ["AtlasKernel", "KernelStatus", "ServiceEntry", "ServiceRegistry"]

__version__ = "0.1.0"
