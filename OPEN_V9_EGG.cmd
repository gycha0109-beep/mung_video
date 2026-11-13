@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v9_egg\VIEW_EGG_V8_VS_V9.html"
if not exist "%PAGE%" (echo V9 review HTML not found.&pause&exit /b 1)
start "" "%PAGE%"
