$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v4'
& python (Join-Path $root 'assemble_glass_challenge_v4.py') *> (Join-Path $out 'assemble.log')
$LASTEXITCODE | Set-Content (Join-Path $out 'assemble.exit')
