"""
backend.py — Core logic for deIMPactor iOS IPA Sideloader.

Handles: configuration persistence, structured logging, and iOS
device operations (device discovery + IPA installation via USB).

Author : Synyster Rick
Version: V0.0.4
License: Apache License 2.0 — Copyright 2026, All rights reserved.
"""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import logging
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# ── Application metadata ──────────────────────────────────────────────────────
VERSION_NUMBER = "0.0.4"
VERSION        = f"V{VERSION_NUMBER}"
APP_NAME       = "deIMPactor"
AUTHOR         = "Synyster Rick"
YEAR           = str(datetime.now().year)

# Windows flag: suppress cmd windows in any subprocess call
CREATE_NO_WINDOW: int = 0x08000000 if sys.platform == "win32" else 0

# ── File names ────────────────────────────────────────────────────────────────
_CONFIG_FILE = "config.json"
_LOG_FILE    = "log.txt"
_REQUIRED_MODULES = ("pymobiledevice3",)

DEFAULT_CONFIG: dict = {
    "version":            VERSION,
    "window_x":           100,
    "window_y":           100,
    "window_width":       780,
    "window_height":      660,
    "auto_start":         False,
    "auto_close":         False,
    "auto_close_seconds": 60,
    "apple_id":           "",
    "last_ipa_dir":       "",
    "last_ipa_path":      "",
}


# ── Paths ─────────────────────────────────────────────────────────────────────
def get_base_path() -> Path:
    """Return the directory containing the running .exe or .py."""
    if getattr(sys, "frozen", False):       # PyInstaller bundle
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def config_path() -> Path:
    return get_base_path() / _CONFIG_FILE


def log_path() -> Path:
    return get_base_path() / _LOG_FILE


# ── Logging ───────────────────────────────────────────────────────────────────
def _setup_logger() -> logging.Logger:
    fmt  = "%(asctime)s  [%(levelname)-8s]  %(message)s"
    dfmt = "%Y-%m-%d %H:%M:%S"
    log  = logging.getLogger(APP_NAME)
    if log.handlers:                        # already initialised
        return log
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path(), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(fmt, dfmt))
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter(fmt, dfmt))
    log.addHandler(fh)
    log.addHandler(sh)
    log.propagate = False
    return log


logger: logging.Logger = _setup_logger()
logger.info("=" * 60)
logger.info(
    f"{APP_NAME} {VERSION}  •  iniciado "
    f"{datetime.now():%Y-%m-%d %H:%M:%S}"
)


def check_runtime_support() -> tuple[bool, str]:
    """Validate whether the active interpreter can talk to iOS devices."""
    missing = [name for name in _REQUIRED_MODULES if importlib.util.find_spec(name) is None]
    if missing:
        return (False, f"Dependencias faltantes: {', '.join(missing)}")

    return (True, "Entorno listo para detectar dispositivos iOS por USB.")


def ensure_runtime_dependencies(
    on_status: Optional[Callable[[str], None]] = None,
) -> tuple[bool, str]:
    """Try to install missing runtime dependencies for the active interpreter."""
    def _status(msg: str) -> None:
        logger.info(msg)
        if on_status:
            on_status(msg)

    missing = [name for name in _REQUIRED_MODULES if importlib.util.find_spec(name) is None]
    if not missing:
        return (True, "Dependencias OK")

    if getattr(sys, "frozen", False):
        msg = (
            "El ejecutable no incluye dependencias requeridas. "
            "Recompile la app con el build actual."
        )
        logger.error(msg)
        return (False, msg)

    _status("Faltan dependencias, instalando en segundo plano...")
    req_file = get_base_path() / "requirements.txt"
    if req_file.is_file():
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-input",
            "-r",
            str(req_file),
        ]
    else:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-input",
            *missing,
        ]

    try:
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
            creationflags=CREATE_NO_WINDOW,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "Error desconocido de pip").strip()
            msg = f"No se pudieron instalar dependencias: {err.splitlines()[-1]}"
            logger.error(msg)
            return (False, msg)
    except Exception as exc:
        msg = f"Fallo instalando dependencias: {exc}"
        logger.exception(msg)
        return (False, msg)

    remaining = [name for name in _REQUIRED_MODULES if importlib.util.find_spec(name) is None]
    if remaining:
        msg = f"Dependencias aún faltantes tras instalar: {', '.join(remaining)}"
        logger.error(msg)
        return (False, msg)

    msg = "Dependencias instaladas correctamente"
    _status(msg)
    return (True, msg)


# ── Configuration ─────────────────────────────────────────────────────────────
def load_config() -> dict:
    """Load config.json; merge with defaults for any missing keys."""
    cfg  = DEFAULT_CONFIG.copy()
    path = config_path()
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as fh:
                stored = json.load(fh)
            if not isinstance(stored, dict):
                raise ValueError("El archivo de configuración debe ser un objeto JSON")
            cfg.update(stored)
            logger.info(f"Configuración cargada desde {path}")
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            logger.warning(f"Error leyendo config: {exc} — usando valores por defecto")
    else:
        logger.info("No se encontró config.json — usando valores por defecto")
    return cfg


def save_config(cfg: dict) -> None:
    """Write configuration to config.json atomically (via temp file)."""
    path = config_path()
    try:
        cfg["version"] = VERSION
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=4, ensure_ascii=False)
        tmp.replace(path)                   # atomic rename
        logger.debug(f"Config guardada → {path}")
    except OSError as exc:
        logger.error(f"No se pudo guardar la configuración: {exc}")


