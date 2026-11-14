import bpy,math,random
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
out=root/"glass_panel_challenge_v4"
bpy.ops.wm.open_mainfile(filepath=str(out/"GLASS_20_PANEL_CHALLENGE_V4_PREVIEW.blend"))
s=bpy.context.scene
random.seed(7801)

def principled(name):
    m=bpy.data.materials.get(name)
    if m is None:return None
    return m.node_tree.nodes.get("Principled BSDF")

glass=bpy.data.materials["V3 clear thin glass"]
edge=bpy.data.materials["V3 glass fracture edge glints"]
crack=bpy.data.materials["V3 stress fissures"]
pane=principled("V3 clear thin glass")
pane.inputs["Base Color"].default_value=(.84,.90,.90,1)
pane.inputs["Roughness"].default_value=.055
pane.inputs["Metallic"].default_value=0
pane.inputs["Transmission Weight"].default_value=.48
pane.inputs["Alpha"].default_value=.29
pane.inputs["IOR"].default_value=1.45
glass.surface_render_method="BLENDED"
p=principled("V3 glass fracture edge glints")
p.inputs["Base Color"].default_value=(.40,.57,.60,1)
p.inputs["Roughness"].default_value=.085
p.inputs["Metallic"].default_value=.04
p.inputs["Transmission Weight"].default_value=.18
p.inputs["Alpha"].default_value=.54
edge.surface_render_method="BLENDED"
p=principled("V3 stress fissures")
p.inputs["Base Color"].default_value=(.70,.82,.84,1)
p.inputs["Emission Strength"].default_value=0.0
p.inputs["Roughness"].default_value=.25
crack.surface_render_method="BLENDED"
# Bring thickness of the side faces down to millimetres without changing the overall silhouette.
count=0
for ob in bpy.data.objects:
    if " irregular shard " in ob.name and ob.type=="MESH":
        for vert in ob.data.vertices:
            vert.co.y*=.40
        ob.data.update()
        count+=1
    elif ob.name.startswith("Glass sheet") and ob.type=="MESH":
        # The unbroken pane was 26 mm thick. Make it 7 mm.
        ob.scale.y*=.27

# Fine concrete grain and bump under contact shadows.
floor=bpy.data.materials["Deep graphite laboratory concrete"]
p=principled("Deep graphite laboratory concrete")
p.inputs["Base Color"].default_value=(.20,.206,.203,1)
p.inputs["Roughness"].default_value=.79
nodes=floor.node_tree.nodes
links=floor.node_tree.links
noise=nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=95
noise.inputs["Detail"].default_value=2
noise.inputs["Roughness"].default_value=.70
bump=nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.11
bump.inputs["Distance"].default_value=.015
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],p.inputs["Normal"])
noise2=nodes.new("ShaderNodeTexNoise")
noise2.inputs["Scale"].default_value=2.5
noise2.inputs["Detail"].default_value=3
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.18
ramp.color_ramp.elements[0].color=(.145,.15,.15,1)
ramp.color_ramp.elements[1].position=.82
ramp.color_ramp.elements[1].color=(.265,.27,.265,1)
links.new(noise2.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],p.inputs["Base Color"])
# Satin metal rods, brushed surface, and wooden material with grain.
metal=principled("Brushed aluminium brackets")
metal.inputs["Base Color"].default_value=(.28,.31,.33,1)
metal.inputs["Metallic"].default_value=.65
metal.inputs["Roughness"].default_value=.32
woodmat=bpy.data.materials["Polished dark hardwood"]
w=woodmat.node_tree.nodes.get("Principled BSDF")
w.inputs["Base Color"].default_value=(.21,.10,.047,1)
w.inputs["Roughness"].default_value=.50
noise=woodmat.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=8
noise.inputs["Detail"].default_value=3
b=woodmat.node_tree.nodes.new("ShaderNodeBump")
b.inputs["Strength"].default_value=.24
b.inputs["Distance"].default_value=.004
woodmat.node_tree.links.new(noise.outputs["Fac"],b.inputs["Height"])
woodmat.node_tree.links.new(b.outputs["Normal"],w.inputs["Normal"])
p=principled("Machined steel | steel sphere")
p.inputs["Base Color"].default_value=(.51,.56,.59,1)
p.inputs["Metallic"].default_value=.91
p.inputs["Roughness"].default_value=.12
# Use dark but legible room lighting rather than cyan sci-fi emitters.
back=principled("Blue-dark stage environment")
back.inputs["Base Color"].default_value=(.17,.19,.20,1)
back.inputs["Roughness"].default_value=.90
world=s.world.node_tree.nodes.get("Background")
world.inputs["Color"].default_value=(.21,.23,.24,1)
world.inputs["Strength"].default_value=.55
for ob in bpy.data.objects:
    if ob.type=="LIGHT":
        if "Long cyan rim" in ob.name:
            ob.data.color=(.88,.94,1)
            ob.data.energy=1550
        elif "Warm strike accent" in ob.name:
            ob.data.color=(1,.94,.85)
            ob.data.energy=1900
        elif "Long cool fill" in ob.name:
            ob.data.color=(.95,.97,1)
            ob.data.energy=1600

def area(name,location,power,size,target,colour=(1,1,1)):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=power
    data.shape="RECTANGLE"
    data.size=size[0];data.size_y=size[1];data.color=colour
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
area("V4.1 softbox above launcher",(-3,-8,5),1250,(3,6),(0,-9,1.45))
area("V4.1 softbox down glass lane",(0,14,8),3500,(4,16),(0,11,1.5))
area("V4.1 wall fill",(0,31,5),2400,(6,4),(0,34,2.1))
# Deliberate contrast for film lighting, avoid cartoon overexposure.
s.view_settings.view_transform="AgX"
try:s.view_settings.look="AgX - Medium High Contrast"
except Exception:pass
s.view_settings.view_settings if False else None
s.camera.data.lens=37
s.render.resolution_percentage=100
# EEVEE blended glass renders cleanly without coarse alpha dithering.
s.render.engine="BLENDER_EEVEE"
try:s.eevee.use_raytracing=True
except Exception:pass
s.frame_set(1)
target=out/"GLASS_20_PANEL_CHALLENGE_V4_1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("MATERIAL_AND_SCENE_READY",target,"SHARDS",count,flush=True)
