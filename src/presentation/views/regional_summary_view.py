"""
View: RegionalSummaryView
Halaman agregasi data per wilayah dengan kalibrasi provinsi.
Hanya sebagai orchestrator — memanggil komponen shared dan processor data bisnis.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

# Import komponen Shared
from src.presentation.components.shared.page_header import PageHeader
from src.presentation.components.shared.input_section import InputSection
from src.presentation.components.shared.info_section import InfoSection
from src.presentation.components.shared.nav_section import NavSection
from src.presentation.components.shared.tables_container import TablesContainer
from src.presentation.components.shared.scroll_manager import ScrollManager

# Import spesifik dari regional_summary
from src.presentation.components.regional_summary.excel_exporter import ExcelExporter
from src.presentation.components.regional_summary.data_processor import RegionalDataProcessor


MASTER_PROVINCES = [
    "BALI", "BANGKA BELITUNG", "BANTEN", "BENGKULU", "DI YOGYAKARTA",
    "DKI JAKARTA", "GORONTALO", "JAMBI", "JAWA BARAT", "JAWA TENGAH",
    "JAWA TIMUR", "KALIMANTAN BARAT", "KALIMANTAN SELATAN", "KALIMANTAN TENGAH",
    "KALIMANTAN TIMUR", "KALIMANTAN UTARA", "KEPULAUAN RIAU", "LAMPUNG",
    "MALUKU", "MALUKU UTARA", "NANGGROE ACEH DARUSSALAM (NAD)",
    "NUSA TENGGARA BARAT (NTB)", "NUSA TENGGARA TIMUR (NTT)", "PAPUA",
    "PAPUA BARAT", "RIAU", "SULAWESI BARAT", "SULAWESI SELATAN",
    "SULAWESI TENGAH", "SULAWESI TENGGARA", "SULAWESI UTARA",
    "SUMATERA BARAT", "SUMATERA SELATAN", "SUMATERA UTARA"
]


class RegionalSummaryView(ctk.CTkFrame):
    """View orchestrator untuk Regional Summary."""

    TABLES_PER_PAGE = 10  # Maksimal tabel yang dirender per halaman

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.current_file_path = None
        self.dates_list = []
        self.current_results = {}
        self.active_table_index = 0
        self.current_page = 0
        self.all_tables_payload = []

        # Inisialisasi Data Processor Logika Bisnis
        self.data_processor = RegionalDataProcessor(master_provinces=MASTER_PROVINCES)

        self._setup_ui()

    def _setup_ui(self):
        """Build UI Layout."""
        self.configure(fg_color="transparent")
        
        # Page Title
        self.header = PageHeader(
            master=self,
            title="Regional Summary Analytics",
            subtitle="Agregasi dan kalkulasi rasio lead/paid data per wilayah provinsi secara berkala."
        )

        # Input Section
        self.input_section = InputSection(
            self,
            title_label="Belum ada file summary dipilih",
            browse_text="📁 Pilih File Summary",
            process_text="▶ Proses Data",
            clear_text="🧹 Bersihkan",
            on_browse=self._on_file_selected,
            on_process=self._process_data,
            on_clear=self._clear_all
        )

        # Output Card Wrapper
        self.output_card = ctk.CTkFrame(self, fg_color=("gray86", "gray17"), corner_radius=8)
        self.output_card.pack_forget()

        # Info & Warnings
        self.info_section = InfoSection(self.output_card)

        # Navigation Buttons Carousel
        self.nav_section = NavSection(
            self.output_card, 
            label_text="Lompat ke tabel tanggal:",
            on_navigate=self._on_nav_click
        )

        # Pagination Controls
        self.pagination_frame = ctk.CTkFrame(self.output_card, fg_color="transparent")
        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="◀ Prev",
            command=self._prev_page,
            width=80,
            height=28
        )
        self.prev_btn.pack(side="left", padx=(0, 10))

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Halaman 1 / 1",
            font=ctk.CTkFont(size=11)
        )
        self.page_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Next ▶",
            command=self._next_page,
            width=80,
            height=28
        )
        self.next_btn.pack(side="right", padx=(10, 0))

        # Tables Scrollable Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.output_card,
            fg_color=("gray90", "gray13"),
            corner_radius=6
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tables_container = TablesContainer(
            self.scroll_frame,
            on_table_click=self._on_table_click
        )

        # Logic Helper Components
        self.scroll_manager = ScrollManager(self.tables_container)
        self.excel_exporter = ExcelExporter(get_data_fn=self._get_export_data)

        # Action Button Export
        self.export_btn = ctk.CTkButton(
            self.output_card,
            text="📊 Ekspor Semua ke Excel",
            command=self._export_to_excel,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=28
        )
        self.export_btn.place(relx=1.0, rely=0.02, anchor="ne", x=-15)

    def on_show(self):
        """Lifecycle hook aplikasi."""
        pass

    def _on_file_selected(self, file_path):
        self.current_file_path = file_path

    def _format_indonesian_date(self, date_str):
        """
        Helper profesional untuk mengonversi format 'YYYY-MM-DD' menjadi 
        'Rangkuman data {Hari}, DD {Bulan} YYYY' sesuai lokalisasi Indonesia.
        """
        if date_str in ['ALL_DATA', 'TANPA_TANGGAL']:
            return "📁 Rekap Data Campuran"

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Mapping nama hari bahasa Indonesia
            hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            hari_indo = hari_list[date_obj.weekday()]
            
            # Mapping nama bulan bahasa Indonesia
            bulan_list = [
                "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            bulan_indo = bulan_list[date_obj.month]
            
            return f"Rangkuman data {hari_indo}, {date_obj.day} {bulan_indo} {date_obj.year}"
        except Exception:
            return f"Tanggal: {date_str}"

    def _process_data(self):
        """Callback UI untuk memproses data menggunakan Processor terpisah."""
        if not self.current_file_path:
            return

        try:
            # PEMBAHARUAN LOGIKA: Delegasikan tugas berat ke data_processor
            data_pack = self.data_processor.process_file(self.current_file_path)

            # Simpan state internal untuk kebutuhan navigasi lokal dan export
            self.dates_list = data_pack["dates_list"]
            self.current_results = data_pack["results_by_date"]
            self.all_tables_payload = []
            self.current_page = 0

            if not self.dates_list:
                raise ValueError("Tidak ada data valid untuk diproses.")

            # Tampilkan Card Output Utama
            self.output_card.pack(fill="both", expand=True, pady=(5, 0))

            # 1. Update Info Section
            stats = data_pack["global_stats"]
            self.info_section.display_info(
                f"Rangkuman Total File || Total Lead: {stats['total_leads']} - Total Paid: {stats['total_paid']} - Ratio: {stats['ratio']:.1f}%"
            )
            
            # 2. Update Warning Section
            warns = data_pack["warnings"]
            self.info_section.display_warning(
                f"⚠️ Terdapat {warns['dropped_rows']} data dibuang karena nama provinsi tidak sesuai master." 
                if warns["has_warning"] else ""
            )

            # 3. Render Carousel Nav Buttons Payload (semua tanggal)
            buttons_payload = []
            for idx, date_str in enumerate(self.dates_list):
                try:
                    day_text = f"Tgl {datetime.strptime(date_str, '%Y-%m-%d').strftime('%d')}"
                except:
                    day_text = date_str
                buttons_payload.append({"id": idx, "display_text": day_text})
            self.nav_section.create_buttons(buttons_payload)

            # 4. Build ALL tables payload tapi simpan, jangan render semua
            for idx, date_str in enumerate(self.dates_list):
                df_res = self.current_results[date_str]['dataframe']
                
                t_leads = df_res['leads'].sum()
                t_paid = df_res['paid'].sum()
                t_ratio = (t_paid / t_leads * 100) if t_leads > 0 else 0.0
                
                rows_list = []
                for _, row in df_res.iterrows():
                    rows_list.append([row['province_clean'], row['leads'], row['paid']])

                self.all_tables_payload.append({
                    "key_id": idx,
                    "title": f"📅 Tanggal {date_str}",
                    "sub_info": f"Leads: {t_leads} | Paid: {t_paid} | Ratio: {t_ratio:.1f}%",
                    "headers": ["PROVINSI", "LEADS", "PAID"],
                    "rows": rows_list
                })

            # 5. Render halaman pertama
            self._render_page(0)

            # 6. Tampilkan pagination jika lebih dari 1 halaman
            total_pages = (len(self.all_tables_payload) + self.TABLES_PER_PAGE - 1) // self.TABLES_PER_PAGE
            if total_pages > 1:
                self.pagination_frame.pack(fill="x", padx=15, pady=(5, 0))
            else:
                self.pagination_frame.pack_forget()

            # Reset fokus tampilan awal
            self.active_table_index = 0
            self._update_active_state()
            self.scroll_manager.reset_scroll()

        except Exception as e:
            messagebox.showerror("Error Pemrosesan", f"Gagal memproses file:\n{str(e)}")
            self._clear_all()

    def _render_page(self, page_num):
        """Render hanya tabel untuk halaman tertentu."""
        start_idx = page_num * self.TABLES_PER_PAGE
        end_idx = start_idx + self.TABLES_PER_PAGE
        page_payload = self.all_tables_payload[start_idx:end_idx]

        self.tables_container.clear()
        self.tables_container.create_tables(page_payload)

        self.current_page = page_num
        self._update_pagination_ui()

    def _update_pagination_ui(self):
        """Update tampilan tombol pagination."""
        total_pages = (len(self.all_tables_payload) + self.TABLES_PER_PAGE - 1) // self.TABLES_PER_PAGE
        self.page_label.configure(text=f"Halaman {self.current_page + 1} / {total_pages}")

        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")

    def _prev_page(self):
        """Navigasi ke halaman sebelumnya."""
        if self.current_page > 0:
            self._render_page(self.current_page - 1)
            self.scroll_manager.reset_scroll()

    def _next_page(self):
        """Navigasi ke halaman berikutnya."""
        total_pages = (len(self.all_tables_payload) + self.TABLES_PER_PAGE - 1) // self.TABLES_PER_PAGE
        if self.current_page < total_pages - 1:
            self._render_page(self.current_page + 1)
            self.scroll_manager.reset_scroll()

    def _on_nav_click(self, index):
        """Handle klik tombol navigasi carousel."""
        # Hitung halaman mana yang mengandung index ini
        page_num = index // self.TABLES_PER_PAGE
        if page_num != self.current_page:
            self._render_page(page_num)
        # Scroll ke tabel yang sesuai di halaman tersebut
        self._scroll_to_table(index % self.TABLES_PER_PAGE)

    def _on_table_click(self, index):
        self._scroll_to_table(index)

    def _scroll_to_table(self, index):
        if index < 0 or index >= self.TABLES_PER_PAGE:
            return
        self.active_table_index = index
        self._update_active_state()
        self.scroll_manager.scroll_to_table(index)

    def _update_active_state(self):
        self.tables_container.set_active_table(self.active_table_index)
        # Map kembali ke index global untuk nav_section
        global_index = self.active_table_index + (self.current_page * self.TABLES_PER_PAGE)
        self.nav_section.set_active(global_index)

    def _get_export_data(self):
        return self.dates_list, self.current_results

    def _export_to_excel(self):
        self.excel_exporter.save(default_filename="regional_summary_report")

    def _clear_all(self):
        self.output_card.pack_forget()
        self.pagination_frame.pack_forget()
        self.dates_list = []
        self.current_results = {}
        self.all_tables_payload = []
        self.active_table_index = 0
        self.current_page = 0
        
        self.input_section.reset()
        self.info_section.clear()
        self.nav_section.clear()
        self.tables_container.clear()
        self.scroll_manager.reset_scroll()