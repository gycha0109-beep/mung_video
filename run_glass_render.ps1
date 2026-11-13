param([ValidateSet('preview','full')][string]$Mode='preview')
$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v1'
$exe='C:\Users\hun\Documents\BlenderPortable\blender-5.2.3-windows-x64\blender.exe'
& $exe --background --threads 6 --python-exit-code 13 --python (Join-Path $root 'render_glass_challenge_v1.py') -- $Mode *> (Join-Path $out ("render_"+$Mode+".log"))
$code=$LASTEXITCODE
$code | Set-Content (Join-Path $out ("render_"+$Mode+".exit"))
