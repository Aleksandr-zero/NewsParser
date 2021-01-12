@echo off
if "%~1"=="" (set "x=%~f0"& start "" /min "%comspec%" /v/c "!x!" any_word & exit /b)
python rem ваш путь к проекту