@echo off
echo Setting up Complete Agentic Frontend...
echo.

REM Install Tailwind CSS
echo Installing Tailwind CSS...
call npm install -D tailwindcss postcss autoprefixer

REM Install missing dependencies
echo Installing dependencies...
call npm install

echo.
echo Setup complete! You can now run:
echo npm run dev
echo.
pause