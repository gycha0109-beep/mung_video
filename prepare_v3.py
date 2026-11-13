from pathlib import Path
src=Path.home()/"Downloads"/"slingshot_quality_proof"/"make_cinematic_v2.py"
t=src.read_text(encoding="utf8")
old='''def get_frame(kind,i):
 if i<41:return still(kind,"launch",i+1)
 if i<89:return still(kind,"impact",i-40)
 if i<139:
  t=(i-89)/49
  return blend_slow_frame(kind,12+23*(t**1.15),'replay')
 t=(i-139)/28
 return blend_slow_frame(kind,36+12*t,'impact')'''
new='''def get_frame(kind,i):
 if i<41:return still(kind,"launch",i+1)
 if i<=54:return still(kind,"impact",i-40)
 if i<=110:
  fraction=(i-54)/56
  return blend_slow_frame(kind,14+19*fraction,"impact")
 fraction=(i-110)/57
 return blend_slow_frame(kind,33+15*fraction,"impact")'''
assert old in t
t=t.replace(old,new)
t=t.replace('TITLE={"egg":"01_EGG_CINEMATIC_V2","steel":"02_STEEL_CINEMATIC_V2","billiard":"03_BILLIARD_CINEMATIC_V2"}','TITLE={"egg":"01_EGG_CINEMATIC_V3","steel":"02_STEEL_CINEMATIC_V3","billiard":"03_BILLIARD_CINEMATIC_V3"}')
t=t.replace('  # A damped, quieter replay makes the edit\'s alternate view apparent.\n replay=89/FPS+(16-12)/(35-12)*(50/FPS)\n add_noise(audio,replay,.6,.11,9,lowpass=245)\n','')
t=t.replace('("launch",1,41),("impact",1,48),("replay",12,35)','("launch",1,41),("impact",1,48)')
t=t.replace('SLINGSHOT_THREE_MATERIALS_CINEMATIC_V2_MASTER.mp4','SLINGSHOT_THREE_MATERIALS_CINEMATIC_V3_MASTER.mp4')
t=t.replace('kind+"_v2_sound.wav"','kind+"_v3_sound.wav"')
t=t.replace('concat_v2.txt','concat_v3.txt')
p=src.with_name("make_cinematic_v3.py")
p.write_text(t,encoding="utf8")
compile(t,str(p),"exec")
print("V3_READY",p)
