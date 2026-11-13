@echo off
setlocal
set "PAGE=%~dp0cinematic_50m_v9t_egg\VIEW_EGG_SHORTS_VS_TRACKLOCK.html"
if not exist "%PAGE%" (echo Comparison page not yet generated.&pause&exit /b 1)
start "" "%PAGE%"
