import threading
import customtkinter as ctk
from presentation.components.shared.toast import Toast


class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, account_service=None, email=""):
        super().__init__(master)
        self.account_service = account_service
        self.email = email

        self.title("Ganti Password")
        self.geometry("420x160")
        self.resizable(False, False)
        self.configure(fg_color="#1F2937")

        self.transient(master)
        self.attributes("-topmost", True)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=16)

        lbl = ctk.CTkLabel(main, text=f"Kirim email reset password ke:\n{self.email}", anchor="w", justify="left")
        lbl.pack(fill="x", pady=(0, 10))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))

        self.btn_cancel = ctk.CTkButton(btn_frame, text="Batal", width=120, fg_color="#4B5563", hover_color="#374151", command=self.destroy)
        self.btn_cancel.pack(side="left")

        self.btn_send = ctk.CTkButton(btn_frame, text="Kirim Email Reset", width=220, fg_color="#3B82F6", hover_color="#2563EB", command=self._handle_send)
        self.btn_send.pack(side="right")

    def _handle_send(self):
        if not self.email:
            Toast.error(master=self, message="Email tidak tersedia untuk user ini.")
            return

        self.btn_send.configure(state="disabled", text="Mengirim...")
        threading.Thread(target=self._send_worker, daemon=True).start()

    def _send_worker(self):
        success = False
        try:
            if not self.account_service:
                raise RuntimeError("Account service belum disuntikkan ke ChangePasswordDialog.")
            success = self.account_service.send_password_reset(self.email)
        except Exception as e:
            self.after(0, lambda: Toast.error(master=self, message=str(e)))

        if success:
            self.after(0, lambda: Toast.success(master=self, message=f"Email reset password dikirim ke {self.email}"))
            self.after(0, self.destroy)
        else:
            self.after(0, lambda: self.btn_send.configure(state="normal", text="Kirim Email Reset"))
            self.after(0, lambda: Toast.error(master=self, message="Gagal mengirim email reset."))
