from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
s=(r/"render_50m_v9t_egg_launch.py").read_text(encoding="utf-8")
s=s.replace('OUT=R/"cinematic_50m_v9t_egg"','OUT=R/"cinematic_50m_v9t_diagnostic"')
s=s.replace("sc.render.use_motion_blur=True","sc.render.use_motion_blur=False")
s=s.replace("cam.data.dof.use_dof=True","cam.data.dof.use_dof=False")
s=s.replace("frames=[1,22,43,48,49,51,55,60,66,74,82,86,87,92,96]","frames=[1,43,55,74]")
s=s.replace('V9T_EGG_LAUNCH_{f:03d}.png','DIAG_{f:03d}.png')
(r/"render_v9t_diagnostic.py").write_text(s,encoding="utf-8")
print("DIAGNOSTIC_SCRIPT_READY")
