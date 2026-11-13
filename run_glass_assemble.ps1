$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v1'
& python (Join-Path $root 'assemble_glass_challenge_v1.py') *> (Join-Path $out 'assemble.log')
$code=$LASTEXITCODE
$code | Set-Content (Join-Path $out 'assemble.exit')
