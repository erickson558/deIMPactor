"""
main.py — Tkinter GUI front-end for deIMPactor iOS IPA Sideloader.

All business logic lives in backend.py.  This module is responsible
ONLY for the user interface: layout, events, and UI state management.

Author : Synyster Rick
Version: V0.0.2
License: Apache License 2.0 — Copyright 2026, All rights reserved.
"""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Optional

import backend


class App(tk.Tk):
    """Main application window for deIMPactor."""

    # ──────────────────────────────────────────────────────────────────────────
    # Construction
    # ──────────────────────────────────────────────────────────────────────────
    def __init__(self) -> None:
        super().__init__()

        self._cfg:       dict          = backend.load_config()
        self._devices:   list[dict]    = []
        self._busy:      bool          = False
        self._save_id:   Optional[str] = None   # debounce handle for config save
        self._geo_id:    Optional[str] = None   # debounce handle for geometry save
        self._countdown: Optional[int] = None   # seconds remaining for auto-close

        self._setup_window()
        self._configure_styles()
        self._build_menu()
        self._build_ui()
        self._build_status_bar()
        self._restore_config()
        self._bind_shortcuts()

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Trigger auto-behaviours after the UI has fully rendered
        if self._cfg.get("auto_start"):
            self.after(800, self._on_refresh_then_install)
        if self._cfg.get("auto_close"):
            self._start_countdown(int(self._cfg.get("auto_close_seconds", 60)))

    # ──────────────────────────────────────────────────────────────────────────
    # Window & theme setup
    # ──────────────────────────────────────────────────────────────────────────
    def _setup_window(self) -> None:
        self.title(f"{backend.APP_NAME}   {backend.VERSION}")
        self.minsize(660, 570)
        self.resizable(True, True)

        icon_path = backend.get_base_path() / "ios_os_logo_icon_134676.ico"
        if icon_path.is_file():
            try:
                self.iconbitmap(default=str(icon_path))
            except tk.TclError:
                pass

        # Pick the best available theme for the current platform
        style = ttk.Style(self)
        for theme in ("vista", "clam", "winnative", "aqua", "alt"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

        self.configure(bg="#eef3f8")

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure("Root.TFrame", background="#eef3f8")
        style.configure(
            "Hero.TFrame",
            background="#16324f",
            relief="flat",
        )
        style.configure(
            "HeroTitle.TLabel",
            background="#16324f",
            foreground="#ffffff",
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "HeroSubtitle.TLabel",
            background="#16324f",
            foreground="#d7e5f2",
            font=("Segoe UI", 10),
        )
        style.configure(
            "VersionBadge.TLabel",
            background="#2f80ed",
            foreground="#ffffff",
            padding=(12, 5),
            font=("Segoe UI Semibold", 10),
        )
        style.configure(
            "Card.TLabelframe",
            background="#ffffff",
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Card.TLabelframe.Label",
            background="#ffffff",
            foreground="#17324d",
            font=("Segoe UI Semibold", 10),
        )
        style.configure("CardBody.TFrame", background="#ffffff")
        style.configure(
            "Hint.TLabel",
            background="#ffffff",
            foreground="#5d6b79",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(12, 8),
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(10, 8),
        )
        style.configure(
            "Status.TLabel",
            background="#eef3f8",
            foreground="#17324d",
            font=("Segoe UI", 9),
        )
        style.configure(
            "ProgressText.TLabel",
            background="#ffffff",
            foreground="#17324d",
            font=("Segoe UI Semibold", 9),
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Menu bar
    # ──────────────────────────────────────────────────────────────────────────
    def _build_menu(self) -> None:
        bar = tk.Menu(self)

        # Archivo
        m_file = tk.Menu(bar, tearoff=False)
        m_file.add_command(
            label="Salir", command=self._on_exit, accelerator="Alt+F4"
        )
        bar.add_cascade(label="Archivo", menu=m_file, underline=0)

        # Dispositivo
        m_dev = tk.Menu(bar, tearoff=False)
        m_dev.add_command(
            label="Actualizar dispositivos",
            command=self._on_refresh,
            accelerator="F5",
        )
        m_dev.add_separator()
        m_dev.add_command(
            label="Instalar IPA", command=self._on_install, accelerator="Enter"
        )
        bar.add_cascade(label="Dispositivo", menu=m_dev, underline=0)

        # Ayuda
        m_help = tk.Menu(bar, tearoff=False)
        m_help.add_command(
            label="Acerca de...", command=self._show_about, accelerator="F1"
        )
        bar.add_cascade(label="Ayuda", menu=m_help, underline=0)

        self.config(menu=bar)

    # ──────────────────────────────────────────────────────────────────────────
    # Main UI content
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=14, style="Root.TFrame")
        root.pack(fill="both", expand=True)

        hero = ttk.Frame(root, padding=(18, 16), style="Hero.TFrame")
        hero.pack(fill="x", pady=(0, 12))
        hero.columnconfigure(0, weight=1)

        ttk.Label(
            hero,
            text=f"{backend.APP_NAME}  |  Instalador IPA para iOS",
            style="HeroTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            hero,
            text="Interfaz optimizada para Windows, sin consola visible y con operaciones en segundo plano.",
            style="HeroSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            hero,
            text=backend.VERSION,
            style="VersionBadge.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        # ── Device section ────────────────────────────────────────────────────
        lf_dev = ttk.LabelFrame(
            root,
            text="Dispositivo iOS conectado",
            padding=10,
            style="Card.TLabelframe",
        )
        lf_dev.pack(fill="x", pady=(0, 8))
        lf_dev.columnconfigure(0, weight=1)

        self._device_var   = tk.StringVar()
        self._device_combo = ttk.Combobox(
            lf_dev, textvariable=self._device_var, state="readonly"
        )
        self._device_combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._btn_refresh = ttk.Button(
            lf_dev,
            text="Actualizar (F5)",
            command=self._on_refresh,
            width=18,
            style="Secondary.TButton",
        )
        self._btn_refresh.grid(row=0, column=1)
        ttk.Label(
            lf_dev,
            text="Conecte el dispositivo por USB y acepte la confianza en iPhone/iPad antes de actualizar.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # ── IPA file section ──────────────────────────────────────────────────
        lf_ipa = ttk.LabelFrame(
            root,
            text="Archivo IPA",
            padding=10,
            style="Card.TLabelframe",
        )
        lf_ipa.pack(fill="x", pady=(0, 8))
        lf_ipa.columnconfigure(0, weight=1)

        self._ipa_var = tk.StringVar()
        ttk.Entry(lf_ipa, textvariable=self._ipa_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(
            lf_ipa,
            text="Examinar...",
            command=self._on_browse_ipa,
            width=12,
            style="Secondary.TButton",
        ).grid(row=0, column=1)
        ttk.Label(
            lf_ipa,
            text="La ruta seleccionada se guarda automáticamente para el próximo inicio.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # ── Apple ID section ──────────────────────────────────────────────────
        lf_aid = ttk.LabelFrame(
            root,
            text="Apple ID (para firma, opcional)",
            padding=10,
            style="Card.TLabelframe",
        )
        lf_aid.pack(fill="x", pady=(0, 8))
        lf_aid.columnconfigure(1, weight=1)

        ttk.Label(lf_aid, text="Correo:").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        self._email_var = tk.StringVar()
        ttk.Entry(lf_aid, textvariable=self._email_var).grid(
            row=0, column=1, sticky="ew", pady=(0, 6)
        )

        ttk.Label(lf_aid, text="Contraseña:").grid(
            row=1, column=0, sticky="w", padx=(0, 6)
        )
        self._pwd_var = tk.StringVar()
        pwd_row = ttk.Frame(lf_aid)
        pwd_row.grid(row=1, column=1, sticky="ew")
        pwd_row.columnconfigure(0, weight=1)

        self._pwd_entry = ttk.Entry(pwd_row, textvariable=self._pwd_var, show="•")
        self._pwd_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._show_pwd_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            pwd_row,
            text="Mostrar",
            variable=self._show_pwd_var,
            command=self._toggle_password,
        ).grid(row=0, column=1)
        ttk.Label(
            lf_aid,
            text="Por seguridad la contraseña no se almacena en config.json.",
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # ── Options section ───────────────────────────────────────────────────
        lf_opt = ttk.LabelFrame(
            root,
            text="Opciones de automatización",
            padding=10,
            style="Card.TLabelframe",
        )
        lf_opt.pack(fill="x", pady=(0, 8))

        self._auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(
            lf_opt,
            text="Auto-iniciar proceso al abrir la aplicación",
            variable=self._auto_start_var,
            command=self._queue_save,
        ).pack(anchor="w")

        ac_row = ttk.Frame(lf_opt)
        ac_row.pack(anchor="w", pady=(6, 0))

        self._auto_close_var = tk.BooleanVar()
        ttk.Checkbutton(
            ac_row,
            text="Auto-cerrar después de",
            variable=self._auto_close_var,
            command=self._on_auto_close_toggle,
        ).pack(side="left")

        self._close_sec_var = tk.IntVar(value=60)
        self._spin_close = ttk.Spinbox(
            ac_row,
            from_=5,
            to=3600,
            textvariable=self._close_sec_var,
            width=6,
            command=self._queue_save,
        )
        self._spin_close.pack(side="left", padx=6)
        ttk.Label(ac_row, text="segundos").pack(side="left")
        ttk.Label(
            lf_opt,
            text="Los cambios de esta sección se guardan automáticamente al modificarlos.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        # ── Progress bar ──────────────────────────────────────────────────────
        lf_prog = ttk.LabelFrame(
            root,
            text="Progreso de instalación",
            padding=10,
            style="Card.TLabelframe",
        )
        lf_prog.pack(fill="x", pady=(0, 8))
        lf_prog.columnconfigure(0, weight=1)

        self._progress_var = tk.IntVar(value=0)
        self._progress = ttk.Progressbar(
            lf_prog,
            variable=self._progress_var,
            maximum=100,
            mode="determinate",
        )
        self._progress.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._progress_text_var = tk.StringVar(value="0%")
        ttk.Label(
            lf_prog,
            textvariable=self._progress_text_var,
            style="ProgressText.TLabel",
        ).grid(row=0, column=1, sticky="e")

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = ttk.Frame(root)
        btn_row.pack(fill="x")

        self._btn_install = ttk.Button(
            btn_row,
            text="Instalar IPA (Enter)",
            command=self._on_install,
            width=22,
            style="Primary.TButton",
        )
        self._btn_install.pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_row,
            text="Salir (Esc)",
            command=self._on_exit,
            width=14,
            style="Secondary.TButton",
        ).pack(side="right")

    # ──────────────────────────────────────────────────────────────────────────
    # Status bar
    # ──────────────────────────────────────────────────────────────────────────
    def _build_status_bar(self) -> None:
        ttk.Separator(self, orient="horizontal").pack(fill="x", side="bottom")
        bar = ttk.Frame(self, relief="sunken")
        bar.pack(fill="x", side="bottom")

        self._status_var = tk.StringVar(
            value=f"Listo  |  {backend.APP_NAME} {backend.VERSION}"
        )
        ttk.Label(
            bar,
            textvariable=self._status_var,
            anchor="w",
            padding=(6, 2),
            style="Status.TLabel",
        ).pack(side="left", fill="x", expand=True)

        self._countdown_var = tk.StringVar(value="")
        ttk.Label(
            bar,
            textvariable=self._countdown_var,
            anchor="e",
            padding=(0, 2, 8, 2),
            style="Status.TLabel",
        ).pack(side="right")

    # ──────────────────────────────────────────────────────────────────────────
    # Restore config → window geometry and widget state
    # ──────────────────────────────────────────────────────────────────────────
    def _restore_config(self) -> None:
        cfg = self._cfg
        x = max(0,   int(cfg.get("window_x",      100)))
        y = max(0,   int(cfg.get("window_y",       100)))
        w = max(660, int(cfg.get("window_width",   780)))
        h = max(570, int(cfg.get("window_height",  660)))
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._email_var.set(cfg.get("apple_id", ""))
        self._auto_start_var.set(bool(cfg.get("auto_start", False)))
        self._auto_close_var.set(bool(cfg.get("auto_close", False)))
        self._close_sec_var.set(int(cfg.get("auto_close_seconds", 60)))

        last = cfg.get("last_ipa_path", "")
        if last and Path(last).is_file():
            self._ipa_var.set(last)

        # Auto-save traces (registered after initial set to avoid false saves)
        self._email_var.trace_add("write",     lambda *_: self._queue_save())
        self._ipa_var.trace_add("write",       lambda *_: self._queue_save())
        self._close_sec_var.trace_add("write", lambda *_: self._queue_save())
        self._cfg["version"] = backend.VERSION

    # ──────────────────────────────────────────────────────────────────────────
    # Config persistence (debounced)
    # ──────────────────────────────────────────────────────────────────────────
    def _queue_save(self, *_) -> None:
        """Schedule a config flush in 400 ms; cancels any pending flush."""
        if self._save_id:
            self.after_cancel(self._save_id)
        self._save_id = self.after(400, self._flush_save)

    def _flush_save(self) -> None:
        """Collect current UI state and persist config immediately."""
        self._save_id = None
        try:
            self._cfg.update({
                "window_x":           self.winfo_x(),
                "window_y":           self.winfo_y(),
                "window_width":       self.winfo_width(),
                "window_height":      self.winfo_height(),
                "auto_start":         self._auto_start_var.get(),
                "auto_close":         self._auto_close_var.get(),
                "auto_close_seconds": int(self._close_sec_var.get()),
                "apple_id":           self._email_var.get().strip(),
                # NOTE: La contraseña NO se guarda por seguridad
                "last_ipa_path":      self._ipa_var.get().strip(),
                "last_ipa_dir": (
                    str(Path(self._ipa_var.get()).parent)
                    if self._ipa_var.get()
                    else self._cfg.get("last_ipa_dir", "")
                ),
            })
            backend.save_config(self._cfg)
        except Exception as exc:
            backend.logger.debug(f"_flush_save omitido: {exc}")

    # ──────────────────────────────────────────────────────────────────────────
    # Keyboard shortcuts
    # ──────────────────────────────────────────────────────────────────────────
    def _bind_shortcuts(self) -> None:
        self.bind("<Return>", lambda _e: self._on_install())
        self.bind("<Escape>", lambda _e: self._on_exit())
        self.bind("<F5>",     lambda _e: self._on_refresh())
        self.bind("<F1>",     lambda _e: self._show_about())

    # ──────────────────────────────────────────────────────────────────────────
    # Thread-safe UI helpers
    # ──────────────────────────────────────────────────────────────────────────
    def _set_status(self, msg: str) -> None:
        self.after(0, self._status_var.set, msg)

    def _set_progress(self, pct: int) -> None:
        self.after(0, self._progress_var.set, pct)
        self.after(0, self._progress_text_var.set, f"{pct}%")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.after(0, lambda: self._btn_install.config(state=state))
        self.after(0, lambda: self._btn_refresh.config(state=state))

    # ──────────────────────────────────────────────────────────────────────────
    # Password show / hide
    # ──────────────────────────────────────────────────────────────────────────
    def _toggle_password(self) -> None:
        self._pwd_entry.config(show="" if self._show_pwd_var.get() else "•")

    # ──────────────────────────────────────────────────────────────────────────
    # Auto-close countdown
    # ──────────────────────────────────────────────────────────────────────────
    def _start_countdown(self, seconds: int) -> None:
        self._countdown = max(1, seconds)
        self._tick()

    def _cancel_countdown(self) -> None:
        self._countdown = None
        self._countdown_var.set("")

    def _tick(self) -> None:
        if self._countdown is None:
            return
        if self._countdown <= 0:
            self._countdown_var.set("Cerrando…")
            self.after(600, self._on_exit)
            return
        self._countdown_var.set(f"Auto-cierre en {self._countdown}s")
        self._countdown -= 1
        self.after(1000, self._tick)

    def _on_auto_close_toggle(self) -> None:
        self._queue_save()
        if self._auto_close_var.get():
            self._start_countdown(int(self._close_sec_var.get()))
        else:
            self._cancel_countdown()

    # ──────────────────────────────────────────────────────────────────────────
    # Window geometry → auto-save (debounced to avoid thousands of writes)
    # ──────────────────────────────────────────────────────────────────────────
    def _on_configure(self, event: tk.Event) -> None:
        if event.widget is self:
            if self._geo_id:
                self.after_cancel(self._geo_id)
            self._geo_id = self.after(500, self._queue_save)

    # ──────────────────────────────────────────────────────────────────────────
    # About dialog
    # ──────────────────────────────────────────────────────────────────────────
    def _show_about(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(f"Acerca de {backend.APP_NAME}")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        text = (
            f"{backend.APP_NAME} {backend.VERSION}\n\n"
            f"Creado por {backend.AUTHOR}\n"
            f"{backend.YEAR} Derechos Reservados\n\n"
            "iOS IPA Sideloader para Windows\n"
            "Instala apps .ipa en dispositivos iOS conectados por USB."
        )
        ttk.Label(dlg, text=text, justify="center", padding=24).pack()
        ttk.Button(dlg, text="Cerrar", command=dlg.destroy, width=12).pack(
            pady=(0, 16)
        )
        dlg.bind("<Escape>", lambda _: dlg.destroy())
        dlg.bind("<Return>", lambda _: dlg.destroy())
        dlg.focus_set()

    # ──────────────────────────────────────────────────────────────────────────
    # Browse IPA
    # ──────────────────────────────────────────────────────────────────────────
    def _on_browse_ipa(self) -> None:
        init = self._cfg.get("last_ipa_dir", "") or str(Path.home())
        path = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo IPA",
            initialdir=init,
            filetypes=[
                ("iOS App Package", "*.ipa"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if path:
            self._ipa_var.set(path)

    # ──────────────────────────────────────────────────────────────────────────
    # Refresh device list
    # ──────────────────────────────────────────────────────────────────────────
    def _on_refresh(self) -> None:
        self._set_status("Buscando dispositivos iOS…")
        self._btn_refresh.config(state="disabled")

        def _task() -> None:
            devices = backend.list_devices()
            self.after(0, self._populate_devices, devices)

        threading.Thread(target=_task, daemon=True).start()

    def _populate_devices(self, devices: list[dict]) -> None:
        self._devices = devices
        self._btn_refresh.config(state="normal")
        if devices:
            labels = [
                f"{d['name']}  ({d['model']})  iOS {d['ios_version']}  "
                f"[{d['udid'][:12]}…]"
                for d in devices
            ]
            self._device_combo["values"] = labels
            self._device_combo.current(0)
            self._set_status(f"{len(devices)} dispositivo(s) encontrado(s)")
        else:
            self._device_combo["values"] = ["Sin dispositivos"]
            self._device_combo.current(0)
            self._set_status(
                "No se encontraron dispositivos. "
                "Conecte su iPhone/iPad y confíe en este equipo."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Auto-start: refresh then install
    # ──────────────────────────────────────────────────────────────────────────
    def _on_refresh_then_install(self) -> None:
        self._set_status("Auto-inicio: buscando dispositivos…")

        def _task() -> None:
            devices = backend.list_devices()
            self.after(0, self._populate_devices, devices)
            if devices:
                self.after(0, self._on_install)

        threading.Thread(target=_task, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────────
    # Install IPA
    # ──────────────────────────────────────────────────────────────────────────
    def _on_install(self) -> None:
        if self._busy:
            return

        ipa = self._ipa_var.get().strip()
        if not ipa:
            self._set_status("⚠  Seleccione un archivo .ipa antes de instalar")
            return
        if not Path(ipa).is_file():
            self._set_status(f"⚠  Archivo no encontrado: {ipa}")
            return

        idx = self._device_combo.current()
        if idx < 0 or not self._devices:
            self._set_status("⚠  No hay dispositivo seleccionado. Presione Actualizar.")
            return

        udid = self._devices[idx]["udid"]
        self._set_busy(True)
        self._set_progress(0)
        self._set_status(
            f"Iniciando instalación en {self._devices[idx]['name']}…"
        )

        backend.install_ipa_threaded(
            udid=udid,
            ipa_path=ipa,
            on_progress=self._set_progress,
            on_status=self._set_status,
            on_done=self._on_install_done,
        )

    def _on_install_done(self, success: bool) -> None:
        self._set_busy(False)
        if success:
            self._set_progress(100)

    # ──────────────────────────────────────────────────────────────────────────
    # Exit
    # ──────────────────────────────────────────────────────────────────────────
    def _on_exit(self) -> None:
        if self._save_id:
            self.after_cancel(self._save_id)
        self._flush_save()
        backend.logger.info(f"{backend.APP_NAME} cerrado por el usuario")
        self.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
