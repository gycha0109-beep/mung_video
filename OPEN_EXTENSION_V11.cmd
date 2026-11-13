@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v11_extension\VIEW_ALL_50M_V11.html"
if not exist "%PAGE%" (echo V11 viewer not ready.&pause&exit /b 1)
start "" "%PAGE%"
