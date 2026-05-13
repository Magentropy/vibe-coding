import customtkinter as ctk
from PIL import Image, ImageSequence
import time
import threading
import winsound

# ============================================================
#  setting...
# ============================================================
WORK_MINUTES  = 1
BREAK_MINUTES = 10
GIF_PATH      = "8 Bit Cat GIF.gif"
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Focusing on the track.")
        self.geometry("420x576")
        self.resizable(False, False)

        self.is_running    = False
        self.is_break      = False
        self.seconds_left  = WORK_MINUTES * 60
        self.session_count = 1
        self.timer_thread  = None

        self.gif_frames    = []
        self.gif_index     = 0
        self.gif_job       = None

        self._load_gif()
        self._build_timer_screen()

    # ----------------------------------------------------------
    #  LOAD GIF
    # ----------------------------------------------------------
    def _load_gif(self):
        try:
            img = Image.open(GIF_PATH)
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA").resize((640, 480))
                self.gif_frames.append(ctk.CTkImage(light_image=frame, dark_image=frame, size=(640, 480)))
        except FileNotFoundError:
            pass

    # ----------------------------------------------------------
    #  LAYAR TIMER
    # ----------------------------------------------------------
    def _build_timer_screen(self):
        self.timer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_frame.pack(fill="both", expand=True, padx=32, pady=24)

        self.status_label = ctk.CTkLabel(
            self.timer_frame, text="Waktu Fokus 🍅",
            font=ctk.CTkFont(size=15)
        )
        self.status_label.pack(pady=(0, 4))

        self.time_label = ctk.CTkLabel(
            self.timer_frame, text=self._fmt(self.seconds_left),
            font=ctk.CTkFont(size=80, weight="bold")
        )
        self.time_label.pack()

        btn_frame = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶  Mulai", width=150, height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#a6e3a1", hover_color="#94d39a", text_color="#1e1e2e",
            command=self.toggle_timer
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            btn_frame, text="↺  Reset", width=150, height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#89b4fa", hover_color="#79a4ea", text_color="#1e1e2e",
            command=self.reset_timer
        ).grid(row=0, column=1, padx=8)

        self.session_label = ctk.CTkLabel(
            self.timer_frame, text="Sesi ke-1",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.session_label.pack(pady=(8, 0))

    # ----------------------------------------------------------
    #  GIF Setting
    # ----------------------------------------------------------
    def _show_cat_screen(self):
        self.timer_frame.pack_forget()
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.attributes("-topmost", True)
        self.resizable(True, True)
        self.after(100, lambda: self.state("zoomed"))

        self.cat_frame = ctk.CTkFrame(self, fg_color="#000000")
        self.cat_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.cat_frame,
            text=f"☕  chill out for {BREAK_MINUTES} minute — you are amazing..",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#cdd6f4", fg_color="transparent"
        ).pack(pady=(28, 8))

        if self.gif_frames:
            self.cat_img_label = ctk.CTkLabel(self.cat_frame, text="", fg_color="transparent")
            self.cat_img_label.pack()
            self._animate_gif()
        else:
            ctk.CTkLabel(
                self.cat_frame, text="🐱",
                font=ctk.CTkFont(size=120),
                fg_color="transparent"
            ).pack(expand=True)
            ctk.CTkLabel(
                self.cat_frame,
                text="Taruh file 'cat.gif' di folder yang sama untuk lihat kucing!",
                font=ctk.CTkFont(size=14), text_color="gray", fg_color="transparent"
            ).pack()

        self.break_time_label = ctk.CTkLabel(
            self.cat_frame, text=self._fmt(self.seconds_left),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#f9e2af", fg_color="transparent"
        )
        self.break_time_label.pack(pady=10)

        ctk.CTkButton(
            self.cat_frame, text="Lewati istirahat →", width=180, height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#fab387", hover_color="#ea9377", text_color="#1e1e2e",
            command=self.skip_break
        ).pack(pady=4)

    def _animate_gif(self):
        if not self.gif_frames:
            return
        frame = self.gif_frames[self.gif_index % len(self.gif_frames)]
        self.cat_img_label.configure(image=frame)
        self.gif_index += 1
        self.gif_job = self.after(60, self._animate_gif)

    def _hide_cat_screen(self):
        if self.gif_job:
            self.after_cancel(self.gif_job)
            self.gif_job = None
        self.attributes("-topmost", False)
        self.state("normal")
        self.geometry("420x380")
        self.resizable(False, False)
        self.cat_frame.destroy()
        self.timer_frame.pack(fill="both", expand=True, padx=32, pady=24)

    # ----------------------------------------------------------
    #  KONTROL TIMER
    # ----------------------------------------------------------
    def toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.configure(text="▶  Lanjut", fg_color="#a6e3a1")
        else:
            self.is_running = True
            self.start_btn.configure(text="⏸  Pause", fg_color="#f9e2af")
            self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self.timer_thread.start()

    def reset_timer(self):
        self.is_running   = False
        self.is_break     = False
        self.seconds_left = WORK_MINUTES * 60
        self.start_btn.configure(text="▶  Mulai", fg_color="#a6e3a1")
        self.status_label.configure(text="Waktu Fokus 🍅")
        self.time_label.configure(text=self._fmt(self.seconds_left))

    def skip_break(self):
        self.is_running = False
        self._end_break()

    def _run_timer(self):
        while self.seconds_left > 0 and self.is_running:
            time.sleep(1)
            if self.is_running:
                self.seconds_left -= 1
                self.after(0, self._tick)
        if self.seconds_left == 0:
            self.after(0, self._phase_done)

    def _tick(self):
        self.time_label.configure(text=self._fmt(self.seconds_left))
        if hasattr(self, "break_time_label"):
            self.break_time_label.configure(text=self._fmt(self.seconds_left))

    def _phase_done(self):
        self.is_running = False
        threading.Thread(target=lambda: winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS), daemon=True).start()
        if not self.is_break:
            self._start_break()
        else:
            self._end_break()

    def _start_break(self):
        self.is_break     = True
        self.seconds_left = BREAK_MINUTES * 60
        self._show_cat_screen()
        self.is_running   = True
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()

    def _end_break(self):
        self.is_break      = False
        self.session_count += 1
        self.seconds_left  = WORK_MINUTES * 60
        self._hide_cat_screen()
        self.session_label.configure(text=f"Sesi ke-{self.session_count}")
        self.status_label.configure(text="Waktu Fokus 🍅")
        self.time_label.configure(text=self._fmt(self.seconds_left))
        self.start_btn.configure(text="▶  Mulai", fg_color="#a6e3a1")

    def _fmt(self, secs):
        m, s = divmod(secs, 60)
        return f"{m:02d}:{s:02d}"

if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()