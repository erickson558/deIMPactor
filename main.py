"""
main.py - Tkinter GUI front-end for deIMPactor iOS IPA Sideloader.

All business logic lives in backend.py. This module is responsible
only for user interface layout, events, and UI state management.

Author : Synyster Rick
Version: V0.1.0
License: Apache License 2.0 - Copyright 2026, All rights reserved.
"""
from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Optional

import backend


class App(tk.Tk):
    """Main application window for deIMPactor."""

    DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN"

    # UI copy dictionary for Spanish and English.
    I18N = {
        "es": {
            "hero_title": f"{backend.APP_NAME}  |  Instalador IPA para iOS",
            "hero_subtitle": "Interfaz optimizada para Windows, sin consola visible y con operaciones en segundo plano.",
            "menu_file": "Archivo",
            "menu_exit": "Salir",
            "menu_device": "Dispositivo",
            "menu_refresh": "Actualizar dispositivos",
            "menu_install": "Instalar IPA",
            "menu_help": "Ayuda",
            "menu_about": "Acerca de...",
            "menu_language": "Idioma",
            "lang_es": "Espanol",
            "lang_en": "Ingles",
            "section_device": "Dispositivo iOS conectado",
            "btn_refresh": "Actualizar (F5)",
            "device_hint": "Conecte el dispositivo por USB y acepte la confianza en iPhone/iPad antes de actualizar.",
            "section_ipa": "Archivo IPA",
            "btn_browse": "Examinar...",
            "ipa_hint": "La ruta seleccionada se guarda automaticamente para el proximo inicio.",
            "section_appleid": "Apple ID (para firma, opcional)",
            "label_email": "Correo:",
            "label_password": "Contrasena:",
            "show_password": "Mostrar",
            "appleid_hint": "Por seguridad la contrasena no se almacena en config.json.",
            "section_options": "Opciones de automatizacion",
            "opt_auto_start": "Auto-iniciar proceso al abrir la aplicacion",
            "opt_auto_close": "Auto-cerrar despues de",
            "seconds": "segundos",
            "opt_hint": "Los cambios de esta seccion se guardan automaticamente al modificarlos.",
            "section_progress": "Progreso de instalacion",
            "section_support": "Soporte y comunidad",
            "support_hint": "Si te ayuda este proyecto, puedes apoyar su mantenimiento con una donacion.",
            "btn_donate": "Comprame una cerveza",
            "label_language": "Idioma:",
            "btn_install": "Instalar IPA (Enter)",
            "btn_exit": "Salir (Esc)",
            "status_ready": f"Listo  |  {backend.APP_NAME} {backend.VERSION}",
            "status_deps_validating": "Validando dependencias del entorno...",
            "status_deps_ready": "Dependencias listas y verificadas. Presione F5 para detectar el iPhone.",
            "status_wait_deps": "Instalando dependencias, espere unos segundos...",
            "status_searching": "Buscando dispositivos iOS...",
            "status_no_devices": "No se encontraron dispositivos. Conecte su iPhone/iPad y confie en este equipo.",
            "status_devices_found": "{count} dispositivo(s) encontrado(s)",
            "status_auto_start": "Auto-inicio: buscando dispositivos...",
            "status_need_ipa": "[AVISO] Seleccione un archivo .ipa antes de instalar",
            "status_file_missing": "[AVISO] Archivo no encontrado: {ipa}",
            "status_no_device": "[AVISO] No hay dispositivo seleccionado. Presione Actualizar.",
            "status_install_start": "Iniciando instalacion en {name}...",
            "status_auto_close": "Auto-cierre en {seconds}s",
            "status_closing": "Cerrando...",
            "status_donate_opening": "Abriendo enlace de donacion en su navegador...",
            "status_donate_error": "No se pudo abrir el enlace de donacion: {err}",
            "about_title": f"Acerca de {backend.APP_NAME}",
            "about_body": (
                f"{backend.APP_NAME} {backend.VERSION}\n\n"
                f"Creado por {backend.AUTHOR}\n"
                f"{backend.YEAR} Derechos Reservados\n\n"
                "iOS IPA Sideloader para Windows\n"
                "Instala apps .ipa en dispositivos iOS conectados por USB."
            ),
            "btn_close": "Cerrar",
            "dlg_select_ipa": "Seleccionar archivo IPA",
            "device_missing_value": "Dependencia faltante",
            "device_empty_value": "Sin dispositivos",
        },
        "en": {
            "hero_title": f"{backend.APP_NAME}  |  IPA Installer for iOS",
            "hero_subtitle": "Windows-optimized interface with hidden console and background operations.",
            "menu_file": "File",
            "menu_exit": "Exit",
            "menu_device": "Device",
            "menu_refresh": "Refresh devices",
            "menu_install": "Install IPA",
            "menu_help": "Help",
            "menu_about": "About...",
            "menu_language": "Language",
            "lang_es": "Spanish",
            "lang_en": "English",
            "section_device": "Connected iOS device",
            "btn_refresh": "Refresh (F5)",
            "device_hint": "Connect the device via USB and trust this computer on iPhone/iPad before refreshing.",
            "section_ipa": "IPA file",
            "btn_browse": "Browse...",
            "ipa_hint": "Selected path is automatically saved for the next launch.",
            "section_appleid": "Apple ID (for signing, optional)",
            "label_email": "Email:",
            "label_password": "Password:",
            "show_password": "Show",
            "appleid_hint": "For security reasons, the password is not stored in config.json.",
            "section_options": "Automation options",
            "opt_auto_start": "Auto-start process when opening the app",
            "opt_auto_close": "Auto-close after",
            "seconds": "seconds",
            "opt_hint": "Changes in this section are saved automatically when modified.",
            "section_progress": "Installation progress",
            "section_support": "Support and community",
            "support_hint": "If this project helps you, you can support maintenance with a donation.",
            "btn_donate": "Buy me a beer",
            "label_language": "Language:",
            "btn_install": "Install IPA (Enter)",
            "btn_exit": "Exit (Esc)",
            "status_ready": f"Ready  |  {backend.APP_NAME} {backend.VERSION}",
            "status_deps_validating": "Validating runtime dependencies...",
            "status_deps_ready": "Dependencies are ready and verified. Press F5 to detect your iPhone.",
            "status_wait_deps": "Installing dependencies, please wait a few seconds...",
            "status_searching": "Searching for iOS devices...",
            "status_no_devices": "No devices found. Connect your iPhone/iPad and trust this computer.",
            "status_devices_found": "{count} device(s) found",
            "status_auto_start": "Auto-start: searching devices...",
            "status_need_ipa": "[WARNING] Select an .ipa file before installing",
            "status_file_missing": "[WARNING] File not found: {ipa}",
            "status_no_device": "[WARNING] No device selected. Press Refresh.",
            "status_install_start": "Starting installation on {name}...",
            "status_auto_close": "Auto-close in {seconds}s",
            "status_closing": "Closing...",
            "status_donate_opening": "Opening donation link in your browser...",
            "status_donate_error": "Could not open donation link: {err}",
            "about_title": f"About {backend.APP_NAME}",
            "about_body": (
                f"{backend.APP_NAME} {backend.VERSION}\n\n"
                f"Created by {backend.AUTHOR}\n"
                f"{backend.YEAR} All rights reserved\n\n"
                "iOS IPA Sideloader for Windows\n"
                "Install .ipa apps on USB-connected iOS devices."
            ),
            "btn_close": "Close",
            "dlg_select_ipa": "Select IPA file",
            "device_missing_value": "Missing dependency",
            "device_empty_value": "No devices",
        },
    }

    # Construction
    def __init__(self) -> None:
        super().__init__()

        self._cfg: dict = backend.load_config()
        self._devices: list[dict] = []
        self._busy: bool = False
        self._save_id: Optional[str] = None
        self._geo_id: Optional[str] = None
        self._countdown: Optional[int] = None
        self._countdown_id: Optional[str] = None
        self._auto_exit_id: Optional[str] = None
        self._deps_ready: bool = False
        self._deps_busy: bool = False
        self._shutting_down: bool = False

        # Language code is kept in config and reused by both menu and combobox.
        self._lang: str = self._normalize_lang(self._cfg.get("language", "es"))
        self._lang_code_var = tk.StringVar(value=self._lang)

        self._setup_window()
        self._configure_styles()
        self._build_menu()
        self._build_ui()
        self._build_status_bar()
        self._restore_config()
        self._bind_shortcuts()
        self._bootstrap_dependencies()

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

        # Trigger auto behaviours after the UI has fully rendered.
        if self._cfg.get("auto_start"):
            self._ui_call(self.after, 800, self._on_refresh_then_install)
        if self._cfg.get("auto_close"):
            self._start_countdown(int(self._cfg.get("auto_close_seconds", 60)))

    # Window and theme setup
    def _setup_window(self) -> None:
        self.title(f"{backend.APP_NAME}   {backend.VERSION}")
        self.minsize(660, 620)
        self.resizable(True, True)

        icon_path = backend.get_base_path() / "ios_os_logo_icon_134676.ico"
        if icon_path.is_file():
            try:
                self.iconbitmap(default=str(icon_path))
            except tk.TclError:
                pass

        style = ttk.Style(self)
        for theme in ("vista", "clam", "winnative", "aqua", "alt"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

        self.configure(bg="#eef3f8")

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure("Root.TFrame", background="#eef3f8")
        style.configure("Hero.TFrame", background="#16324f", relief="flat")
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
        style.configure("Card.TLabelframe", background="#ffffff", borderwidth=1, relief="solid")
        style.configure(
            "Card.TLabelframe.Label",
            background="#ffffff",
            foreground="#17324d",
            font=("Segoe UI Semibold", 10),
        )
        style.configure("Hint.TLabel", background="#ffffff", foreground="#5d6b79", font=("Segoe UI", 9))
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(12, 8))
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 8))
        style.configure("Status.TLabel", background="#eef3f8", foreground="#17324d", font=("Segoe UI", 9))
        style.configure(
            "ProgressText.TLabel",
            background="#ffffff",
            foreground="#17324d",
            font=("Segoe UI Semibold", 9),
        )

    # Language helpers
    def _normalize_lang(self, value: str) -> str:
        return value if value in self.I18N else "es"

    def _tr(self, key: str, **kwargs: object) -> str:
        text = self.I18N.get(self._lang, self.I18N["es"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _lang_display(self, code: str) -> str:
        return self._tr("lang_es") if code == "es" else self._tr("lang_en")

    def _language_values(self) -> list[str]:
        return [self._tr("lang_es"), self._tr("lang_en")]

    # Thread-safe UI scheduling helpers
    def _ui_call(self, fn, *args) -> None:
        # This guard avoids Tk crashes when workers try to update widgets during shutdown.
        if self._shutting_down:
            return
        try:
            fn(*args)
        except tk.TclError:
            pass

    def _safe_after(self, delay_ms: int, callback) -> Optional[str]:
        if self._shutting_down:
            return None
        try:
            return self.after(delay_ms, callback)
        except tk.TclError:
            return None

    def _cancel_after(self, after_id: Optional[str]) -> None:
        if not after_id:
            return
        try:
            self.after_cancel(after_id)
        except tk.TclError:
            pass

    # Menu bar
    def _build_menu(self) -> None:
        bar = tk.Menu(self)

        m_file = tk.Menu(bar, tearoff=False)
        m_file.add_command(label=self._tr("menu_exit"), command=self._on_exit, accelerator="Alt+F4")
        bar.add_cascade(label=self._tr("menu_file"), menu=m_file, underline=0)

        m_dev = tk.Menu(bar, tearoff=False)
        m_dev.add_command(label=self._tr("menu_refresh"), command=self._on_refresh, accelerator="F5")
        m_dev.add_separator()
        m_dev.add_command(label=self._tr("menu_install"), command=self._on_install, accelerator="Enter")
        bar.add_cascade(label=self._tr("menu_device"), menu=m_dev, underline=0)

        m_help = tk.Menu(bar, tearoff=False)
        m_help.add_command(label=self._tr("menu_about"), command=self._show_about, accelerator="F1")

        m_lang = tk.Menu(m_help, tearoff=False)
        m_lang.add_radiobutton(label=self.I18N[self._lang]["lang_es"], variable=self._lang_code_var, value="es", command=lambda: self._set_language("es"))
        m_lang.add_radiobutton(label=self.I18N[self._lang]["lang_en"], variable=self._lang_code_var, value="en", command=lambda: self._set_language("en"))
        m_help.add_cascade(label=self._tr("menu_language"), menu=m_lang)

        bar.add_cascade(label=self._tr("menu_help"), menu=m_help, underline=0)

        self.config(menu=bar)

    # Main UI content
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=14, style="Root.TFrame")
        root.pack(fill="both", expand=True)

        hero = ttk.Frame(root, padding=(18, 16), style="Hero.TFrame")
        hero.pack(fill="x", pady=(0, 12))
        hero.columnconfigure(0, weight=1)

        self._lbl_hero_title = ttk.Label(hero, text=self._tr("hero_title"), style="HeroTitle.TLabel")
        self._lbl_hero_title.grid(row=0, column=0, sticky="w")

        self._lbl_hero_subtitle = ttk.Label(hero, text=self._tr("hero_subtitle"), style="HeroSubtitle.TLabel")
        self._lbl_hero_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        ttk.Label(hero, text=backend.VERSION, style="VersionBadge.TLabel").grid(row=0, column=1, rowspan=2, sticky="e")

        self._lf_dev = ttk.LabelFrame(root, text=self._tr("section_device"), padding=10, style="Card.TLabelframe")
        self._lf_dev.pack(fill="x", pady=(0, 8))
        self._lf_dev.columnconfigure(0, weight=1)

        self._device_var = tk.StringVar()
        self._device_combo = ttk.Combobox(self._lf_dev, textvariable=self._device_var, state="readonly")
        self._device_combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._btn_refresh = ttk.Button(
            self._lf_dev,
            text=self._tr("btn_refresh"),
            command=self._on_refresh,
            width=18,
            style="Secondary.TButton",
        )
        self._btn_refresh.grid(row=0, column=1)

        self._lbl_device_hint = ttk.Label(self._lf_dev, text=self._tr("device_hint"), style="Hint.TLabel")
        self._lbl_device_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self._lf_ipa = ttk.LabelFrame(root, text=self._tr("section_ipa"), padding=10, style="Card.TLabelframe")
        self._lf_ipa.pack(fill="x", pady=(0, 8))
        self._lf_ipa.columnconfigure(0, weight=1)

        self._ipa_var = tk.StringVar()
        ttk.Entry(self._lf_ipa, textvariable=self._ipa_var).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._btn_browse = ttk.Button(
            self._lf_ipa,
            text=self._tr("btn_browse"),
            command=self._on_browse_ipa,
            width=12,
            style="Secondary.TButton",
        )
        self._btn_browse.grid(row=0, column=1)

        self._lbl_ipa_hint = ttk.Label(self._lf_ipa, text=self._tr("ipa_hint"), style="Hint.TLabel")
        self._lbl_ipa_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self._lf_aid = ttk.LabelFrame(root, text=self._tr("section_appleid"), padding=10, style="Card.TLabelframe")
        self._lf_aid.pack(fill="x", pady=(0, 8))
        self._lf_aid.columnconfigure(1, weight=1)

        self._lbl_email = ttk.Label(self._lf_aid, text=self._tr("label_email"))
        self._lbl_email.grid(row=0, column=0, sticky="w", padx=(0, 6))

        self._email_var = tk.StringVar()
        ttk.Entry(self._lf_aid, textvariable=self._email_var).grid(row=0, column=1, sticky="ew", pady=(0, 6))

        self._lbl_password = ttk.Label(self._lf_aid, text=self._tr("label_password"))
        self._lbl_password.grid(row=1, column=0, sticky="w", padx=(0, 6))

        self._pwd_var = tk.StringVar()
        pwd_row = ttk.Frame(self._lf_aid)
        pwd_row.grid(row=1, column=1, sticky="ew")
        pwd_row.columnconfigure(0, weight=1)

        self._pwd_entry = ttk.Entry(pwd_row, textvariable=self._pwd_var, show="*")
        self._pwd_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._show_pwd_var = tk.BooleanVar(value=False)
        self._chk_show_pwd = ttk.Checkbutton(
            pwd_row,
            text=self._tr("show_password"),
            variable=self._show_pwd_var,
            command=self._toggle_password,
        )
        self._chk_show_pwd.grid(row=0, column=1)

        self._lbl_appleid_hint = ttk.Label(self._lf_aid, text=self._tr("appleid_hint"), style="Hint.TLabel")
        self._lbl_appleid_hint.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self._lf_opt = ttk.LabelFrame(root, text=self._tr("section_options"), padding=10, style="Card.TLabelframe")
        self._lf_opt.pack(fill="x", pady=(0, 8))

        self._auto_start_var = tk.BooleanVar()
        self._chk_auto_start = ttk.Checkbutton(
            self._lf_opt,
            text=self._tr("opt_auto_start"),
            variable=self._auto_start_var,
            command=self._queue_save,
        )
        self._chk_auto_start.pack(anchor="w")

        ac_row = ttk.Frame(self._lf_opt)
        ac_row.pack(anchor="w", pady=(6, 0))

        self._auto_close_var = tk.BooleanVar()
        self._chk_auto_close = ttk.Checkbutton(
            ac_row,
            text=self._tr("opt_auto_close"),
            variable=self._auto_close_var,
            command=self._on_auto_close_toggle,
        )
        self._chk_auto_close.pack(side="left")

        self._close_sec_var = tk.IntVar(value=60)
        self._spin_close = ttk.Spinbox(ac_row, from_=5, to=3600, textvariable=self._close_sec_var, width=6, command=self._queue_save)
        self._spin_close.pack(side="left", padx=6)

        self._lbl_seconds = ttk.Label(ac_row, text=self._tr("seconds"))
        self._lbl_seconds.pack(side="left")

        self._lbl_opt_hint = ttk.Label(self._lf_opt, text=self._tr("opt_hint"), style="Hint.TLabel")
        self._lbl_opt_hint.pack(anchor="w", pady=(8, 0))

        self._lf_prog = ttk.LabelFrame(root, text=self._tr("section_progress"), padding=10, style="Card.TLabelframe")
        self._lf_prog.pack(fill="x", pady=(0, 8))
        self._lf_prog.columnconfigure(0, weight=1)

        self._progress_var = tk.IntVar(value=0)
        self._progress = ttk.Progressbar(self._lf_prog, variable=self._progress_var, maximum=100, mode="determinate")
        self._progress.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self._progress_text_var = tk.StringVar(value="0%")
        ttk.Label(self._lf_prog, textvariable=self._progress_text_var, style="ProgressText.TLabel").grid(row=0, column=1, sticky="e")

        self._lf_support = ttk.LabelFrame(root, text=self._tr("section_support"), padding=10, style="Card.TLabelframe")
        self._lf_support.pack(fill="x", pady=(0, 8))
        self._lf_support.columnconfigure(2, weight=1)

        self._btn_donate = ttk.Button(
            self._lf_support,
            text=self._tr("btn_donate"),
            command=self._on_donate,
            width=22,
            style="Secondary.TButton",
        )
        self._btn_donate.grid(row=0, column=0, padx=(0, 8), pady=(0, 6), sticky="w")

        self._lbl_language = ttk.Label(self._lf_support, text=self._tr("label_language"))
        self._lbl_language.grid(row=0, column=1, padx=(8, 6), pady=(0, 6), sticky="e")

        self._lang_display_var = tk.StringVar(value=self._lang_display(self._lang))
        self._combo_language = ttk.Combobox(
            self._lf_support,
            textvariable=self._lang_display_var,
            state="readonly",
            values=self._language_values(),
            width=18,
        )
        self._combo_language.grid(row=0, column=2, sticky="w", pady=(0, 6))
        self._combo_language.bind("<<ComboboxSelected>>", self._on_language_combo)

        self._lbl_support_hint = ttk.Label(self._lf_support, text=self._tr("support_hint"), style="Hint.TLabel")
        self._lbl_support_hint.grid(row=1, column=0, columnspan=3, sticky="w")

        btn_row = ttk.Frame(root)
        btn_row.pack(fill="x")

        self._btn_install = ttk.Button(
            btn_row,
            text=self._tr("btn_install"),
            command=self._on_install,
            width=22,
            style="Primary.TButton",
        )
        self._btn_install.pack(side="left", padx=(0, 8))

        self._btn_exit = ttk.Button(btn_row, text=self._tr("btn_exit"), command=self._on_exit, width=14, style="Secondary.TButton")
        self._btn_exit.pack(side="right")

    # Status bar
    def _build_status_bar(self) -> None:
        ttk.Separator(self, orient="horizontal").pack(fill="x", side="bottom")
        bar = ttk.Frame(self, relief="sunken")
        bar.pack(fill="x", side="bottom")

        self._status_var = tk.StringVar(value=self._tr("status_ready"))
        ttk.Label(bar, textvariable=self._status_var, anchor="w", padding=(6, 2), style="Status.TLabel").pack(
            side="left", fill="x", expand=True
        )

        self._countdown_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._countdown_var, anchor="e", padding=(0, 2, 8, 2), style="Status.TLabel").pack(
            side="right"
        )

    # Restore config and widget state
    def _restore_config(self) -> None:
        cfg = self._cfg
        x = max(0, int(cfg.get("window_x", 100)))
        y = max(0, int(cfg.get("window_y", 100)))
        w = max(660, int(cfg.get("window_width", 780)))
        h = max(620, int(cfg.get("window_height", 660)))
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._email_var.set(cfg.get("apple_id", ""))
        self._auto_start_var.set(bool(cfg.get("auto_start", False)))
        self._auto_close_var.set(bool(cfg.get("auto_close", False)))
        self._close_sec_var.set(int(cfg.get("auto_close_seconds", 60)))

        self._lang = self._normalize_lang(cfg.get("language", self._lang))
        self._lang_code_var.set(self._lang)
        self._lang_display_var.set(self._lang_display(self._lang))

        last = cfg.get("last_ipa_path", "")
        if last and Path(last).is_file():
            self._ipa_var.set(last)

        # Traces are registered after initial set to avoid writing config on startup.
        self._email_var.trace_add("write", lambda *_: self._queue_save())
        self._ipa_var.trace_add("write", lambda *_: self._queue_save())
        self._close_sec_var.trace_add("write", lambda *_: self._queue_save())
        self._cfg["version"] = backend.VERSION
        self._apply_translations()

    # Config persistence
    def _queue_save(self, *_) -> None:
        if self._shutting_down:
            return
        self._cancel_after(self._save_id)
        self._save_id = self._safe_after(400, self._flush_save)

    def _flush_save(self) -> None:
        self._save_id = None
        try:
            self._cfg.update(
                {
                    "window_x": self.winfo_x(),
                    "window_y": self.winfo_y(),
                    "window_width": self.winfo_width(),
                    "window_height": self.winfo_height(),
                    "auto_start": self._auto_start_var.get(),
                    "auto_close": self._auto_close_var.get(),
                    "auto_close_seconds": int(self._close_sec_var.get()),
                    "apple_id": self._email_var.get().strip(),
                    "language": self._lang,
                    # Password is intentionally not persisted for safety.
                    "last_ipa_path": self._ipa_var.get().strip(),
                    "last_ipa_dir": str(Path(self._ipa_var.get()).parent) if self._ipa_var.get() else self._cfg.get("last_ipa_dir", ""),
                }
            )
            backend.save_config(self._cfg)
        except Exception as exc:
            backend.logger.debug(f"_flush_save skipped: {exc}")

    # Keyboard shortcuts
    def _bind_shortcuts(self) -> None:
        self.bind("<Return>", lambda _e: self._on_install())
        self.bind("<Escape>", lambda _e: self._on_exit())
        self.bind("<F5>", lambda _e: self._on_refresh())
        self.bind("<F1>", lambda _e: self._show_about())

    # Runtime dependency bootstrap
    def _set_status(self, msg: str) -> None:
        self._ui_call(self._status_var.set, msg)

    def _bootstrap_dependencies(self) -> None:
        self._deps_busy = True
        self._set_status(self._tr("status_deps_validating"))

        def _task() -> None:
            ok, msg = backend.ensure_runtime_dependencies(self._set_status)

            def _done() -> None:
                self._deps_busy = False
                self._deps_ready = ok
                self._set_status(msg if not ok else self._tr("status_deps_ready"))

            self._safe_after(0, _done)

        threading.Thread(target=_task, daemon=True, name="deps-bootstrap").start()

    def _set_progress(self, pct: int) -> None:
        self._ui_call(self._progress_var.set, pct)
        self._ui_call(self._progress_text_var.set, f"{pct}%")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self._ui_call(self._btn_install.config, state=state)
        self._ui_call(self._btn_refresh.config, state=state)

    # Language change handlers
    def _on_language_combo(self, _event: tk.Event) -> None:
        display = self._lang_display_var.get().strip().lower()
        if display in (self._tr("lang_en").lower(), "english"):
            self._set_language("en")
        else:
            self._set_language("es")

    def _set_language(self, lang_code: str) -> None:
        lang_code = self._normalize_lang(lang_code)
        if lang_code == self._lang:
            return
        self._lang = lang_code
        self._lang_code_var.set(lang_code)
        self._lang_display_var.set(self._lang_display(lang_code))
        self._apply_translations()
        self._queue_save()

    def _apply_translations(self) -> None:
        # Refresh all static texts so language switch applies immediately.
        self.title(f"{backend.APP_NAME}   {backend.VERSION}")
        self._build_menu()

        self._lbl_hero_title.config(text=self._tr("hero_title"))
        self._lbl_hero_subtitle.config(text=self._tr("hero_subtitle"))

        self._lf_dev.config(text=self._tr("section_device"))
        self._btn_refresh.config(text=self._tr("btn_refresh"))
        self._lbl_device_hint.config(text=self._tr("device_hint"))

        self._lf_ipa.config(text=self._tr("section_ipa"))
        self._btn_browse.config(text=self._tr("btn_browse"))
        self._lbl_ipa_hint.config(text=self._tr("ipa_hint"))

        self._lf_aid.config(text=self._tr("section_appleid"))
        self._lbl_email.config(text=self._tr("label_email"))
        self._lbl_password.config(text=self._tr("label_password"))
        self._chk_show_pwd.config(text=self._tr("show_password"))
        self._lbl_appleid_hint.config(text=self._tr("appleid_hint"))

        self._lf_opt.config(text=self._tr("section_options"))
        self._chk_auto_start.config(text=self._tr("opt_auto_start"))
        self._chk_auto_close.config(text=self._tr("opt_auto_close"))
        self._lbl_seconds.config(text=self._tr("seconds"))
        self._lbl_opt_hint.config(text=self._tr("opt_hint"))

        self._lf_prog.config(text=self._tr("section_progress"))

        self._lf_support.config(text=self._tr("section_support"))
        self._btn_donate.config(text=self._tr("btn_donate"))
        self._lbl_language.config(text=self._tr("label_language"))
        self._combo_language.config(values=self._language_values())
        self._lbl_support_hint.config(text=self._tr("support_hint"))

        self._btn_install.config(text=self._tr("btn_install"))
        self._btn_exit.config(text=self._tr("btn_exit"))

        if not self._busy:
            self._status_var.set(self._tr("status_ready"))

        if self._countdown is not None:
            self._countdown_var.set(self._tr("status_auto_close", seconds=self._countdown))

    # Password show and hide
    def _toggle_password(self) -> None:
        self._pwd_entry.config(show="" if self._show_pwd_var.get() else "*")

    # Auto-close countdown
    def _start_countdown(self, seconds: int) -> None:
        self._countdown = max(1, seconds)
        self._cancel_after(self._countdown_id)
        self._cancel_after(self._auto_exit_id)
        self._tick()

    def _cancel_countdown(self) -> None:
        self._countdown = None
        self._cancel_after(self._countdown_id)
        self._cancel_after(self._auto_exit_id)
        self._countdown_id = None
        self._auto_exit_id = None
        self._countdown_var.set("")

    def _tick(self) -> None:
        if self._countdown is None or self._shutting_down:
            return

        if self._countdown <= 0:
            self._countdown_var.set(self._tr("status_closing"))
            self._auto_exit_id = self._safe_after(600, self._on_exit)
            return

        self._countdown_var.set(self._tr("status_auto_close", seconds=self._countdown))
        self._countdown -= 1
        self._countdown_id = self._safe_after(1000, self._tick)

    def _on_auto_close_toggle(self) -> None:
        self._queue_save()
        if self._auto_close_var.get():
            self._start_countdown(int(self._close_sec_var.get()))
        else:
            self._cancel_countdown()

    # Window geometry autosave
    def _on_configure(self, event: tk.Event) -> None:
        if event.widget is not self or self._shutting_down:
            return
        self._cancel_after(self._geo_id)
        self._geo_id = self._safe_after(500, self._queue_save)

    # About dialog
    def _show_about(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title(self._tr("about_title"))
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text=self._tr("about_body"), justify="center", padding=24).pack()
        ttk.Button(dlg, text=self._tr("btn_close"), command=dlg.destroy, width=12).pack(pady=(0, 16))
        dlg.bind("<Escape>", lambda _: dlg.destroy())
        dlg.bind("<Return>", lambda _: dlg.destroy())
        dlg.focus_set()

    # Donation button
    def _on_donate(self) -> None:
        self._set_status(self._tr("status_donate_opening"))
        try:
            webbrowser.open(self.DONATE_URL, new=2)
        except Exception as exc:
            self._set_status(self._tr("status_donate_error", err=exc))

    # Browse IPA file
    def _on_browse_ipa(self) -> None:
        init = self._cfg.get("last_ipa_dir", "") or str(Path.home())
        path = filedialog.askopenfilename(
            parent=self,
            title=self._tr("dlg_select_ipa"),
            initialdir=init,
            filetypes=[("iOS App Package", "*.ipa"), ("All files", "*.*")],
        )
        if path:
            self._ipa_var.set(path)

    # Refresh device list
    def _on_refresh(self) -> None:
        if self._deps_busy:
            self._set_status(self._tr("status_wait_deps"))
            return

        ready, message = backend.check_runtime_support()
        if not ready:
            self._devices = []
            self._device_combo["values"] = [self._tr("device_missing_value")]
            self._device_combo.current(0)
            self._set_status(message)
            self._btn_refresh.config(state="normal")
            return

        self._set_status(self._tr("status_searching"))
        self._btn_refresh.config(state="disabled")

        def _task() -> None:
            devices = backend.list_devices()
            self._safe_after(0, lambda: self._populate_devices(devices))

        threading.Thread(target=_task, daemon=True).start()

    def _populate_devices(self, devices: list[dict]) -> None:
        self._devices = devices
        self._btn_refresh.config(state="normal")
        if devices:
            labels = [f"{d['name']}  ({d['model']})  iOS {d['ios_version']}  [{d['udid'][:12]}...]" for d in devices]
            self._device_combo["values"] = labels
            self._device_combo.current(0)
            self._set_status(self._tr("status_devices_found", count=len(devices)))
        else:
            self._device_combo["values"] = [self._tr("device_empty_value")]
            self._device_combo.current(0)
            self._set_status(self._tr("status_no_devices"))

    # Auto-start workflow
    def _on_refresh_then_install(self) -> None:
        self._set_status(self._tr("status_auto_start"))

        def _task() -> None:
            devices = backend.list_devices()
            self._safe_after(0, lambda: self._populate_devices(devices))
            if devices:
                self._safe_after(0, self._on_install)

        threading.Thread(target=_task, daemon=True).start()

    # Install IPA
    def _on_install(self) -> None:
        if self._busy:
            return

        ipa = self._ipa_var.get().strip()
        if not ipa:
            self._set_status(self._tr("status_need_ipa"))
            return
        if not Path(ipa).is_file():
            self._set_status(self._tr("status_file_missing", ipa=ipa))
            return

        idx = self._device_combo.current()
        if idx < 0 or not self._devices:
            self._set_status(self._tr("status_no_device"))
            return

        udid = self._devices[idx]["udid"]
        self._set_busy(True)
        self._set_progress(0)
        self._set_status(self._tr("status_install_start", name=self._devices[idx]["name"]))

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

    # Exit with safe cancellation of pending callbacks
    def _on_exit(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True

        self._cancel_after(self._save_id)
        self._cancel_after(self._geo_id)
        self._cancel_countdown()

        # Persist latest state one last time before destroying widgets.
        self._flush_save()
        backend.logger.info(f"{backend.APP_NAME} closed by user")

        try:
            self.destroy()
        except tk.TclError:
            pass


# Entry point

def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
