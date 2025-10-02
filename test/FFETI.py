import subprocess

def verify_serial(serial: str):
    result = subprocess.run(
        ["./ffeticlient.exe", "-VERIFY", serial],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Verificación completada")
        print("Salida:", result.stdout.strip())
    else:
        print("⚠️ Error en verificación")
        print("STDOUT:", result.stdout.strip())
        print("STDERR:", result.stderr.strip())

# Ejemplo de uso
verify_serial("GLBFLG254000411")