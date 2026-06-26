"""
Repository Interface: UserRepositoryPort
Abstract interface untuk operasi user dan profil aplikasi.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class UserRepositoryPort(ABC):
    """Abstract repository for user profile and account data."""

    @abstractmethod
    def get_all_users(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all_teams(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_user_profile(self, id_user: str, profile_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def create_team_profile(self, team_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def stream_users_data(self, callback_function) -> Optional[Any]:
        pass

    @abstractmethod
    def update_team_profile(self, team_id: str, profile_data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def stream_teams_data(self, callback_function) -> Optional[Any]:
        pass
