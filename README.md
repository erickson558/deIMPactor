# deIMPactor

deIMPactor es una aplicación de escritorio en Python para Windows orientada a instalar archivos `.ipa` en dispositivos iOS conectados por USB, manteniendo la interfaz responsive, configuración persistente y compilación sin consola visible.

## Versión

Versión actual: `V0.0.4`

## Características

- GUI en Tkinter separada del backend
- Instalación de `.ipa` sin congelar la interfaz
- Configuración persistente en `config.json`
- Registro técnico en `log.txt` con timestamp
- Auto inicio opcional del proceso
- Auto cierre configurable con cuenta regresiva en barra de estado
- Recordatorio de posición y tamaño de la ventana
- Menú de aplicación con accesos rápidos estilo Windows
- Compilación a `.exe` usando icono `.ico`
- Sin ventana de consola al ejecutar el `.exe`
- Auto-instalación silenciosa de dependencias faltantes al iniciar

## Estructura

- `main.py`: interfaz gráfica
- `backend.py`: lógica de negocio, logging, configuración, instalación IPA
- `config.json`: parámetros persistentes de la GUI
- `requirements.txt`: dependencias Python
- `ios_os_logo_icon_134676.ico`: icono usado en la aplicación y compilación

## Requisitos

- Windows
- Python 3.12 o superior
- Drivers de Apple instalados en el equipo
  - Recomendado: instalar iTunes o Apple Mobile Device Support
- Dispositivo iOS confiando en el PC por USB

## Instalación local

```powershell
python -m pip install -r requirements.txt
python .\main.py
```

## Compilación

```powershell
.\build.ps1
```

## Versionado

Se sigue un versionado incremental por commit:

- `V0.0.1`: base inicial compilable
- `V0.0.2`: corrección del menú, mejora visual de la GUI y preparación del repositorio
- `V0.0.3`: corrección de detección del entorno Python y empaquetado confiable de `pymobiledevice3`
- `V0.0.4`: bootstrap de dependencias al inicio para mejorar portabilidad entre equipos

Cada commit debe:

- incrementar la versión en el código
- mantener la misma versión en `config.json`
- usar el mismo tag en git y release de GitHub

## Seguridad

- La contraseña no se guarda en `config.json`
- La escritura del archivo de configuración se realiza de forma atómica
- La UI no usa `messagebox` para flujos normales de operación
- El ejecutable se genera en modo ventana para evitar consola visible

## Licencia

Apache License 2.0. Ver `LICENSE`.