# ── iOS Device Helpers ────────────────────────────────────────────────────────
def _resolve_maybe_awaitable(value: Any) -> Any:
    """Resolve plain values and awaitables using a private event loop when needed."""
    if not inspect.isawaitable(value):
        return value

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(value)
    finally:
        loop.close()


def _make_lockdown(udid: str) -> Any:
    """
    Create a LockdownClient for *udid*.
    Tries the v4+ API first, falls back to the legacy constructor.
    """
    try:
        from pymobiledevice3.lockdown import create_using_usbmux
        return _resolve_maybe_awaitable(create_using_usbmux(serial=udid))
    except (ImportError, TypeError):
        import pymobiledevice3.lockdown as lockdown_module

        lockdown_ctor = getattr(lockdown_module, "LockdownClient", None)
        if lockdown_ctor is None:
            raise RuntimeError("No se pudo crear el cliente Lockdown")

        try:
            return lockdown_ctor(udid=udid)
        except TypeError:
            return lockdown_ctor(udid)


# ── iOS Device Operations ─────────────────────────────────────────────────────
def list_devices() -> list[dict]:
    """
    Return a list of dicts describing each USB-connected iOS device.

    Each dict contains: udid, name, ios_version, model.
    Returns an empty list when no device is found or when
    pymobiledevice3 is unavailable.
    """
    result: list[dict] = []
    try:
        from pymobiledevice3.usbmux import list_devices as _list_usb
        devices = _resolve_maybe_awaitable(_list_usb())
        for dev in devices:
            udid = getattr(dev, "serial", str(dev))
            info: dict = {
                "udid":        udid,
                "name":        "Desconocido",
                "ios_version": "?",
                "model":       "?",
            }
            try:
                lk = _make_lockdown(udid)
                info.update({
                    "name":        getattr(lk, "display_name",    udid),
                    "ios_version": getattr(lk, "product_version", "?"),
                    "model":       getattr(lk, "product_type",    "?"),
                })
                logger.info(
                    f"  Dispositivo: {info['name']}  ({info['model']})  "
                    f"iOS {info['ios_version']}  [{udid[:12]}…]"
                )
            except Exception as exc:
                logger.warning(f"  No se pudo obtener info de {udid[:12]}: {exc}")
            result.append(info)

    except ImportError:
        logger.error(
            "pymobiledevice3 no está instalado.\n"
            "Ejecuta:  pip install pymobiledevice3"
        )
    except Exception as exc:
        logger.error(f"list_devices error: {exc}")

    return result


def install_ipa(
    udid:        str,
    ipa_path:    str,
    on_progress: Optional[Callable[[int], None]] = None,
    on_status:   Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Synchronously install *ipa_path* on the device identified by *udid*.

    Must be called from a background thread to keep the UI responsive.
    Returns True on success, False on failure.
    """
    def _status(msg: str) -> None:
        logger.info(msg)
        if on_status:
            on_status(msg)

    name = Path(ipa_path).name
    try:
        _status(f"Conectando al dispositivo {udid[:12]}…")
        lk = _make_lockdown(udid)
        dev_name = getattr(lk, "display_name",    udid)
        ios_ver  = getattr(lk, "product_version", "?")
        _status(f"Conectado → {dev_name}  (iOS {ios_ver})")

        from pymobiledevice3.services.installation_proxy import (
            InstallationProxyService,
        )
        svc = InstallationProxyService(lockdown=lk)
        _status(f"Instalando {name}…")

        def _progress(info: dict) -> None:
            pct = int(info.get("PercentComplete", 0))
            msg = info.get("Status", "")
            if on_progress:
                on_progress(pct)
            if msg:
                _status(f"[{pct:3d}%] {msg}")

        install_method = getattr(svc, "install_from_local_file", None)
        if callable(install_method):
            _resolve_maybe_awaitable(install_method(ipa_path, callback=_progress))
        else:
            fallback_install = getattr(svc, "install", None)
            if not callable(fallback_install):
                raise RuntimeError(
                    "La versión instalada de pymobiledevice3 no expone un método de instalación compatible"
                )
            _resolve_maybe_awaitable(fallback_install(ipa_path, callback=_progress))

        _status(f"✔  {name} instalada correctamente!")
        logger.info(f"IPA instalada: {ipa_path!r} → dispositivo {udid}")
        return True

    except ImportError as exc:
        _status(f"Dependencia faltante: {exc}")
        return False
    except Exception as exc:
        _status(f"Instalación fallida: {exc}")
        logger.exception(f"install_ipa({udid!r}, {ipa_path!r})")
        return False


def install_ipa_threaded(
    udid:        str,
    ipa_path:    str,
    on_progress: Optional[Callable[[int], None]] = None,
    on_status:   Optional[Callable[[str], None]] = None,
    on_done:     Optional[Callable[[bool], None]] = None,
) -> threading.Thread:
    """
    Run :func:`install_ipa` in a daemon thread.

    *on_done* is called with ``True`` on success or ``False`` on failure.
    Returns the running :class:`threading.Thread`.
    """
    def _run() -> None:
        success = install_ipa(udid, ipa_path, on_progress, on_status)
        if on_done:
            on_done(success)

    thread = threading.Thread(target=_run, daemon=True, name="ipa-installer")
    thread.start()
    logger.debug(f"Thread de instalación iniciado: {thread.name}")
    return thread
