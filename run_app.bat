@echo off
echo ================================================
echo   ContractGuardian - AI Contract Analysis
echo   Powered by IBM WatsonX Orchestrate
echo ================================================
echo.
echo Starting application...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run Streamlit app (using python -m to avoid PATH issues)
python -m streamlit run app.py

pause
