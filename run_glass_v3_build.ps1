$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v3'
$exe='C:\Users\hun\Documents\BlenderPortable\blender-5.2.3-windows-x64\blender.exe'
& $exe --background --threads 6 --python-exit-code 13 --python (Join-Path $root 'build_glass_challenge_v3.py') *> (Join-Path $out 'build.log')
$LASTEXITCODE|Set-Content (Join-Path $out 'build.exit')
