@echo off
cd /d "%~dp0"
chcp 65001 > nul

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [오류] 가상환경 .venv 를 찾을 수 없습니다.
    echo 프로젝트 루트에서 다음 명령으로 먼저 가상환경을 만들어 주세요:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -e .
    echo.
    pause
    exit /b 1
)

echo 텔레그램 봇을 시작합니다...
echo.

".venv\Scripts\python.exe" -m markdown_creat.telegram_bot

echo.
echo 봇 프로세스가 종료되었습니다. 아무 키나 누르면 이 창이 닫힙니다.
pause
