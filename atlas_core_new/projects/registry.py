"""
Project Registry - Central access point for all projects
Import all project modules to register them
"""
from .base import project_registry, Project, ProjectPhase, BuildModule, BuildStep

from .power_cell import power_cell_project
from .oxygen_converter import oxygen_converter_project
from .mimic_cell import mimic_cell_project
from .gaia_system import gaia_system_project

__all__ = [
    'project_registry',
    'Project',
    'ProjectPhase', 
    'BuildModule',
    'BuildStep',
    'power_cell_project',
    'oxygen_converter_project',
    'mimic_cell_project',
    'gaia_system_project'
]
