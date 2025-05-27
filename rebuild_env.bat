@echo off
echo Deleting old environment...
rmdir /s /q .venv

echo Creating new virtual environment...
python -m venv .venv
call .\.venv\Scripts\activate

echo Upgrading pip...
pip install --upgrade pip

echo Installing production packages...
pip install -r requirements.txt

echo Installing development tools...
pip install -r requirements-dev.txt

echo.
echo ✅ Full environment rebuild complete.
pause
