"""Build paper PDF and slide deck: `uv run src/build.py` (run analysis.py first)."""
from __future__ import annotations

import base64
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
FONT = "Malgun Gothic"
INK = RGBColor(0x1B, 0x1F, 0x24)
ACC = RGBColor(0x1F, 0x6F, 0xEB)


def build_pdf() -> None:
    md = (ROOT / "paper" / "main.md").read_text(encoding="utf-8")

    def embed(m: re.Match) -> str:
        path = (ROOT / "paper" / m.group(2)).resolve()
        b64 = base64.b64encode(path.read_bytes()).decode()
        return f'<img alt="{m.group(1)}" src="data:image/png;base64,{b64}" style="max-width:80%">'

    html = markdown.markdown(re.sub(r"!\[(.*?)\]\((.*?)\)", "\x00\\1\x00\\2\x00", md).replace("\x00", "\x00"), extensions=["tables"])
    # images: convert after markdown to keep tables intact
    md_img = re.sub(r"!\[(.*?)\]\((.*?)\)", lambda m: embed(m), md)
    html = markdown.markdown(md_img, extensions=["tables"])
    css = (
        f"body{{font-family:'{FONT}';font-size:10.5pt;line-height:1.55;margin:0 8mm;color:#1b1f24}}"
        "h1{font-size:20pt;margin-bottom:2pt}h3{color:#555;font-weight:400}h2{border-bottom:1px solid #ccc;padding-bottom:2pt;margin-top:18pt}"
        "table{border-collapse:collapse;font-size:9pt;margin:6pt 0}th,td{border:1px solid #bbb;padding:2pt 6pt}th{background:#f2f4f7}"
        "img{display:block;margin:6pt auto}code{background:#f2f4f7;padding:0 3pt}"
    )
    doc = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{html}</body></html>"
    tmp = ROOT / "paper" / "_paper.html"
    tmp.write_text(doc, encoding="utf-8")
    with sync_playwright() as p:
        b = None
        for ch in ("chrome", "msedge", None):
            try:
                b = p.chromium.launch(channel=ch) if ch else p.chromium.launch()
                break
            except Exception:
                continue
        assert b, "no browser"
        pg = b.new_page()
        pg.goto(tmp.as_uri(), wait_until="networkidle")
        pg.pdf(path=str(ROOT / "paper" / "cvd-screening-review.pdf"), format="A4", margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
        b.close()
    tmp.unlink()


def _text(slide, x, y, w, h, text, size=20, bold=False, color=INK):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split("\n")):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.text = line
        para.font.size, para.font.bold, para.font.name = Pt(size), bold, FONT
        para.font.color.rgb = color
        para.space_after = Pt(6)
    return tb


def build_slides() -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def slide(title: str):
        s = prs.slides.add_slide(blank)
        _text(s, 0.6, 0.35, 12, 0.9, title, 30, True)
        bar = s.shapes.add_shape(1, Inches(0.6), Inches(1.2), Inches(1.2), Inches(0.06))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACC
        bar.line.fill.background()
        return s

    s = prs.slides.add_slide(blank)
    _text(s, 0.8, 2.2, 11.5, 1.5, "색각 이상 자가 테스트는\n얼마나 믿을 수 있는가", 42, True)
    _text(s, 0.8, 4.4, 11.5, 1.2, "발표된 유병률·검사 성능 수치를 결합한 양성예측도 분석\n새 실험 데이터 없음 · 전 계산 재현 가능", 20, False, RGBColor(0x55, 0x5B, 0x63))

    s = slide("질문")
    _text(s, 0.6, 1.6, 12, 4.5, "온라인·앱 색각 테스트가 널리 퍼져 있다.\n\n유병률이 낮은 집단에서, 알려진 검사 성능으로\n'정상'과 '이상' 결과는 각각 얼마나 믿을 만한가?\n\n→ 한국 유병률 × 발표된 민감도·특이도 → PPV·NPV·놓침", 24)

    s = slide("입력값은 모두 문헌 출처")
    _text(s, 0.6, 1.6, 12, 4.8,
          "한국 성인 유병률  남 6.5% · 여 1.1% · 전체 3.9%  (n=2,686)  — Kim & Ng 2019\n"
          "숨은 숫자 판 민감도 약 50%  — Birch 1997\n"
          "변환+소실판 민감도 95.5~99%  — Birch 1997\n"
          "앱 특이도 최고 95.2% · 최저 54.8%  — Sorkin 2016\n\n"
          "가정(†): 인쇄판 특이도 95%, 앱 민감도 95.5% — 출처 없음, 명시함", 22)

    s = slide("결과 1 — 특이도가 낮으면 양성의 대부분이 오경보")
    s.shapes.add_picture(str(ROOT / "figures" / "fig1_ppv_vs_specificity.png"), Inches(0.6), Inches(1.5), height=Inches(5.4))
    _text(s, 8.4, 2.0, 4.6, 4.5, "앱 특이도 .548\n남성 PPV 12.8%†\n\n앱 특이도 .952\n남성 PPV 58.0%†\n\n여성은 최고 성능 앱도\nPPV 18.1%†\n(유병률 1.1%의 결과)", 20)

    s = slide("결과 2 — 판 종류가 놓침을 결정")
    s.shapes.add_picture(str(ROOT / "figures" / "fig2_missed_cases.png"), Inches(0.6), Inches(1.5), height=Inches(5.4))
    _text(s, 8.4, 2.0, 4.6, 4.5, "남성 1,000명당\n숨은 숫자 판: 32.5명 놓침\n변환+소실판: 2.9명\n\n약 11배(점추정)", 22)

    s = slide("한계")
    _text(s, 0.6, 1.6, 12, 5,
          "• 인쇄판 특이도·앱 민감도는 가정 — 결과에 조건부\n"
          "• 유병률과 검사 성능이 서로 다른 집단에서 왔음\n"
          "• 적록 결함 중심, 청황·중증도별 성능 미반영\n"
          "• 화면 조건 영향은 정성적 근거만\n"
          "• 5인 리뷰어 패널은 AI 시뮬레이션 자체 점검 — 외부 심사 아님", 22)

    s = slide("결론")
    _text(s, 0.6, 1.6, 12, 4.8,
          "1. '정상' 결과는 어떤 판을 썼는지 알아야 해석된다\n"
          "2. '이상' 결과는 여성·저특이도 앱에서 대부분 오경보로 계산된다\n"
          "3. 안내 문구: 선별용, 확진은 안과\n\n"
          "코드·데이터·리뷰: github.com/rhlfur2055-prog/cvd-screening-review", 24)

    prs.save(ROOT / "slides" / "cvd-screening-review.pptx")


if __name__ == "__main__":
    build_pdf()
    build_slides()
    print("built")
