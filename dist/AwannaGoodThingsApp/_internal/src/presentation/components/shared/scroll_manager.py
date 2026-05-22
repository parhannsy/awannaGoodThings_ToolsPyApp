"""
Komponen: ScrollManager
Logic untuk scroll ke header tabel tertentu.
"""


class ScrollManager:
    """Manager untuk scroll operations."""

    def __init__(self, tables_container):
        self.tables_container = tables_container
        self._scroll_job = None

    def scroll_to_table(self, index, after_callback=None):
        """Schedule scroll ke tabel dengan index tertentu."""
        if self._scroll_job is not None:
            self.tables_container.container.after_cancel(self._scroll_job)

        self._scroll_job = self.tables_container.container.after(
            50,
            lambda: self._perform_scroll(index, after_callback)
        )

    def _perform_scroll(self, index, after_callback=None):
        """Execute scroll ke header tabel."""
        try:
            header = self.tables_container.get_header_label(index)
            if not header:
                return

            canvas = self.tables_container.get_canvas()
            self.tables_container.container.update_idletasks()
            canvas.update_idletasks()

            bbox = canvas.bbox("all")
            if not bbox:
                return

            total_height = bbox[3] - bbox[1]
            if total_height <= 0:
                return

            # Calculate position
            header_root_y = header.winfo_rooty()
            content_root_y = self.tables_container.container.winfo_rooty()
            header_y = header_root_y - content_root_y - 10

            fraction = header_y / total_height
            fraction = min(1.0, max(0.0, fraction))

            canvas.yview_moveto(fraction)

            if after_callback:
                after_callback()

        except Exception as e:
            print(f"[DEBUG] Scroll error: {e}")
        finally:
            self._scroll_job = None

    def reset_scroll(self):
        """Reset scroll ke atas."""
        try:
            canvas = self.tables_container.get_canvas()
            canvas.yview_moveto(0.0)
        except:
            pass

    def cancel_pending(self):
        """Cancel pending scroll job."""
        if self._scroll_job is not None:
            self.tables_container.container.after_cancel(self._scroll_job)
            self._scroll_job = None