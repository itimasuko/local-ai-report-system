@echo off
echo ==========================================
echo  AI Report System Starting...
echo ==========================================
echo.

REM Docker起動確認
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running.
    echo Please start Docker Desktop first.
    pause
    exit /b
)

REM コンテナ起動
docker-compose up -d --build

echo.
echo ==========================================
echo  System Started Successfully!
echo ==========================================
echo  Admin: http://localhost:8501
echo  User : http://localhost:8502
echo.
pause