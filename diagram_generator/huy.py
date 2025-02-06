import subprocess

# Проверьте путь к mmdc через "where.exe mmdc"
mmdc_path = r"C:\Users\IG\AppData\Roaming\npm\mmdc.cmd"

# Запускаем Mermaid CLI
subprocess.run([mmdc_path, "-i", "diagram_generator\diagram.mmd", "-o", "diagram_generator\diagram.svg"], shell=True)
