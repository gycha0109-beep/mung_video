from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
src=r/"render_50m_v9_egg_launch.py"
dest=r/"render_50m_v9s_egg_launch.py"
s=src.read_text(encoding="utf-8")
s=s.replace('OUT=R/"cinematic_50m_v9_egg"','OUT=R/"cinematic_50m_v9s_egg"')
start=s.index("# Shot 1: high-tension")
end=s.index("# Preserve linear world-space trajectory.")
new='''# Shorts style: two simple perspectives; no theatrical camera orbit or optical zoom.
# 1-54: one locked camera witnesses the tension, snap and initial acceleration.
cam_pose(1,(.30,-51.95,2.02),(0,-49.50,1.75),38)
cam_pose(54,(.30,-51.95,2.02),(0,-49.50,1.75),38)
# 55-96: a single continuous straightforward rear flight camera; fixed lens.
# One normal cut at frame 55 (2.25s). The next cut is the physical impact at 4.0s.
for f in range(55,97):
 y,z=ball_at(f)
 t=(f-55)/41.0
 trail=2.0+5.8*t
 cam_pose(f,(.60,y-trail,1.89),(0,y+1.0,z-.04),35)
# Frame 54 is a hard cut boundary, not a zoom / interpolation sequence.
'''
s=s[:start]+new+s[end:]
s=s.replace('kp.co.x in (58,85)','kp.co.x in (54,)')
s=s.replace('"V9_50M_ACTUAL_DISTANCE"','"V9S_50M_ACTUAL_DISTANCE"')
s=s.replace('"EGG_50M_V9_SPEED_AND_SURFACE.blend"','"EGG_50M_V9S_SIMPLE_SHORTS.blend"')
s=s.replace('"V9_ASSET_READY"','"V9S_ASSET_READY"')
s=s.replace('"V9_EGG_LAUNCH_{f:03d}.png"','"V9S_EGG_LAUNCH_{f:03d}.png"')
s=s.replace('"V9_LAUNCH_PREVIEW"','"V9S_LAUNCH_PREVIEW"')
s=s.replace('"V9_LAUNCH_FULL"','"V9S_LAUNCH_FULL"')
s=s.replace('frames=[43,48,49,50,51,52,56,60,66,74,82,85,86,90,94,96]', 'frames=[1,22,43,48,49,51,54,55,60,66,74,82,88,94,96]')
assert 'cam_pose(54,' in s and "frames=[1,22" in s
dest.write_text(s,encoding="utf-8")
print("SHORTCUT_SCRIPT_READY",dest)
