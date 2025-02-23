import subprocess

# Проверьте путь к mmdc через "where.exe mmdc"
mmdc_path = r"C:\Users\IG\AppData\Roaming\npm\mmdc.cmd"

# Запускаем Mermaid CLI
subprocess.run([mmdc_path, "-i", r"diagram_generator\diagram.mmd", "-o", r"diagram_generator\diagram.svg"], shell=True)

git push amvera ux_no_button_gen:master
ux_no_button_gen
