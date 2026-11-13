@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v8\final\VIEW_50M_V8.html"
if not exist "%PAGE%" (
  echo 50m V8 comparison HTML has not been generated yet.
  pause
  exit /b 1
)
start "" "%PAGE%"
