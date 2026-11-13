from pathlib import Path
import cv2, json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cinematic_50m_v12_steel"
OUT.mkdir(exist_ok=True)
video = ROOT / "cinematic_50m_v11_extension" / "steel" / "01_STEEL_50M_V11.mp4"
before = OUT / "STEEL_V11_FRAME_094.png"
after = OUT / "STEEL_V12_FRAME_094.png"
assert video.is_file(), video
cap = cv2.VideoCapture(str(video))
assert cap.isOpened(), "Cannot open V11 video"
cap.set(cv2.CAP_PROP_POS_FRAMES, 93)
ok, frame = cap.read()
cap.release()
assert ok and frame is not None
assert frame.shape[0:2] == (1280,720), frame.shape
assert cv2.imwrite(str(before), frame)
v12 = cv2.imread(str(after))
if v12 is None:
    print("V12_NOT_RENDERED: baseline extracted; HTML will display pending image")
else:
    assert v12.shape[:2] == frame.shape[:2], (v12.shape, frame.shape)
html = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>V11 vs V12 | 쇠구슬 충돌 직전 동일 프레임</title>
<style>
:root{color-scheme:dark;font-family:system-ui,"Malgun Gothic",sans-serif}
*{box-sizing:border-box}body{margin:0;background:#0b1018;color:#eaf1f8;padding:22px}
main{max-width:1360px;margin:auto}h1{font-size:1.6rem;margin-bottom:7px}
p{color:#b2c2d2;line-height:1.65} .meta{font-size:.88rem}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
figure{margin:0;background:#192331;border:1px solid #394656;border-radius:12px;padding:12px}
img{width:100%;height:auto;display:block;border-radius:7px}
figcaption{padding:10px 2px 2px;font-weight:700}
.compare{width:min(100%,600px);position:relative;margin:22px auto;aspect-ratio:9/16;overflow:hidden;border-radius:12px;border:1px solid #506173}
.compare>img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.compare .right{clip-path:inset(0 0 0 50%)}
.compare:after{content:"";position:absolute;top:0;bottom:0;left:50%;border-left:2px solid #eaf5ff;pointer-events:none}
input[type=range]{width:100%;accent-color:#91c4ee}
code{font-family:Consolas,monospace}a{color:#8bc7ff}
@media(max-width:650px){body{padding:10px}.cols{gap:7px}figure{padding:5px}figcaption{font-size:.8rem}}
</style></head><body><main>
<h1>V11 / V12 — 쇠구슬 충돌 직전 그래픽 비교</h1>
<p class="meta">동일 장면 · 동일 카메라 · 94프레임(3.92초) · 720×1280 · V12: Cycles + 사실적 표면·조명 개선. V12는 단일 정지 프레임 시안이며 충돌 물리 개선과는 별도입니다.</p>
<div class="cols">
<figure><img src="STEEL_V11_FRAME_094.png" alt="V11 original"><figcaption>V11 — 기존 그래픽</figcaption></figure>
<figure><img src="STEEL_V12_FRAME_094.png" alt="V12 render"><figcaption>V12 — 시네마틱 CGI 시안</figcaption></figure>
</div>
<h2>같은 위치 비교</h2>
<div class="compare"><img src="STEEL_V11_FRAME_094.png" alt="before"><img class="right" id="after" src="STEEL_V12_FRAME_094.png" alt="after"></div>
<input id="slider" type="range" min="0" max="100" value="50" aria-label="V12 비교 위치">
<p>슬라이더를 움직이면 왼쪽 V11과 오른쪽 V12의 경계를 이동할 수 있습니다.</p>
<p><a href="../cinematic_50m_v11_extension/VIEW_ALL_50M_V11.html">V11 네 소재 영상 열기</a></p>
</main><script>
const range=document.querySelector("#slider"), over=document.querySelector("#after"), box=document.querySelector(".compare");
range.addEventListener("input",()=>{let v=Number(range.value);over.style.clipPath="inset(0 0 0 "+v+"%)";box.style.setProperty("--split",v+"%")});
</script></body></html>"""
html=html.replace('left:50%;border-left:2px','left:var(--split,50%);border-left:2px')
path = OUT / "VIEW_STEEL_V11_VS_V12.html"
path.write_text(html, encoding="utf-8")
launcher=ROOT / "OPEN_STEEL_V12_COMPARE.cmd"
launcher.write_text('@echo off\r\nsetlocal\r\nstart "" "%~dp0cinematic_50m_v12_steel\\VIEW_STEEL_V11_VS_V12.html"\r\n', encoding="ascii")
print("BASELINE_OK", before)
print("V12_EXISTS", after.exists(), "HTML", path, "CMD", launcher)
