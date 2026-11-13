from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
src=r/"render_50m_v9s_egg_launch.py"
s=src.read_text(encoding="utf-8")
s=s.replace('OUT=R/"cinematic_50m_v9s_egg"','OUT=R/"cinematic_50m_v9t_egg"')
s=s.replace('sc.render.motion_blur_shutter=.37','sc.render.motion_blur_shutter=.64')
where='bands={side:bpy.data.objects["TENSIONED LATEX / "+side] for side in ("LEFT","RIGHT")}\n'
assert where in s
s=s.replace(where,where+'''# Focus stays on the moving projectile. Background moves and blurs, egg remains sharp.
cam.data.dof.use_dof=True
cam.data.dof.focus_object=ball
cam.data.dof.aperture_fstop=1.65
cam.data.dof.aperture_blades=6
''')
start=s.index('# Shorts style: two simple perspectives')
end=s.index('# Preserve linear world-space trajectory.')
new='''# Camera fixed RELATIVE TO the egg until 10m remain (through frame 86).
# No changes of angle, focal length, or shot during the first 40m.
for f in range(1,87):
 y,z=ball_at(f)
 cam_pose(f,(.36,y-2.48,z+.26),(0,y+.02,z),37)
# Only the last 10m is photographed from a fixed sideline camera.
# One direct cut after frame 86; lens and camera position then remain fixed.
for f in range(87,97):
 cam_pose(f,(2.30,-8.30,1.84),(0,-1.0,1.33),35)
# Hold DOF wide for the prelaunch, shallow during high-speed travel, then reset.
for f,stop in [(1,5.6),(48,5.6),(49,2.4),(55,1.65),(86,1.65),(87,4.8),(96,4.8)]:
 cam.data.dof.aperture_fstop=stop
 cam.data.dof.keyframe_insert(data_path="aperture_fstop",frame=f)
# Camera release is not a third shot; it is just the final 10m viewpoint.
'''
s=s[:start]+new+s[end:]
s=s.replace('kp.co.x in (54,)','kp.co.x in (86,)')
repl={
 'V9S_50M_ACTUAL_DISTANCE':'V9T_50M_ACTUAL_DISTANCE',
 'EGG_50M_V9S_SIMPLE_SHORTS.blend':'EGG_50M_V9T_TRACKLOCK.blend',
 'V9S_ASSET_READY':'V9T_ASSET_READY',
 'V9S_EGG_LAUNCH_{f:03d}.png':'V9T_EGG_LAUNCH_{f:03d}.png',
 'V9S_LAUNCH_PREVIEW':'V9T_LAUNCH_PREVIEW',
 'V9S_LAUNCH_FULL':'V9T_LAUNCH_FULL',
 'frames=[1,22,43,48,49,51,54,55,60,66,74,82,88,94,96]':'frames=[1,22,43,48,49,51,55,60,66,74,82,86,87,92,96]'
}
for a,b in repl.items():
 assert a in s,a
 s=s.replace(a,b)
dst=r/"render_50m_v9t_egg_launch.py"
dst.write_text(s,encoding="utf-8")
compile(s,str(dst),"exec")
print("V9T_TRACK_SCRIPT_READY",dst)
