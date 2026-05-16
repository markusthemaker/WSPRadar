@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0WSPRadar-AB-Relay-Switch.ps1" %*

