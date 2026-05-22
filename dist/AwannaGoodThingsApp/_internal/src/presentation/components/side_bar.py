"""
Component: Sidebar
"""

import customtkinter as ctk
from typing import Callable, Dict


class Sidebar(ctk.CTkFrame):
    """Navigation sidebar component."""

    MENU_GROUPS = [
        {
            "label": "GENERAL",
            "items": [
                {"id": "dashboard", "label": "Dashboard", "icon": "🏠"},
                {"id": "history", "label": "History", "icon": "🕘"},
            ]
        },
        {
            "label": "TOOLS",
            "items": [
                {"id": "regional_summary", "label": "Regional Summary", "icon": "📊"},
                {"id": "rate_zonasi", "label": "Rate Zonasi", "icon": "📍"},
                {"id": "transformer", "label": "Data Transformer", "icon": "🔄"},
                {"id": "performance", "label": "Performance", "icon": "📈"},
            ]
        }
    ]

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        app_name: str,
        **kwargs
    ):
        super().__init__(master, width=250, **kwargs)

        self.on_navigate = on_navigate
        self.buttons: Dict[str, ctk.CTkButton] = {}

        self._setup_layout()
        self._setup_header(app_name)
        self._setup_menu()
        self._setup_footer()

    def _setup_layout(self):
        self.grid_rowconfigure(1, weight=1)

    def _setup_header(self, app_name: str):
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.pack(fill="x", padx=16, pady=(20, 10))

        logo_label = ctk.CTkLabel(
            header_container,
            text="🧩",
            font=ctk.CTkFont(size=32)
        )
        logo_label.pack(anchor="w")

        app_label = ctk.CTkLabel(
            header_container,
            text=app_name,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        app_label.pack(anchor="w", pady=(4, 0))

        subtitle = ctk.CTkLabel(
            header_container,
            text="Sales Data Workspace",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        subtitle.pack(anchor="w")

        line = ctk.CTkFrame(
            self,
            height=2,
            fg_color=("gray75", "gray25")
        )
        line.pack(fill="x", padx=15, pady=(10, 15))

    def _setup_menu(self):
        # FIX: Ganti CTkScrollableFrame → CTkFrame biasa
        # Agar tidak ada scrollbar yang mengganggu
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.pack(
            fill="both",
            expand=True,  # Stretch mengisi ruang kosong
            padx=10,
            pady=(0, 10)
        )

        for group in self.MENU_GROUPS:
            # GROUP LABEL
            group_label = ctk.CTkLabel(
                self.menu_frame,
                text=group["label"],
                anchor="w",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="gray50"
            )
            group_label.pack(fill="x", padx=10, pady=(14, 6))

            # GROUP ITEMS
            for item in group["items"]:
                btn = ctk.CTkButton(
                    self.menu_frame,
                    text=f"{item['icon']}   {item['label']}",
                    anchor="w",
                    height=42,
                    corner_radius=10,
                    border_width=0,
                    fg_color="transparent",
                    hover_color=("gray80", "gray22"),
                    text_color=("gray15", "gray90"),
                    font=ctk.CTkFont(size=13),
                    command=lambda x=item["id"]: self.on_navigate(x)
                )
                btn.pack(fill="x", pady=3, padx=2)
                self.buttons[item["id"]] = btn

    def _setup_footer(self):
        footer_container = ctk.CTkFrame(self, fg_color="transparent")
        footer_container.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=15
        )

        line = ctk.CTkFrame(footer_container, height=1, fg_color=("gray75", "gray25"))
        line.pack(fill="x", pady=(0, 10))

        footer = ctk.CTkLabel(
            footer_container,
            text="v1.0.0  •  Sales Data Tool",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        footer.pack()

    def set_active(self, view_id: str):
        for vid, btn in self.buttons.items():
            if vid == view_id:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    hover_color=("gray75", "gray25"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    border_width=1,
                    border_color=("gray65", "gray35")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=("gray80", "gray22"),
                    font=ctk.CTkFont(size=13),
                    border_width=0
                )