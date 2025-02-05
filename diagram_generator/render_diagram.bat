@echo off
cd %~dp0
npx -p @mermaid-js/mermaid-cli mmdc -i "%~dp0diagram_generator\diagram.mmd" -o "%~dp0diagram_generator\diagram.svg"
pause
