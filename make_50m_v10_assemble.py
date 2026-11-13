from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
s=(r/"assemble_50m_v9t_egg.py").read_text(encoding="utf-8")
repl=[
 ('O=R/"cinematic_50m_v9t_egg"','O=R/"cinematic_50m_v10_egg"'),
 ('SOURCE=[O/"launch_frames"/f"frame_{n:04d}.png" for n in range(1,97)]\nSOURCE += [R/"cinematic_50m_v9_egg"/"impact_frames"/f"frame_{n:04d}.png" for n in range(13,109)]',
  'SOURCE=[O/"frames"/f"frame_{n:04d}.png" for n in range(1,193)]'),
 ('EGG_50M_8SEC_TRACKLOCK_V9T.mp4','EGG_50M_8SEC_V10_UNCUT.mp4'),
 ('TRACKLOCK_QUALITY_CONTACT.jpg','V10_UNCUT_CONTACT.jpg'),
 ('VIEW_EGG_SHORTS_VS_TRACKLOCK.html','VIEW_EGG_V9T_VS_V10.html'),
 ('TRACKLOCK_CHECK.txt','V10_QUALITY_CHECK.txt'),
 ('TRACKLOCK_VIDEO_PASS','V10_VIDEO_PASS'),
 ('TRACKLOCK_REVIEW_READY','V10_RELEASE_READY'),
 ('../cinematic_50m_v9s_egg/EGG_50M_8SEC_SHORTS_CUT.mp4','../cinematic_50m_v9t_egg/EGG_50M_8SEC_TRACKLOCK_V9T.mp4'),
 ('50m 계란 비행 카메라 | 쇼츠컷 vs 투사체 고정','50m 계란 V9T / V10 한 장면 비교'),
 ('새총 50m 계란 — 기존 쇼츠컷 vs 고정 추적','새총 50m 계란 — 이전 전환 화면 vs V10 연속 장면'),
 ('기존 — 쇼츠 카메라','V9T — 다른 충돌 장면으로 전환'),
 ('신규 — 계란 고정 추적','V10 — 카메라 멈춤, 한 장면 충돌'),
 ('49<=i<=86','49<=i<=91')
]
for old,new in repl:
 if old not in s:print("MISSING",old)
 else:s=s.replace(old,new)
s=s.replace('신규 버전은 계란에 카메라를 고정해 첫 약 40m를 비행하고 마지막 10m에서만 충돌 구도로 바뀝니다. 초점은 계란에 두고 배경 흐림과 상대 움직임을 강화했습니다. 충돌 반응은 기존 V9와 동일하므로 카메라 차이를 비교할 수 있습니다.',
'''V10은 50m 발사 후 <strong>벽 충돌 약 5.5m 전</strong>까지 계란을 따라가다가 카메라가 그 자리에 멈춥니다. <strong>벽·바닥·조명·카메라를 교체하지 않고 한 Blender 장면에서 충돌까지</strong> 진행합니다. 잘못 배치된 가죽 링 13개를 제거했습니다. 충돌 액체 효과는 기존 V9의 스타일을 유지했습니다.''')
s=s.replace('첫 96 launch frames and 96 physical impact frames newly rendered.','192 frames from ONE Blender scene, with no source-scene splice.')
out=r/"assemble_50m_v10_egg.py"
out.write_text(s,encoding="utf-8")
compile(s,str(out),"exec")
print("V10_ASSEMBLER_READY",out)
