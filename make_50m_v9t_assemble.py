from pathlib import Path
r=Path.home()/"Downloads"/"slingshot_quality_proof"
s=(r/"assemble_50m_v9s_egg.py").read_text(encoding="utf-8")
rules={
 'O=R/"cinematic_50m_v9s_egg"':'O=R/"cinematic_50m_v9t_egg"',
 'EGG_50M_8SEC_SHORTS_CUT.mp4':'EGG_50M_8SEC_TRACKLOCK_V9T.mp4',
 'SHORTS_QUALITY_CONTACT.jpg':'TRACKLOCK_QUALITY_CONTACT.jpg',
 '../cinematic_50m_v9_egg/EGG_50M_8SEC_V9_PREVIEW.mp4':'../cinematic_50m_v9s_egg/EGG_50M_8SEC_SHORTS_CUT.mp4',
 'VIEW_EGG_V9_VS_SHORTS.html':'VIEW_EGG_SHORTS_VS_TRACKLOCK.html',
 'SHORTS_CHECK.txt':'TRACKLOCK_CHECK.txt',
 'SHORTS_VIDEO_PASS':'TRACKLOCK_VIDEO_PASS',
 'SHORTS_REVIEW_READY':'TRACKLOCK_REVIEW_READY',
 '50m 계란 비행 카메라 V9 / 간결한 쇼츠컷 비교':'50m 계란 비행 카메라 | 쇼츠컷 vs 투사체 고정',
 '새총 50m 계란 — V9 / 쇼츠컷 비교':'새총 50m 계란 — 기존 쇼츠컷 vs 고정 추적',
 'V9 — 시네마틱 카메라':'기존 — 쇼츠 카메라',
 '쇼츠컷 — 최소한의 카메라':'신규 — 계란 고정 추적'
}
for a,b in rules.items():
 if a not in s:print("MISSING",a)
 else:s=s.replace(a,b)
s=s.replace(
 '새 버전은 <strong>계란 1종 쇼츠 카메라 검증 시안</strong>입니다. 발사 장면은 고정 구도, 비행은 한 화면으로 이어집니다. 충돌 장면과 효과는 V9와 동일하므로 카메라 문법만 비교할 수 있습니다.',
 '신규 버전은 계란에 카메라를 고정해 첫 약 40m를 비행하고 마지막 10m에서만 충돌 구도로 바뀝니다. 초점은 계란에 두고 배경 흐림과 상대 움직임을 강화했습니다. 충돌 반응은 기존 V9와 동일하므로 카메라 차이를 비교할 수 있습니다.'
)
dest=r/"assemble_50m_v9t_egg.py"
dest.write_text(s,encoding="utf-8")
compile(s,str(dest),"exec")
print("ASSEMBLER_READY",dest)
