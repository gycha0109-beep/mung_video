$ErrorActionPreference='Continue'
$root='C:\Users\hun\Documents\mung_video'
$exe='C:\Users\hun\Documents\BlenderPortable\blender-5.2.3-windows-x64\blender.exe'
$out=Join-Path $root 'cinematic_50m_v12_steel'
New-Item -ItemType Directory -Path $out -Force | Out-Null
& $exe --background --threads 6 --python (Join-Path $root 'render_v12_steel_preview.py') *> (Join-Path $out 'render.log')
$renderExit=$LASTEXITCODE
$renderExit | Set-Content (Join-Path $out 'render.exit')
if ($renderExit -eq 0 -and (Test-Path (Join-Path $out 'STEEL_V12_FRAME_094.png'))) {
  & python (Join-Path $root 'build_v12_steel_comparison.py') *> (Join-Path $out 'compare.log')
  if ($LASTEXITCODE -eq 0){'SUCCESS' | Set-Content (Join-Path $out 'render.state')}
  else {'COMPARE_FAILED' | Set-Content (Join-Path $out 'render.state')}
} else {
  'RENDER_FAILED' | Set-Content (Join-Path $out 'render.state')
}
