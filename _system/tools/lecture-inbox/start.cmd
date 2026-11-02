@echo off
setlocal
set "UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\lecture-inbox\venv"
uv run --locked --project "%~dp0." python "%~dp0app.py" %*
