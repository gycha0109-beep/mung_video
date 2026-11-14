from pathlib import Path
root=Path(r"C:\Users\hun\Documents\mung_video")
src=(root/"build_glass_challenge_v2.py").read_text(encoding="utf-8")
s=src.replace('glass_panel_challenge_v2','glass_panel_challenge_v3').replace('GLASS_20_PANEL_CHALLENGE_V2.blend','GLASS_20_PANEL_CHALLENGE_V3.blend')
s=s.replace('SEED=20261114','SEED=20261114')  # same break count for fair comparison
s=s.replace('glass=mat("V2 tempered clear glass",(.69,.90,.96),rough=.095,trans=.07,alpha=.24)','glass=mat("V3 clear thin glass",(.75,.91,.95),rough=.075,trans=.30,alpha=.23)')
s=s.replace('glass.surface_render_method="BLENDED"','glass.surface_render_method="DITHERED"')
s=s.replace('glass_edge=mat("V2 broken glass bright edge facets",(.34,.88,.98),rough=.12,trans=.08,alpha=.91)','glass_edge=mat("V3 glass fracture edge glints",(.46,.78,.85),rough=.17,trans=.12,alpha=.97)')
s=s.replace('crack_mat=mat("V2 irregular glass stress fracture",(.80,.96,1),rough=.30,emission=.35)','crack_mat=mat("V3 stress fissures",(.83,.95,1),rough=.31,emission=.30)')
anchor='def polygon_shard(name,xzpoints,cy,material):'
assert anchor in s
s=s.replace(anchor,'def polygon_shard(name,xzpoints,cy,material,thickness=None):')
s=s.replace('    verts=[(x,cy-.011,z+PANEL_Z) for x,z in xzpoints]+[(x,cy+.011,z+PANEL_Z) for x,z in xzpoints]',
'''    # Actual front/back faces, plus visible edges. Thickness varies with fragment scale.
    t=thickness if thickness is not None else .016
    verts=[(x,cy-t/2,z+PANEL_Z) for x,z in xzpoints]+[(x,cy+t/2,z+PANEL_Z) for x,z in xzpoints]''')
s=s.replace('    mesh.materials.append(glass_edge)\n    for face in mesh.polygons:',
'''    mesh.materials.append(glass_edge)
    for face in mesh.polygons:''')
s=s.replace('V2 STOP jagged radial','V3 STOP jagged radial')
s=s.replace('    for j in range(10):\n        r=.12+.29*math.sqrt(rng.random())','    for j in range(18):\n        r=.085+.30*math.sqrt(rng.random())')
s=s.replace('print("V2_FRACTURE"','print("V3_FRACTURE"')
s=s.replace('name=f"V2 pane {idx+1:02d} irregular shard {part_num:03d}"','name=f"V3 pane {idx+1:02d} irregular shard {part_num:03d}"')
s=s.replace('        ob=polygon_shard(name,poly,y,glass)\n        bpy.context.view_layer.objects.active=ob',
'''        cx0=sum(p[0] for p in poly)/len(poly)
        cz0=sum(p[1] for p in poly)/len(poly)
        area=abs(sum(poly[k][0]*poly[(k+1)%len(poly)][1]-
                    poly[(k+1)%len(poly)][0]*poly[k][1] for k in range(len(poly)))/2)
        t=min(.023,max(.009,.011+.065*math.sqrt(area))) * rng.uniform(.85,1.15)
        ob=polygon_shard(name,poly,y,glass,thickness=t)
        bpy.context.view_layer.objects.active=ob''')
