"""
Service: UserService
Application service layer for user profile operations.
"""

from typing import List, Dict, Optional, Any
from domain.repositories.user_repository import UserRepositoryPort


class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self._user_repository = user_repository

    def get_all_users(self) -> List[Dict[str, Any]]:
        return self._user_repository.get_all_users()

    def get_all_teams(self) -> List[Dict[str, Any]]:
        return self._user_repository.get_all_teams()

    def update_user_profile(self, id_user: str, profile_data: Dict[str, Any]) -> bool:
        return self._user_repository.update_user_profile(id_user, profile_data)

    def create_team_profile(self, team_data: Dict[str, Any]) -> bool:
        return self._user_repository.create_team_profile(team_data)

    def update_team_profile(self, team_id: str, profile_data: Dict[str, Any]) -> bool:
        return self._user_repository.update_team_profile(team_id, profile_data)

    def stream_users_data(self, callback_function) -> Optional[Any]:
        return self._user_repository.stream_users_data(callback_function)

    def stream_teams_data(self, callback_function) -> Optional[Any]:
        return self._user_repository.stream_teams_data(callback_function)
