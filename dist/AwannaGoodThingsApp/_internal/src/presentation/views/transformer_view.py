"""
View: TransformerView
Halaman transformasi dan cleaning data.
"""

import threading
import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox

from src.presentation.components.shared.page_header import PageHeader
from src.presentation.components.shared.toast import Toast

from src.presentation.components.dataTransformer import (
    FileInput,
    PlatformSelector,
    ProcessButton
)

# CATATAN MENTOR: Path import ini sebaiknya dipindah dari presentation ke domain/infrastructure.
# Untuk saat ini disesuaikan dengan struktur komponen yang kamu miliki agar tidak breaking.
from src.presentation.components.dataTransformer.data_processor_spx import DataProcessorSPX
from src.presentation.components.dataTransformer.data_processor_flik import DataProcessorFLIK


class TransformerView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.selected_file = ctk.StringVar()
        self.platform_var = ctk.StringVar(value="SPX")

        # Mapping platform ke class processor masing-masing untuk menghindari if-else berulang (DRY)
        self._processors = {
            "SPX": DataProcessorSPX,
            "FLIK": DataProcessorFLIK
        }

        self._setup_ui()

    # ==================================================
    # UI
    # ==================================================

    def _setup_ui(self):
        self.configure(fg_color="transparent")

        # =====================
        # HEADER
        # =====================
        self.header = PageHeader(
            master=self,
            title="Data Transformer",
            subtitle=(
                "Alat bantu yang diminta sama "
                "baginda kanjeng dimas adipati "
                "IDUY sang ATMIN😊🙏."
            )
        )

        # =====================
        # CONTENT CARD
        # =====================
        self.content_card = ctk.CTkFrame(
            self,
            fg_color=("gray86", "gray17"),
            corner_radius=8
        )
        self.content_card.pack(
            fill="x",
            pady=(5, 0),
            padx=5
        )

        # =====================
        # FORM AREA
        # =====================
        self.form_frame = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent"
        )
        self.form_frame.pack(
            fill="x",
            padx=30,
            pady=30
        )

        # =====================
        # FILE INPUT
        # =====================
        self.file_input = FileInput(
            self.form_frame,
            file_var=self.selected_file
        )
        self.file_input.pack(fill="x")

        # =====================
        # PLATFORM
        # =====================
        self.platform_selector = PlatformSelector(
            self.form_frame,
            variable=self.platform_var
        )
        self.platform_selector.pack(
            fill="x",
            pady=(25, 0)
        )

        # =====================
        # BUTTON
        # =====================
        self.process_button = ProcessButton(
            self.form_frame,
            command=self._on_process_click
        )
        self.process_button.pack(
            fill="x",
            pady=(30, 0)
        )

    # ==================================================
    # EVENT HANDLER
    # ==================================================

    def _on_process_click(self):
        selected_platform = self.platform_var.get()
        file_path = self.selected_file.get()

        # Validation
        if not file_path:
            messagebox.showwarning(
                "File Belum Dipilih",
                "Mohon pilih file terlebih dahulu."
            )
            return

        processor = self._processors.get(selected_platform)
        if not processor:
            messagebox.showerror(
                "Platform Tidak Dikenal",
                f"Processor untuk platform {selected_platform} tidak ditemukan."
            )
            return

        # Get save location
        output_path = filedialog.asksaveasfilename(
            title="Simpan Hasil Transformasi",
            defaultextension=".xlsx",
            initialfile=processor.generate_default_filename(),
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if not output_path:
            return

        # Update Button State
        self.process_button.configure(
            state="disabled",
            text="Memproses..."
        )

        # Threading Execution (Universal untuk semua platform)
        threading.Thread(
            target=self._run_transform_process,
            args=(processor, file_path, output_path),
            daemon=True
        ).start()

    # ==================================================
    # PROCESSOR (DYNAMIC & CENTRALIZED)
    # ==================================================

    def _run_transform_process(self, processor, input_file, output_file):
        """
        Fungsi pemroses tunggal yang menerima objek processor secara dinamis.
        Menggantikan _run_spx_process dan _run_flik_process yang duplikat.
        """
        try:
            result = processor.process(
                input_file=input_file,
                output_file=output_file
            )
            self.after(0, self._on_process_success, result)

        except Exception as e:
            error_message = str(e)
            self.after(0, self._on_process_error, error_message)

    # ==================================================
    # CALLBACK
    # ==================================================

    def _on_process_success(self, result):
        self.process_button.configure(
            state="normal",
            text="Proses"
        )

        total_data = 0
        if isinstance(result, dict):
            total_data = result.get("total_data", 0)

        self._show_success(
            f"Transformasi berhasil.\n"
            f"Total Data : {total_data}"
        )

    def _on_process_error(self, error_message):
        self.process_button.configure(
            state="normal",
            text="Proses"
        )

        self._show_error(
            f"Transformasi gagal.\n\n"
            f"{error_message}"
        )

    # ==================================================
    # NOTIFICATION
    # ==================================================

    def _show_success(self, message):
        Toast.success(
            master=self.winfo_toplevel(),
            message=message
        )

    def _show_error(self, message):
        Toast.error(
            master=self.winfo_toplevel(),
            message=message
        )

    # ==================================================
    # LIFECYCLE
    # ==================================================

    def on_show(self):
        pass