s=s.replace('        delay=0 if dist<.45 else (1 if dist<.75 else 2)','        delay=0 if dist<.35 else (1 if dist<.70 else 2)')
s=s.replace('        ob.rigid_body.restitution=.13','        ob.rigid_body.restitution=.16')
# Short contact fissures are tied to hit time, then disappear as fragments separate.
insertion='''    # V3 impact fissures: short-lived, physically localized to the hit.
    for radial in range(9):
        a=radial*math.tau/9+rng.uniform(-.10,.10)
        radius=.025
        previous=(0,y-.035,PANEL_Z)
        for segment in range(3):
            a+=rng.uniform(-.16,.16)
            radius+=rng.uniform(.065,.10)
            nxt=(radius*math.cos(a),y-.035,PANEL_Z+radius*math.sin(a))
            fiss=cylinder_between(f"V3 contact fissure {idx+1}-{radial}-{segment}",previous,nxt,.0018,crack_mat,6)
            visibility(fiss,1,False)
            visibility(fiss,f-1,False)
            visibility(fiss,f,True)
            visibility(fiss,f+3,False)
            previous=nxt
    # Dust-sized splinters appear only around the projectile, not the whole panel.
    # These are a visual secondary effect; larger pieces below remain rigid bodies.
    for micro in range(12):
        ang=rng.random()*math.tau
        rad=rng.uniform(.012,.06)
        mx,mz=rad*math.cos(ang),rad*math.sin(ang)
        sz=rng.uniform(.008,.026)
        poly=[(mx-sz,mz-sz*.48),(mx+sz*.9,mz),(mx-sz*.25,mz+sz*.8)]
        speck=polygon_shard(f"V3 fine splinter {idx+1}-{micro}",poly,y,glass_edge,thickness=.0035)
        visibility(speck,1,False)
        visibility(speck,f-1,False)
        visibility(speck,f,True)
        speck.location=(0,0,0)
        speck.keyframe_insert(data_path="location",frame=f)
        speed=rng.uniform(.08,.24)
        speck.location=(math.cos(ang)*speed,speed*1.65,math.sin(ang)*speed*.8)
        speck.keyframe_insert(data_path="location",frame=f+2)
        speck.location=(math.cos(ang)*speed*1.8,speed*2.9,math.sin(ang)*speed-0.07)
        speck.keyframe_insert(data_path="location",frame=f+7)
        speck.rotation_euler=(rng.random(),rng.random(),rng.random())
        speck.keyframe_insert(data_path="rotation_euler",frame=f+7)
        visibility(speck,f+9,False)
'''
anchor='    for part_num,poly in enumerate(all_polys):'
assert s.count(anchor)==1
s=s.replace(anchor,insertion+'\n'+anchor)
s=s.replace('note="V2 irregular Voronoi-style pre-fracture; simplified stylized energy attenuation for ball; rigid-body shards are released on contact, not a fully coupled fracture solver."',
'''note="V3 variable-thickness fragments and dithered glass, radial fissures and small secondary splinters. Energy model simplified, no coupled stress solver."''')
(root/"build_glass_challenge_v3.py").write_text(s,encoding="utf-8")
render=(root/"render_glass_challenge_v2.py").read_text(encoding="utf-8")
render=render.replace('glass_panel_challenge_v2','glass_panel_challenge_v3').replace('GLASS_20_PANEL_CHALLENGE_V2.blend','GLASS_20_PANEL_CHALLENGE_V3.blend')
render=render.replace('[1,40,49,57,63,72,95,120,146,154,171,192]','[1,40,49,57,60,63,72,95,120,146,154,171,192]')
(root/"render_glass_challenge_v3.py").write_text(render,encoding="utf-8")
assemble=(root/"assemble_glass_challenge_v2.py").read_text(encoding="utf-8")
assemble=assemble.replace('glass_panel_challenge_v2','glass_panel_challenge_v3')
assemble=assemble.replace('GLASS_V2_SYNTH_SOUND','GLASS_V3_SYNTH_SOUND')
assemble=assemble.replace('GLASS_20_PANELS_8SEC_V2','GLASS_20_PANELS_8SEC_V3')
assemble=assemble.replace('VIEW_GLASS_CHALLENGE_V2.html','VIEW_GLASS_CHALLENGE_V3.html')
assemble=assemble.replace('OPEN_GLASS_CHALLENGE_V2.cmd','OPEN_GLASS_CHALLENGE_V3.cmd')
assemble=assemble.replace('V2 영상 비교','V2 / V3 영상 비교').replace('VIEW_GLASS_V1_VS_V2.html','VIEW_GLASS_V2_VS_V3.html')
assemble=assemble.replace('add_burst(e["frame"]/24,.35*(1-.027*i),.19,1880+93*(i%5),"glass")',
'''add_burst(e["frame"]/24,.39*(1-.025*i),.16,2070+91*(i%5),"glass")
    add_burst(e["frame"]/24+.042,.12*(1-.03*i),.17,630+43*(i%7),"glass")''')
(root/"assemble_glass_challenge_v3.py").write_text(assemble,encoding="utf-8")
print("V3_FILES_CREATED",len(s.splitlines()),len(render.splitlines()),len(assemble.splitlines()))
