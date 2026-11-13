from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
p=r/"render_extension_v11.py"
s=p.read_text(encoding="utf-8")
assert 'projectile.scale=(.36,.36,.36)' in s
s=s.replace('projectile.scale=(.36,.36,.36)','projectile.scale=(.20,.20,.20)')
old='# Camera follows the V10 shot without changes: last follow-frame 91 at about 5.5m.'
assert old in s
insert='''# Cannon start: look past the carriage and smoothly join V10 projectile tracking.
if kind=="cannon":
 positions={};rotations={}
 for f in range(1,193):
  s.frame_set(f)
  positions[f]=camera.location.copy()
  rotations[f]=camera.rotation_euler.copy()
 camera.animation_data_clear()
 for f in range(1,193):
  if f<=48:
   y,z=pkeys[f].y,pkeys[f].z
   loc=Vector((1.47,y-4.15,z+.81))
   target=Vector((0,y+1.9,z-.13))
   rot=(target-loc).to_track_quat("-Z","Y").to_euler()
  elif f<63:
   t=(f-48)/15.
   y,z=pkeys[f].y,pkeys[f].z
   side=Vector((1.47,y-4.15,z+.81))
   target=Vector((0,y+1.9,z-.13))
   loc=side.lerp(positions[f],t)
   rot=(target-loc).to_track_quat("-Z","Y").to_euler()
   rot=rot.to_quaternion().slerp(rotations[f].to_quaternion(),t).to_euler()
  else:
   loc=positions[f];rot=rotations[f]
  camera.location=loc
  camera.rotation_euler=rot
  camera.keyframe_insert("location",frame=f)
  camera.keyframe_insert("rotation_euler",frame=f)
 glow=bpy.data.materials.new("V11 cannon muzzle orange glow")
 glow.use_nodes=True
 g=glow.node_tree.nodes.get("Principled BSDF")
 g.inputs["Base Color"].default_value=(1.0,.23,.015,1)
 g.inputs["Emission Color"].default_value=(1.0,.17,.015,1)
 g.inputs["Emission Strength"].default_value=14
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1)
 fx=bpy.context.object
 fx.name="V11 muzzle ignition flash"
 fx.data.materials.append(glow)
 for f,a in ((1,.001),(48,.001),(49,.48),(50,.66),(51,.34),(53,.001),(192,.001)):
  keypose(fx,f,(0,-50.84,1.53),scale=(a,a*.67,a))
'''
s=s.replace(old,insert+old)
p.write_text(s,encoding="utf8")
compile(s,str(p),"exec")
print("EXTENSION_V11_REFINED")
