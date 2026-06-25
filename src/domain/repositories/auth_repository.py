"""
Repository Interface: AuthRepository
Abstract interface untuk autentikasi pengguna.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict


class AuthRepository(ABC):
    """Abstract repository untuk autentikasi dan pendaftaran pengguna."""

    @abstractmethod
    def login_user(self, email: str, password: str) -> Optional[Dict[str, object]]:
        """Login user dengan email dan password."""
        pass

    @abstractmethod
    def sign_up(self, email: str, password: str) -> Optional[str]:
        """Buat akun baru dan kembalikan id_user yang dibuat."""
        pass
