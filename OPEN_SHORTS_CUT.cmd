@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v9s_egg\VIEW_EGG_V9_VS_SHORTS.html"
if not exist "%PAGE%" (echo The comparison video is not ready.&pause&exit /b 1)
start "" "%PAGE%"
