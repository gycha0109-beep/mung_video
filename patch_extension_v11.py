from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
p=r/"render_extension_v11.py"
s=p.read_text(encoding="utf8")
a='for o in list(s.objects):\n if o.name.startswith("V9 ") or o.name.startswith("V10 original shell fragments"):\n  bpy.data.objects.remove(o,do_unlink=True)'
b='''for o in list(s.objects):
 if (o.name.startswith("V9 ") or o.name.startswith("V10 original shell fragments")
     or o.name.startswith("Clay splinter") or o.name.startswith("Microscopic brick powder")):
  bpy.data.objects.remove(o,do_unlink=True)
# V10 previously keyed some original wall bricks to disappear for the egg.
# All materials must begin with an intact wall; only material-specific damage is allowed.
for o in s.objects:
 if o.name.startswith("Hand-laid worn masonry"):
  o.animation_data_clear()
  o.hide_render=False'''
assert a in s;s=s.replace(a,b)
a='   z=max(.115,orig.z+(1.0+random.random()*.2)*t-4.905*t*t)'
b='   z=max(.115,orig.z+(1.0+.09*math.sin(j*2.1))*t-4.905*t*t)'
assert a in s;s=s.replace(a,b)
a='   y=-.34-1.4*t+random.uniform(-.012,.012)'
b='   y=-.34-1.4*t+(.012*math.sin(j*.9))'
assert a in s;s=s.replace(a,b)
a='location=(0,-49.55,1.53)'
b='location=(0,-52.05,1.53)'
assert a in s;s=s.replace(a,b)
a='for f,y in ((1,-49.55),(45,-49.55),(48,-49.55),(49,-49.90),(53,-49.78),(61,-49.55),(192,-49.55)):'
b='for f,y in ((1,-52.05),(45,-52.05),(48,-52.05),(49,-52.40),(53,-52.28),(61,-52.05),(192,-52.05)):'
assert a in s;s=s.replace(a,b)
a='location=(x,-49.7,.50)'
b='location=(x,-52.2,.50)'
assert a in s;s=s.replace(a,b)
p.write_text(s,encoding="utf8")
compile(s,str(p),"exec")
print("EXTENSION_V11_PATCHED")
