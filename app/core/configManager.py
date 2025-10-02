import os, sys, json
from pathlib import Path

def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta absoluta al recurso, compatible con PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):  # cuando está en un EXE
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Ruta preferida para guardar config.json (externo editable)
CONFIG_PATH = Path(os.getcwd()) / "config.json"

# Ruta al config por defecto (empaquetado con PyInstaller)
DEFAULT_CONFIG_PATH = resource_path("config.json")


def load_config():
    """
    Carga el archivo de configuración.
    - Si existe un config.json externo => lo carga.
    - Si no, intenta cargar el empaquetado (solo lectura).
    - Si no hay nada, devuelve estructura vacía.
    """
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)

        if os.path.exists(DEFAULT_CONFIG_PATH):
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)

    except Exception as e:
        print(f"⚠️ Error cargando config.json: {e}")

    return {"plc": {}, "scanner": {}, "images": {}, "ui": {}, "counters": {}}


def save_config(data: dict):
    """
    Guarda SIEMPRE en el config externo (junto al .exe o cwd).
    Así se conservan cambios aunque la app esté empaquetada.
    """
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"💾 Config guardado en {CONFIG_PATH}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar config.json: {e}")