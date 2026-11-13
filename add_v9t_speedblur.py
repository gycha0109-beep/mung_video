from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
p=r/"assemble_50m_v9t_egg.py"
s=p.read_text(encoding="utf-8")
mark="def encode():"
assert mark in s
func='''def directional_background_blur(im,frame):
 # Camera tracks the egg; the world streaks downward. Keep the egg sharp.
 # Compute a soft elliptical matte around the centered projectile.
 yy,xx=np.ogrid[:H,:W]
 radial=((xx-W*.50)/(W*.103))**2+((yy-H*.50)/(H*.085))**2
 egg=np.clip((1.25-radial)/.48,0,1)
 ramp=np.clip((frame-48.)/8.,0,1)
 ground=np.clip((yy-H*.23)/(H*.65),0,1)
 amount=ramp*(.18+.72*ground)*(1-egg)
 # Vertical motion streak: stronger near the ground, subtle in sky.
 k=int(21+32*np.clip((frame-49.)/25.,0,1))
 if k%2==0:k+=1
 kernel=np.ones((k,1),dtype=np.float32)/k
 streak=cv2.filter2D(im,-1,kernel,borderType=cv2.BORDER_REFLECT101)
 soft=cv2.GaussianBlur(im,(0,0),2.2)
 bg=cv2.addWeighted(streak,.82,soft,.18,0)
 return np.clip(im.astype(np.float32)*(1-amount[:,:,None])+bg.astype(np.float32)*amount[:,:,None],0,255).astype(np.uint8)
'''
s=s.replace(mark,func+mark)
needle='   proc.stdin.write(im.tobytes())'
assert needle in s
s=s.replace(needle,'''   if 49<=i<=86:
    im=directional_background_blur(im,i)
   proc.stdin.write(im.tobytes())''')
p.write_text(s,encoding="utf-8")
compile(s,str(p),"exec")
print("BACKGROUND_ONLY_BLUR_READY")
