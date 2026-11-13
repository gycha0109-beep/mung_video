$root='C:\Users\hun\Documents\mung_video'
$out=Join-Path $root 'glass_panel_challenge_v2'
$renderExit=Join-Path $out 'render_full.exit'
for($i=0;$i -lt 160;$i++){
  if(Test-Path $renderExit){break}
  Start-Sleep -Seconds 5
}
if(-not(Test-Path $renderExit)){'RENDER_TIMEOUT'|Set-Content (Join-Path $out 'finish.state');exit 1}
$rc=(Get-Content $renderExit -Raw).Trim()
if($rc -ne '0'){'RENDER_FAILED'|Set-Content (Join-Path $out 'finish.state');exit 2}
$n=(Get-ChildItem (Join-Path $out 'frames') -Filter 'frame_*.png' -File|Measure-Object).Count
if($n -ne 192){"MISSING_FRAMES_$n"|Set-Content (Join-Path $out 'finish.state');exit 3}
& python (Join-Path $root 'assemble_glass_challenge_v2.py') *> (Join-Path $out 'assemble.log')
$ac=$LASTEXITCODE
$ac|Set-Content (Join-Path $out 'assemble.exit')
if($ac -ne 0){'ASSEMBLY_FAILED'|Set-Content (Join-Path $out 'finish.state');exit 4}
'SUCCESS'|Set-Content (Join-Path $out 'finish.state')
