from abc import ABC, abstractmethod
from typing import Dict, Any, List


class DesignPlugin(ABC):
    key: str = "base"
    display_name: str = "Base Plugin"

    @abstractmethod
    def default_constraints(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def generate_variant(self, idx: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def acceptance_tests(self, constraints: Dict[str, Any]) -> List[str]:
        ...

    @abstractmethod
    def parts_list(self, constraints: Dict[str, Any]) -> List[str]:
        ...
