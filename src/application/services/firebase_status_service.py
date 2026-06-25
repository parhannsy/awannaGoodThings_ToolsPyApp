"""
Service: FirebaseStatusService
Application service layer for Firebase connectivity checks.
"""

from typing import Tuple
from domain.repositories.firebase_status_repository import FirebaseStatusRepository


class FirebaseStatusService:
    def __init__(self, status_repository: FirebaseStatusRepository):
        self._status_repository = status_repository

    def check_connection(self) -> Tuple[bool, str]:
        return self._status_repository.check_connection()

