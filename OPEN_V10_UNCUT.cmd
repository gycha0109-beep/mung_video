@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v10_egg\VIEW_EGG_V9T_VS_V10.html"
if not exist "%PAGE%" (echo V10 comparison page is not ready.&pause&exit /b 1)
start "" "%PAGE%"
