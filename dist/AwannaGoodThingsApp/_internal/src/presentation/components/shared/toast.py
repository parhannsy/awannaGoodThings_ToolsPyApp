"""
Toast Notification Component

Reusable toast notification untuk seluruh aplikasi.
"""

import customtkinter as ctk


class Toast(ctk.CTkToplevel):

    WIDTH = 320
    HEIGHT = 90

    SUCCESS_ICON = "✓"
    ERROR_ICON = "✕"

    SUCCESS_TITLE = "Berhasil"
    ERROR_TITLE = "Gagal"

    def __init__(
        self,
        master,
        title,
        message,
        icon,
        duration=3500
    ):
        super().__init__(master)

        self.duration = duration

        # ==================================
        # WINDOW CONFIG
        # ==================================

        self.overrideredirect(True)

        self.attributes("-topmost", True)

        self.resizable(False, False)

        self.configure(
            fg_color=("white", "#2B2B2B")
        )

        self._set_position(master)

        # ==================================
        # UI
        # ==================================

        self.container = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        self.container.pack(
            fill="both",
            expand=True
        )

        self.icon_label = ctk.CTkLabel(
            self.container,
            text=icon,
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            width=40
        )

        self.icon_label.pack(
            side="left",
            padx=(15, 10),
            pady=15
        )

        self.content_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15),
            pady=12
        )

        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text=title,
            anchor="w",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        self.title_label.pack(
            fill="x"
        )

        self.message_label = ctk.CTkLabel(
            self.content_frame,
            text=message,
            anchor="w",
            justify="left",
            wraplength=220,
            font=ctk.CTkFont(
                size=12
            )
        )

        self.message_label.pack(
            fill="x",
            pady=(2, 0)
        )

        # ==================================
        # AUTO CLOSE
        # ==================================

        self.after(
            self.duration,
            self._close
        )

    def _set_position(self, master):

        self.update_idletasks()

        root_x = master.winfo_rootx()
        root_y = master.winfo_rooty()

        root_width = master.winfo_width()

        x = (
            root_x +
            root_width -
            self.WIDTH -
            20
        )

        y = root_y + 20

        self.geometry(
            f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}"
        )

    def _close(self):
        try:
            self.destroy()
        except Exception:
            pass

    # ==================================
    # STATIC HELPERS
    # ==================================

    @classmethod
    def success(
        cls,
        master,
        message,
        duration=3500
    ):
        return cls(
            master=master,
            title=cls.SUCCESS_TITLE,
            message=message,
            icon=cls.SUCCESS_ICON,
            duration=duration
        )

    @classmethod
    def error(
        cls,
        master,
        message,
        duration=4500
    ):
        return cls(
            master=master,
            title=cls.ERROR_TITLE,
            message=message,
            icon=cls.ERROR_ICON,
            duration=duration
        )