"""
Service: AccountService
Application service layer that orchestrates authentication and user profile management.
"""
from typing import Optional, Dict, Any
from domain.repositories.auth_repository import AuthRepository
from domain.repositories.user_repository import UserRepositoryPort


class AccountService:
    def __init__(self, auth_repository: AuthRepository, user_repository: UserRepositoryPort):
        self._auth_repository = auth_repository
        self._user_repository = user_repository

    def login_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        return self._auth_repository.login_user(email, password)

    def sign_up(self, email: str, password: str, role: str) -> Optional[str]:
        return self._auth_repository.sign_up(email, password)

    def create_user_profile(self, id_user: str, profile_data: Dict[str, Any]) -> bool:
        return self._user_repository.update_user_profile(id_user, profile_data)

    def create_user_account(self, email: str, password: str, profile_data: Dict[str, Any]) -> bool:
        created_id = self._auth_repository.sign_up(email, password)
        if not created_id:
            raise ValueError(
                "Gagal mendaftarkan akun di Firebase Auth. Pastikan email belum terdaftar dan password minimal 6 karakter."
            )

        profile_data["idUser"] = created_id
        if not self._user_repository.update_user_profile(created_id, profile_data):
            raise RuntimeError(
                "Akun berhasil dibuat di Firebase Auth, tetapi penyimpanan profil user di Firestore gagal."
            )

        return True

    def get_all_users(self) -> list[Dict[str, Any]]:
        return self._user_repository.get_all_users()

    def update_user_profile(self, id_user: str, profile_data: Dict[str, Any]) -> bool:
        return self._user_repository.update_user_profile(id_user, profile_data)

    def stream_users_data(self, callback_function) -> Optional[Any]:
        return self._user_repository.stream_users_data(callback_function)

    def send_password_reset(self, email: str) -> bool:
        return self._auth_repository.send_password_reset(email)
