param([ValidateSet("preview","full")][string]$Mode="preview")
$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v7'
$exe='C:\Users\hun\Documents\BlenderPortable\blender-5.2.3-windows-x64\blender.exe'
& $exe --background --threads 6 --python-exit-code 13 --python (Join-Path $root 'render_glass_v7.py') -- $Mode *> (Join-Path $out ("render_"+$Mode+".log"))
$LASTEXITCODE | Set-Content (Join-Path $out ("render_"+$Mode+".exit"))
