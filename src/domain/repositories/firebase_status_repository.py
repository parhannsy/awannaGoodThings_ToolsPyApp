"""
Repository Interface: FirebaseStatusRepository
Abstract port for Firebase connectivity checks.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class FirebaseStatusRepository(ABC):
    @abstractmethod
    def check_connection(self) -> Tuple[bool, str]:
        pass
