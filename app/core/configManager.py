import os, sys, json
from pathlib import Path

def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta absoluta al recurso, compatible con PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):  # cuando está en un EXE
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Ruta al config.json (cuando está en modo desarrollo)
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

def load_config():
    """
    Carga el archivo de configuración.
    - En desarrollo: usa config.json junto al código.
    - En PyInstaller: usa el config.json empaquetado.
    """
    try:
        # Primero buscamos con resource_path (para EXE)
        path = resource_path("app/config.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Si no existe, usamos el path normal en desarrollo
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)

    except Exception as e:
        print(f"⚠️ Error cargando config.json: {e}")

    # Si no hay archivo, devolvemos un diccionario vacío
    return {"plc": {}, "scanner": {}, "images": {}, "ui": {}, "counters": {}}

def save_config(data: dict):
    """
    Guarda el archivo config.json (solo funciona en modo desarrollo,
    porque dentro del EXE no se puede escribir).
    """
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"⚠️ No se pudo guardar config.json: {e}")