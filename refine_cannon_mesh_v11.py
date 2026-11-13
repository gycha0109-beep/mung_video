from pathlib import Path
import textwrap
r=Path.home()/"Downloads"/"slingshot_quality_proof"
p=r/"render_extension_v11.py"
s=p.read_text(encoding="utf8")
old=''' barrel.data.materials.append(m)
 for face in barrel.data.polygons:face.use_smooth=True'''
new=''' # A hollow thick-walled steel barrel, not a capped solid cylinder.
 n=48;v=[];faces=[]
 for radius,z in ((.33,-1.2),(.33,1.2),(.23,-1.2),(.23,1.2)):
  for i in range(n):
   a=2*math.pi*i/n
   v.append((radius*math.cos(a),radius*math.sin(a),z))
 for i in range(n):
  j=(i+1)%n
  faces.extend(((i,j,n+j,n+i),
                (2*n+i,3*n+i,3*n+j,2*n+j),
                (i,2*n+i,2*n+j,j),
                (n+i,n+j,3*n+j,3*n+i)))
 mesh=bpy.data.meshes.new("V11 hollow cannon bore")
 mesh.from_pydata(v,[],faces);mesh.update()
 barrel.data=mesh
 barrel.data.materials.append(m)
 for face in barrel.data.polygons:face.use_smooth=True'''
assert old in s
s=s.replace(old,new)
p.write_text(s,encoding="utf8")
compile(s,str(p),"exec")
print("V11_HOLLOW_CANNON_GEOMETRY_READY")
