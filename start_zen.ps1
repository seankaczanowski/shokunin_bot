# start_zen.ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

cd C:\Users\sean\zen_trader_bot
.venv\Scripts\Activate

& "$PSScriptRoot\.venv\Scripts\jupyter.exe" notebook

