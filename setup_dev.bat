@echo off
echo Activating virtual environment...
call .\.venv\Scripts\activate

echo Installing development packages...
pip install jupyterlab ipykernel seaborn plotly requests statsmodels PyYAML

echo.
echo ✅ Dev environment setup complete.
pause
