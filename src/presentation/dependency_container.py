"""Dependency container for presentation layer services."""

from infrastructure.persistence.firebase_auth_impl import FirebaseAuthRepository
from infrastructure.persistence.user_repository import UserRepository
from infrastructure.persistence.firebase_status_adapter import FirebaseStatusAdapter
from infrastructure.persistence.excel_writter import ExcelWriter
from application.services.account_service import AccountService
from application.services.firebase_status_service import FirebaseStatusService
from application.services.export_manager import ExportManagerService
from application.services.user_service import UserService


def create_presentation_services():
    """Build concrete services and adapters for the presentation layer."""
    auth_repo = FirebaseAuthRepository()
    user_repo = UserRepository()
    firebase_status_repo = FirebaseStatusAdapter()
    excel_writer = ExcelWriter()

    account_service = AccountService(auth_repo, user_repo)
    user_service = UserService(user_repo)
    firebase_status_service = FirebaseStatusService(firebase_status_repo)
    export_manager = ExportManagerService(excel_writer)

    return {
        "account_service": account_service,
        "user_service": user_service,
        "firebase_status_service": firebase_status_service,
        "export_manager": export_manager,
    }
