from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
s=(r/"assemble_50m_v9_egg.py").read_text(encoding="utf-8")
pairs=[
 ('O=R/"cinematic_50m_v9_egg"', 'O=R/"cinematic_50m_v9s_egg"'),
 ('SOURCE += [O/"impact_frames"/f"frame_{n:04d}.png" for n in range(13,109)]', 'SOURCE += [R/"cinematic_50m_v9_egg"/"impact_frames"/f"frame_{n:04d}.png" for n in range(13,109)]'),
 ('EGG_50M_8SEC_V9_PREVIEW.mp4','EGG_50M_8SEC_SHORTS_CUT.mp4'),
 ('V9_EGG_QUALITY_CONTACT.jpg','SHORTS_QUALITY_CONTACT.jpg'),
 ('../cinematic_50m_v8/final/01_EGG_50M_8SEC_V8.mp4','../cinematic_50m_v9_egg/EGG_50M_8SEC_V9_PREVIEW.mp4'),
 ('V8 — 변경 전','V9 — 시네마틱 카메라'),
 ('V9 — 개선 시안','쇼츠컷 — 최소한의 카메라'),
 ('50m 계란 비행 V8 / V9 비교','50m 계란 비행 카메라 V9 / 간결한 쇼츠컷 비교'),
 ('새총 50m 계란 — V8 / V9 시안 비교','새총 50m 계란 — V9 / 쇼츠컷 비교'),
 ('VIEW_EGG_V8_VS_V9.html','VIEW_EGG_V9_VS_SHORTS.html'),
 ('V9_EGG_CHECK.txt','SHORTS_CHECK.txt'),
 ('V9_VIDEO_PASS','SHORTS_VIDEO_PASS'),
 ('V9_EGG_REVIEW_READY','SHORTS_REVIEW_READY')
]
for old,new in pairs:
 if old not in s: print("NOT_FOUND",old)
 else: s=s.replace(old,new)
# A quoted line in the HTML is the new video, but the old relative V9 path above must remain unchanged.
s=s.replace('충돌 후 확대는 없습니다.','충돌 후 확대는 없습니다. 카메라 전환을 줄인 두 화면 구성을 비교합니다.')
s=s.replace('V9는 현재 <strong>계란 1종 검증 시안</strong>입니다. 50.56m 거리 유지, 빠른 밴드 복원, 개선된 비행 카메라 및 재질, 넓은 충돌 구도를 비교하세요. 실제 유체 시뮬레이션은 아직 적용되지 않았습니다.',
'''새 버전은 <strong>계란 1종 쇼츠 카메라 검증 시안</strong>입니다. 발사 장면은 고정 구도, 비행은 한 화면으로 이어집니다. 충돌 장면과 효과는 V9와 동일하므로 카메라 문법만 비교할 수 있습니다.''')
# Ensure the V9 side of comparison actually references the old V9 file, and the Shorts side new output.
assert s.count('../cinematic_50m_v9_egg/EGG_50M_8SEC_V9_PREVIEW.mp4')==1
assert s.count('src="EGG_50M_8SEC_SHORTS_CUT.mp4"')==1
(r/"assemble_50m_v9s_egg.py").write_text(s,encoding="utf-8")
print("SHORTCUT_ASSEMBLER_READY")
