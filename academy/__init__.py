"""ATLAS Academy package.

Keep package import lightweight: the current Academy implementation exposes schemas and
school registry data, while optional engines can be added without breaking school modules.
"""

from .schemas import AcademyLesson, AcademyProject, AcademySchool, MasteryLevel

__all__ = [
    "AcademyLesson",
    "AcademyProject",
    "AcademySchool",
    "MasteryLevel",
]
