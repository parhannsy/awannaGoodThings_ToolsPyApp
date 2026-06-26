"""
Component: UserSummaryCard
Menangani rendering visual tiga blok kartu ringkasan informasi total SDM, Staff, dan Tim.
"""

import customtkinter as ctk


class UserSummaryCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#0B1220", height=130, corner_radius=8, **kwargs)
        self.pack_propagate(False)
        
        # Container horizontal utama
        self.box_container = ctk.CTkFrame(self, fg_color="transparent")
        self.box_container.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Bangun 3 pilar card informasi
        self.box_total_sdm, self.lbl_sdm_value, self.lbl_sdm_breakdown = self._build_card("Total SDM")
        self.box_total_staff, self.lbl_staff_value, self.lbl_staff_breakdown = self._build_card("Total Staff")
        self.box_total_team, self.lbl_team_value, self.lbl_team_breakdown = self._build_card("Total Tim")
        
        # Tuning spesifikasi ukuran teks visual font
        self.lbl_sdm_value.configure(font=ctk.CTkFont(size=44, weight="bold"))
        self.lbl_staff_value.configure(font=ctk.CTkFont(size=34, weight="bold"))
        self.lbl_team_value.configure(font=ctk.CTkFont(size=34, weight="bold"))
        
        self.lbl_sdm_breakdown.configure(text="Jumlah keseluruhan staff dan tim terdaftar.")

    def _build_card(self, title_text):
        frame = ctk.CTkFrame(self.box_container, fg_color="#111827", corner_radius=10)
        frame.pack(side="left", fill="both", expand=True, padx=4)
        frame.pack_propagate(False)

        header = ctk.CTkLabel(
            frame, text=title_text, text_color="#9CA3AF", 
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        )
        header.pack(fill="x", padx=12, pady=(12, 6))

        value_container = ctk.CTkFrame(frame, fg_color="#1F2937", corner_radius=8)
        value_container.pack(fill="x", padx=12, pady=(0, 10))
        value_container.configure(height=56)
        value_container.pack_propagate(False)

        value_label = ctk.CTkLabel(value_container, text="0", font=ctk.CTkFont(size=38, weight="bold"), text_color="#FFFFFF")
        value_label.pack(side="left", padx=(16, 4), pady=8)
        
        unit_label = ctk.CTkLabel(value_container, text="Orang", font=ctk.CTkFont(size=12), text_color="#D1D5DB")
        unit_label.pack(side="left", pady=14)

        detail_panel = ctk.CTkFrame(frame, fg_color="#111827", corner_radius=8)
        detail_panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        detail_label = ctk.CTkLabel(detail_panel, text="", text_color="#D1D5DB", anchor="nw", justify="left", wraplength=220)
        detail_label.pack(fill="both", padx=10, pady=10)

        return frame, value_label, detail_label

    def update_statistics(self, total_sdm, total_staff, total_teams, staff_breakdown, team_breakdown):
        """Metode API Publik untuk memperbarui teks data angka & breakdown dari luar."""
        self.lbl_sdm_value.configure(text=str(total_sdm))
        self.lbl_staff_value.configure(text=str(total_staff))
        self.lbl_team_value.configure(text=str(total_teams))
        
        self.lbl_staff_breakdown.configure(text=self._format_alignment(staff_breakdown))
        self.lbl_team_breakdown.configure(text=self._format_alignment(team_breakdown))

    def _format_alignment(self, lines):
        if not lines:
            return "-"
        max_label = max([l.split(":")[0].strip() for l in lines])
        formatted = []
        for l in lines:
            parts = l.split(":")
            label = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            pad = " " * (max(0, len(max_label) - len(label)))
            formatted.append(f"{label}{pad} : {value}")
        return "\n".join(formatted)