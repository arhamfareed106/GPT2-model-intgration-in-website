@echo off
set PYTHONPATH=%cd%\src
echo Running tests with PYTHONPATH=%PYTHONPATH%
pytest -q --disable-warnings