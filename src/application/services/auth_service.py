"""
Service: AuthService
Application service layer for authentication workflows.
"""

from typing import Optional, Dict
from domain.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self._auth_repository = auth_repository

    def login_user(self, email: str, password: str) -> Optional[Dict[str, object]]:
        return self._auth_repository.login_user(email, password)

    def sign_up(self, email: str, password: str) -> Optional[str]:
        return self._auth_repository.sign_up(email, password)
