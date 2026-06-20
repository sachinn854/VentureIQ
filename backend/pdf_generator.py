import io
import html as _html
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

from backend.schemas.models import FinalReport

# ─── Colour Palette ───────────────────────────────────────────────────────────
BLUE     = colors.HexColor('#3B82F6')
BLUE_LT  = colors.HexColor('#EFF6FF')
GREEN    = colors.HexColor('#10B981')
GREEN_LT = colors.HexColor('#ECFDF5')
RED      = colors.HexColor('#EF4444')
RED_LT   = colors.HexColor('#FEF2F2')
AMBER    = colors.HexColor('#F59E0B')
VIOLET   = colors.HexColor('#8B5CF6')
GRAY_900 = colors.HexColor('#111827')
GRAY_600 = colors.HexColor('#4B5563')
GRAY_400 = colors.HexColor('#9CA3AF')
GRAY_100 = colors.HexColor('#F3F4F6')
WHITE    = colors.white

DIM_COLORS = {
    'market':      BLUE,
    'competition': VIOLET,
    'financial':   AMBER,
    'risk':        RED,
}


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', fontSize=22, textColor=GRAY_900, fontName='Helvetica-Bold', spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontSize=10, textColor=GRAY_400, fontName='Helvetica', spaceAfter=0),
        'section': ParagraphStyle('section', fontSize=12, textColor=GRAY_900, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6),
        'body': ParagraphStyle('body', fontSize=9, textColor=GRAY_600, fontName='Helvetica', leading=14, spaceAfter=4),
        'small': ParagraphStyle('small', fontSize=8, textColor=GRAY_400, fontName='Helvetica', leading=12),
        'verdict_go':   ParagraphStyle('verdict_go',   fontSize=28, textColor=GREEN,    fontName='Helvetica-Bold', alignment=TA_CENTER),
        'verdict_nogo': ParagraphStyle('verdict_nogo', fontSize=28, textColor=RED,      fontName='Helvetica-Bold', alignment=TA_CENTER),
        'score_big': ParagraphStyle('score_big', fontSize=36, textColor=GRAY_900, fontName='Helvetica-Bold', alignment=TA_CENTER),
        'label': ParagraphStyle('label', fontSize=8, textColor=GRAY_400, fontName='Helvetica', alignment=TA_CENTER),
        'bullet': ParagraphStyle('bullet', fontSize=9, textColor=GRAY_600, fontName='Helvetica', leading=14, leftIndent=12, spaceAfter=3),
    }


def _score_bar_table(label: str, score: float, bar_color: colors.Color, s: dict) -> Table:
    filled = int(round((score / 10) * 20))
    empty  = 20 - filled

    bar_cells = [[
        Paragraph(label, s['small']),
        Paragraph(f'{score:.1f}', s['small']),
    ]]
    bar_table = Table(bar_cells, colWidths=[5 * cm, 1 * cm])
    bar_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Simple bar using colored rectangles via a nested table
    block = '█'
    dash  = '░'
    bar_str = f'<font color="#{bar_color.hexval().lstrip("#")}">{block * filled}</font><font color="#E5E7EB">{dash * empty}</font>'

    data = [
        [Paragraph(f'{label}', s['small']), Paragraph(bar_str, s['small']), Paragraph(f'{score:.1f}/10', s['small'])],
    ]
    t = Table(data, colWidths=[4 * cm, 7 * cm, 2 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def generate_pdf(report: FinalReport, idea: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm,  bottomMargin=2 * cm,
    )

    s = _styles()
    story = []
    W = A4[0] - 4 * cm  # usable width

    # ── Header ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('⚡ Startup Validator', s['title']),
        Paragraph('AI-Powered Multi-Agent Analysis', s['label']),
    ]]
    header_table = Table(header_data, colWidths=[W * 0.7, W * 0.3])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=1, color=GRAY_100, spaceAfter=10))

    # ── Idea Summary ──────────────────────────────────────────────────────────
    story.append(Paragraph('Idea Analyzed', s['section']))
    safe_idea = _html.escape(idea[:400]) + ('...' if len(idea) > 400 else '')
    idea_table = Table(
        [[Paragraph(safe_idea, s['body'])]],
        colWidths=[W],
    )
    idea_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE_LT),
        ('ROUNDEDCORNERS', [6]),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
    ]))
    story.append(idea_table)
    story.append(Spacer(1, 14))

    # ── Verdict + Score ────────────────────────────────────────────────────────
    is_go       = report.verdict == 'GO'
    verdict_bg  = GREEN_LT if is_go else RED_LT
    verdict_col = GREEN    if is_go else RED
    verdict_style = s['verdict_go'] if is_go else s['verdict_nogo']

    verdict_data = [
        [
            Paragraph(report.verdict, verdict_style),
            Paragraph(f'{report.overall_score:.1f}', s['score_big']),
            Paragraph(f'{report.confidence}%', s['score_big']),
        ],
        [
            Paragraph('Decision', s['label']),
            Paragraph('Overall Score / 10', s['label']),
            Paragraph('Confidence', s['label']),
        ],
    ]
    verdict_table = Table(verdict_data, colWidths=[W / 3, W / 3, W / 3])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), verdict_bg),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, 0), 16),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('LINEBELOW',     (0, 0), (-1, 0), 0.5, GRAY_100),
        ('BOX',           (0, 0), (-1, -1), 1, verdict_col),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 14))

    # ── Score Breakdown ────────────────────────────────────────────────────────
    story.append(Paragraph('Score Breakdown', s['section']))
    bd = report.score_breakdown or {}
    for dim, col in DIM_COLORS.items():
        val = bd.get(dim, 0.0)
        story.append(_score_bar_table(dim.capitalize(), val, col, s))
    story.append(Spacer(1, 8))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story.append(Paragraph('Executive Summary', s['section']))
    summary_table = Table(
        [[Paragraph(report.executive_summary, s['body'])]],
        colWidths=[W],
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), GRAY_100),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # ── Strengths / Risks / Next Steps ────────────────────────────────────────
    def bullet_list(title: str, items: list, icon: str, bg: colors.Color) -> Table:
        content = [Paragraph(f'<b>{icon}  {title}</b>', s['body'])]
        for item in items:
            content.append(Paragraph(f'•  {item}', s['bullet']))
        col = Table([[p] for p in content], colWidths=[W / 3 - 0.4 * cm])
        col.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), bg),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ]))
        return col

    three_col = Table(
        [[
            bullet_list('Top Strengths', report.top_3_strengths,        '💪', GREEN_LT),
            bullet_list('Key Risks',      report.top_3_risks,            '⚠️', RED_LT),
            bullet_list('Next Steps',     report.recommended_next_steps, '🚀', BLUE_LT),
        ]],
        colWidths=[W / 3, W / 3, W / 3],
        hAlign='LEFT',
    )
    three_col.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
    ]))
    story.append(Paragraph('Analysis', s['section']))
    story.append(three_col)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRAY_100))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'Generated by Startup Validator · AI-powered multi-agent analysis · Results are indicative, not financial advice.',
        s['small'],
    ))

    doc.build(story)
    return buffer.getvalue()
