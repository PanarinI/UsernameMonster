import subprocess

# Проверьте путь к mmdc через "where.exe mmdc"
mmdc_path = r"C:\Users\ВашПользователь\AppData\Roaming\npm\mmdc.cmd"

# Запускаем Mermaid CLI
subprocess.run([mmdc_path, "-i", "diagram.mmd", "-o", "diagram.svg"], shell=True)
