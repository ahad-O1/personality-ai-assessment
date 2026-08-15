"""
Professional PDF report generation for personality assessment results.
"""

from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    CondPageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from assessment.models import AssessmentResult

from recommendations.ai_personality import (
    generate_improvements,
    generate_personality_details,
    generate_personality_type,
    generate_strengths,
    get_personality_analysis,
)
from recommendations.recommendation_engine import get_recommended_careers


# =========================================================
# Color palette
# =========================================================

PRIMARY = HexColor("#1E3A8A")
PRIMARY_LIGHT = HexColor("#2563EB")
SECONDARY = HexColor("#7C3AED")

TEXT_DARK = HexColor("#0F172A")
TEXT_MUTED = HexColor("#64748B")

BACKGROUND = HexColor("#F8FAFC")
CARD_BACKGROUND = HexColor("#FFFFFF")
LIGHT_BLUE = HexColor("#EFF6FF")
LIGHT_PURPLE = HexColor("#F5F3FF")
LIGHT_GREEN = HexColor("#ECFDF5")
LIGHT_ORANGE = HexColor("#FFF7ED")

BORDER = HexColor("#E2E8F0")
PROGRESS_BACKGROUND = HexColor("#E5E7EB")
SUCCESS = HexColor("#059669")
WARNING = HexColor("#D97706")


# =========================================================
# Custom progress bar
# =========================================================

class ScoreProgressBar(Flowable):
    """Draw a modern horizontal score progress bar."""

    def __init__(
        self,
        score,
        width=165 * mm,
        height=4.5 * mm,
        bar_color=PRIMARY_LIGHT,
    ):
        super().__init__()

        try:
            self.score = max(0, min(100, float(score)))
        except (TypeError, ValueError):
            self.score = 0

        self.width = width
        self.height = height
        self.bar_color = bar_color

    def draw(self):
        canvas = self.canv
        radius = self.height / 2

        # Background
        canvas.setFillColor(PROGRESS_BACKGROUND)
        canvas.roundRect(
            0,
            0,
            self.width,
            self.height,
            radius,
            fill=1,
            stroke=0,
        )

        # Filled section
        filled_width = self.width * self.score / 100

        if filled_width > 0:
            canvas.setFillColor(self.bar_color)
            canvas.roundRect(
                0,
                0,
                filled_width,
                self.height,
                radius,
                fill=1,
                stroke=0,
            )


# =========================================================
# Utility functions
# =========================================================

def safe_text(value, fallback="Not available"):
    """Return clean string data for PDF rendering."""
    if value is None:
        return fallback

    text = str(value).strip()
    return text if text else fallback


def get_score_color(score):
    """Return a progress color based on the score."""
    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        numeric_score = 0

    if numeric_score >= 70:
        return SUCCESS
    if numeric_score >= 45:
        return PRIMARY_LIGHT
    return WARNING


def get_level_badge_colors(level):
    """Return badge background and text colors."""
    level = safe_text(level, "").lower()

    if level == "high":
        return LIGHT_GREEN, SUCCESS
    if level == "low":
        return LIGHT_ORANGE, WARNING
    return LIGHT_BLUE, PRIMARY


def build_styles():
    """Create all report styles."""
    sample_styles = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=sample_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.white,
            spaceAfter=2,
        ),

        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=sample_styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=HexColor("#DBEAFE"),
        ),

        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=sample_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            textColor=PRIMARY,
        ),

        "card_title": ParagraphStyle(
            "CardTitle",
            parent=sample_styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=PRIMARY,
            spaceAfter=2,
        ),

        "career_title": ParagraphStyle(
            "CareerTitle",
            parent=sample_styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=PRIMARY,
        ),

        "body": ParagraphStyle(
            "Body",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=TEXT_DARK,
        ),

        "small": ParagraphStyle(
            "Small",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=TEXT_MUTED,
        ),

        "label": ParagraphStyle(
            "Label",
            parent=sample_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=TEXT_MUTED,
        ),

        "score": ParagraphStyle(
            "Score",
            parent=sample_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=TEXT_DARK,
        ),

        "personality_name": ParagraphStyle(
            "PersonalityName",
            parent=sample_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=PRIMARY,
            spaceAfter=3,
        ),

        "badge": ParagraphStyle(
            "Badge",
            parent=sample_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            alignment=TA_CENTER,
        ),

        "footer": ParagraphStyle(
            "Footer",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            alignment=TA_CENTER,
            textColor=TEXT_MUTED,
        ),
    }

    return styles


def section_heading(title, styles):
    """Create a professional section heading."""
    heading = Table(
        [[Paragraph(title, styles["section_title"])]],
        colWidths=[180 * mm],
    )

    heading.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    return heading


def bullet_paragraph(text, styles):
    """Create a clean bullet paragraph."""
    return Paragraph(
        f'<font color="#2563EB">•</font>&nbsp;&nbsp;{safe_text(text)}',
        styles["body"],
    )


# =========================================================
# Header and footer
# =========================================================

def draw_page_footer(canvas, document):
    """Draw footer and page number on every page."""
    canvas.saveState()
    page_width, _ = A4

    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(
        document.leftMargin,
        12 * mm,
        page_width - document.rightMargin,
        12 * mm,
    )

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(TEXT_MUTED)

    canvas.drawString(
        document.leftMargin,
        7 * mm,
        "AI Adaptive Personality Assessment System",
    )

    canvas.drawRightString(
        page_width - document.rightMargin,
        7 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


def build_report_header(username, report_date, result_id, styles):
    """Build the main report header."""
    title = Paragraph(
        "AI Personality Assessment Report",
        styles["title"],
    )

    subtitle = Paragraph(
        "OCEAN Personality Profile, AI Analysis and Career Insights",
        styles["subtitle"],
    )

    title_block = Table(
        [[title], [subtitle]],
        colWidths=[180 * mm],
    )

    title_block.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
            ("TOPPADDING", (0, 1), (-1, 1), 0),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
        ])
    )

    information = [
        [
            Paragraph("USER", styles["label"]),
            Paragraph("REPORT DATE", styles["label"]),
            Paragraph("REPORT ID", styles["label"]),
        ],
        [
            Paragraph(safe_text(username), styles["score"]),
            Paragraph(safe_text(report_date), styles["score"]),
            Paragraph(f"PA-{result_id:05d}", styles["score"]),
        ],
    ]

    information_table = Table(
        information,
        colWidths=[60 * mm, 60 * mm, 60 * mm],
    )

    information_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
            ("TOPPADDING", (0, 1), (-1, 1), 1),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    return [title_block, Spacer(1, 3 * mm), information_table]


# =========================================================
# Personality sections
# =========================================================

def build_personality_summary(
    personality_type,
    personality_summary,
    personality_details,
    styles,
):
    """Build the AI personality summary card."""
    summary_card = Table(
        [[
            Paragraph(
                "AI PERSONALITY TYPE",
                styles["label"],
            ),
        ], [
            Paragraph(
                safe_text(personality_type),
                styles["personality_name"],
            ),
        ], [
            Paragraph(
                safe_text(personality_summary),
                styles["body"],
            ),
        ]],
        colWidths=[180 * mm],
    )

    summary_card.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
            ("BOX", (0, 0), (-1, -1), 0.7, HexColor("#DDD6FE")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
            ("TOPPADDING", (0, 1), (-1, 1), 1),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 2),
            ("TOPPADDING", (0, 2), (-1, 2), 2),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 8),
        ])
    )

    environment_items = personality_details.get("environments", [])
    domain_items = personality_details.get("domains", [])

    environment_content = [
        Paragraph("BEST WORK ENVIRONMENT", styles["card_title"]),
    ]

    if environment_items:
        environment_content.extend(
            bullet_paragraph(item, styles)
            for item in environment_items[:4]
        )
    else:
        environment_content.append(
            Paragraph("Work environment information is not available.", styles["body"])
        )

    domain_content = [
        Paragraph("RECOMMENDED DOMAINS", styles["card_title"]),
    ]

    if domain_items:
        domain_content.extend(
            bullet_paragraph(item, styles)
            for item in domain_items[:4]
        )
    else:
        domain_content.append(
            Paragraph("Career domain information is not available.", styles["body"])
        )

    details_table = Table(
        [[environment_content, domain_content]],
        colWidths=[88 * mm, 88 * mm],
        hAlign="LEFT",
    )

    details_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), LIGHT_BLUE),
            ("BACKGROUND", (1, 0), (1, 0), LIGHT_GREEN),
            ("BOX", (0, 0), (0, 0), 0.6, BORDER),
            ("BOX", (1, 0), (1, 0), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    return [
        summary_card,
        Spacer(1, 2.5 * mm),
        details_table,
    ]


def build_ocean_scores(result, styles):
    """Create score cards and progress bars."""
    scores = [
        ("Openness", result.openness),
        ("Conscientiousness", result.conscientiousness),
        ("Extraversion", result.extraversion),
        ("Agreeableness", result.agreeableness),
        ("Neuroticism", result.neuroticism),
    ]

    rows = []

    for trait, score in scores:
        score_color = get_score_color(score)

        label = Paragraph(trait, styles["score"])

        value = Paragraph(
            f"{float(score):.2f}%",
            ParagraphStyle(
                f"{trait}Value",
                parent=styles["score"],
                alignment=TA_LEFT,
                textColor=score_color,
            ),
        )

        progress = ScoreProgressBar(
            score,
            width=105 * mm,
            height=4.5 * mm,
            bar_color=score_color,
        )

        rows.append([label, value, progress])

    score_table = Table(
        rows,
        colWidths=[38 * mm, 22 * mm, 120 * mm],
        rowHeights=[9 * mm] * len(rows),
    )

    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    return score_table


def build_strengths_growth(strengths, improvements, styles):
    """Build strengths and growth areas cards."""
    strength_content = [
        Paragraph("TOP STRENGTHS", styles["card_title"]),
    ]

    if strengths:
        strength_content.extend(
            bullet_paragraph(item, styles)
            for item in strengths[:5]
        )
    else:
        strength_content.append(
            Paragraph("No strengths information available.", styles["body"])
        )

    improvement_content = [
        Paragraph("GROWTH AREAS", styles["card_title"]),
    ]

    if improvements:
        improvement_content.extend(
            bullet_paragraph(item, styles)
            for item in improvements[:5]
        )
    else:
        improvement_content.append(
            Paragraph("No improvement information available.", styles["body"])
        )

    table = Table(
        [[strength_content, improvement_content]],
        colWidths=[88 * mm, 88 * mm],
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), LIGHT_GREEN),
            ("BACKGROUND", (1, 0), (1, 0), LIGHT_ORANGE),
            ("BOX", (0, 0), (0, 0), 0.6, BORDER),
            ("BOX", (1, 0), (1, 0), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    return table


def build_personality_analysis(personality_analysis, styles):
    """Build detailed trait-analysis cards."""
    cards = []

    for item in personality_analysis:
        badge_background, badge_text = get_level_badge_colors(item.get("level"))

        title = Paragraph(
            safe_text(item.get("trait")),
            styles["card_title"],
        )

        badge_style = ParagraphStyle(
            f"Badge{safe_text(item.get('trait'))}",
            parent=styles["badge"],
            textColor=badge_text,
        )

        badge = Table(
            [[Paragraph(
                f"{safe_text(item.get('level'))} - {float(item.get('score', 0)):.2f}%",
                badge_style,
            )]],
            colWidths=[34 * mm],
        )

        badge.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), badge_background),
                ("BOX", (0, 0), (-1, -1), 0.4, badge_text),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ])
        )

        header = Table(
            [[title, badge]],
            colWidths=[134 * mm, 36 * mm],
        )

        header.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ])
        )

        description = Paragraph(
            safe_text(item.get("description")),
            styles["body"],
        )

        card = Table(
            [[header], [description]],
            colWidths=[174 * mm],
        )

        card.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), CARD_BACKGROUND),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 1),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
            ])
        )

        cards.extend([
            KeepTogether(card),
            Spacer(1, 2 * mm),
        ])

    return cards


# =========================================================
# Career section
# =========================================================

def build_skill_tags(skills, styles):
    """Build readable skill-tag rows."""
    if isinstance(skills, str):
        skill_list = [
            skill.strip()
            for skill in skills.split(",")
            if skill.strip()
        ]
    else:
        skill_list = list(skills or [])

    if not skill_list:
        return Paragraph("Skills not specified.", styles["small"])

    tags = []

    for skill in skill_list[:8]:
        tags.append(
            Table(
                [[Paragraph(
                    safe_text(skill),
                    ParagraphStyle(
                        f"Skill{safe_text(skill)}",
                        parent=styles["small"],
                        textColor=PRIMARY,
                        alignment=TA_CENTER,
                    ),
                )]],
                colWidths=[None],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                ]),
            )
        )

    first_row = tags[:4]
    second_row = tags[4:8]

    while len(first_row) < 4:
        first_row.append("")

    rows = [first_row]

    if second_row:
        while len(second_row) < 4:
            second_row.append("")
        rows.append(second_row)

    tags_table = Table(
        rows,
        colWidths=[40 * mm] * 4,
        hAlign="LEFT",
    )

    tags_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ])
    )

    return tags_table


def build_career_card(career, index, styles):
    """Build one compact professional career recommendation card."""
    title = safe_text(career.get("title"))

    try:
        score = float(career.get("final_score", 0))
    except (TypeError, ValueError):
        score = 0

    category = safe_text(career.get("category"))
    description = safe_text(career.get("description"))
    skills = career.get("skills", "")
    reasons = career.get("reasons") or []
    warnings = career.get("warnings") or []
    roadmap = career.get("roadmap") or []

    rank_circle = Table(
        [[Paragraph(
            f"#{index}",
            ParagraphStyle(
                f"Rank{index}",
                parent=styles["score"],
                alignment=TA_CENTER,
                textColor=colors.white,
            ),
        )]],
        colWidths=[9 * mm],
        rowHeights=[9 * mm],
    )

    rank_circle.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_LIGHT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )

    career_heading = Paragraph(
        f"{title}<br/><font size='7.5' color='#64748B'>{category}</font>",
        styles["career_title"],
    )

    match_badge = Table(
        [[Paragraph(
            f"{score:.1f}% MATCH",
            ParagraphStyle(
                f"Match{index}",
                parent=styles["badge"],
                textColor=SUCCESS,
            ),
        )]],
        colWidths=[30 * mm],
    )

    match_badge.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREEN),
            ("BOX", (0, 0), (-1, -1), 0.5, SUCCESS),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )

    card_header = Table(
        [[rank_circle, career_heading, match_badge]],
        colWidths=[12 * mm, 124 * mm, 34 * mm],
    )

    card_header.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ])
    )

    # Reasons content
    reasons_content = [Paragraph("WHY RECOMMENDED", styles["card_title"])]
    if reasons:
        reasons_content.extend(bullet_paragraph(r, styles) for r in reasons[:2])
    else:
        reasons_content.append(Paragraph("Personality profile aligns with this career.", styles["body"]))

    # Roadmap content
    roadmap_content = [Paragraph("LEARNING ROADMAP", styles["card_title"])]
    if roadmap:
        for step_idx, step in enumerate(roadmap[:2], start=1):
            roadmap_content.append(
                Paragraph(f'<font color="#2563EB"><b>{step_idx}.</b></font>&nbsp;&nbsp;{safe_text(step)}', styles["body"])
            )
    else:
        roadmap_content.append(Paragraph("Focus on core domain skills.", styles["body"]))

    two_col_details = Table(
        [[reasons_content, roadmap_content]],
        colWidths=[83 * mm, 83 * mm],
    )

    two_col_details.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), LIGHT_BLUE),
            ("BACKGROUND", (1, 0), (1, 0), LIGHT_PURPLE),
            ("BOX", (0, 0), (0, 0), 0.5, BORDER),
            ("BOX", (1, 0), (1, 0), 0.5, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    content = [
        card_header,
        Spacer(1, 1.5 * mm),
        Paragraph(description, styles["body"]),
        Spacer(1, 1.5 * mm),
        Paragraph("<b>Recommended Skills:</b>", styles["small"]),
        Spacer(1, 1 * mm),
        build_skill_tags(skills, styles),
        Spacer(1, 1.5 * mm),
        ScoreProgressBar(
            score,
            width=166 * mm,
            height=4 * mm,
            bar_color=get_score_color(score),
        ),
        Spacer(1, 2 * mm),
        two_col_details,
    ]

    if warnings:
        warning_text = safe_text(warnings[0])

        warning_card = Table(
            [[Paragraph(
                f"<b>Growth consideration:</b> {warning_text}",
                styles["small"],
            )]],
            colWidths=[166 * mm],
        )

        warning_card.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ORANGE),
                ("BOX", (0, 0), (-1, -1), 0.4, HexColor("#FED7AA")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )

        content.extend([
            Spacer(1, 1.5 * mm),
            warning_card,
        ])

    card = Table(
        [[content]],
        colWidths=[174 * mm],
    )

    card.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD_BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    return KeepTogether(card)


# =========================================================
# Main download view
# =========================================================

def download_report(request, result_id):
    """
    Generate and download a compact, highly professional personality assessment report.
    """

    result = get_object_or_404(
        AssessmentResult.objects.select_related(
            "session",
            "session__user",
        ),
        id=result_id,
        session__user=request.user,
    )

    careers = get_recommended_careers(
        result,
        top_n=5,
    )

    personality_analysis = get_personality_analysis(result)

    personality_type, personality_summary = (
        generate_personality_type(result)
    )

    personality_details = generate_personality_details(result)
    strengths = generate_strengths(result)
    improvements = generate_improvements(result)

    username = result.session.user.username
    report_date = result.created_at.strftime("%d %B %Y")

    response = HttpResponse(
        content_type="application/pdf",
    )

    filename = (
        f"AI_Personality_Report_"
        f"{username}_"
        f"{result.created_at.strftime('%Y%m%d')}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    document = SimpleDocTemplate(
        response,  # type: ignore
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=10 * mm,
        bottomMargin=18 * mm,
        title="AI Personality Assessment Report",
        author="AI Adaptive Personality Assessment System",
        subject="OCEAN Personality and Career Recommendation Report",
    )

    styles = build_styles()
    story = []

    # Header
    story.extend(
        build_report_header(
            username=username,
            report_date=report_date,
            result_id=result.id,
            styles=styles,
        )
    )

    story.append(Spacer(1, 3.5 * mm))

    # Personality summary
    story.append(
        section_heading(
            "PERSONALITY PROFILE",
            styles,
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.extend(
        build_personality_summary(
            personality_type=personality_type,
            personality_summary=personality_summary,
            personality_details=personality_details,
            styles=styles,
        )
    )

    story.append(Spacer(1, 3.5 * mm))

    # OCEAN score section
    story.append(
        section_heading(
            "OCEAN PERSONALITY SCORES",
            styles,
        )
    )

    story.append(Spacer(1, 2 * mm))
    story.append(build_ocean_scores(result, styles))

    story.append(Spacer(1, 3.5 * mm))

    # Strengths and Growth Areas
    story.append(CondPageBreak(40 * mm))

    story.append(
        section_heading(
            "STRENGTHS AND DEVELOPMENT AREAS",
            styles,
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.append(
        build_strengths_growth(
            strengths,
            improvements,
            styles,
        )
    )

    story.append(Spacer(1, 3.5 * mm))

    # Detailed Analysis
    story.append(CondPageBreak(45 * mm))

    story.append(
        section_heading(
            "DETAILED PERSONALITY ANALYSIS",
            styles,
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.extend(
        build_personality_analysis(
            personality_analysis,
            styles,
        )
    )

    story.append(Spacer(1, 3.5 * mm))

    # Top 5 AI Career Recommendations
    story.append(CondPageBreak(55 * mm))

    story.append(
        section_heading(
            "TOP 5 AI CAREER RECOMMENDATIONS",
            styles,
        )
    )

    story.append(Spacer(1, 3 * mm))

    if careers:
        for index, career in enumerate(
            careers[:5],
            start=1,
        ):
            story.append(
                build_career_card(
                    career,
                    index,
                    styles,
                )
            )

            story.append(Spacer(1, 3 * mm))

    else:
        no_career_card = Table(
            [[Paragraph(
                "No career recommendations are currently available for this assessment.",
                styles["body"],
            )]],
            colWidths=[174 * mm],
        )

        no_career_card.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ORANGE),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )

        story.append(no_career_card)

    story.append(Spacer(1, 3 * mm))

    # Closing note
    closing_note = Table(
        [[Paragraph(
            (
                "<b>Important:</b> This AI-generated report is designed "
                "to support self-awareness and career exploration. "
                "It should be considered alongside personal interests, "
                "education, experience and professional guidance."
            ),
            styles["small"],
        )]],
        colWidths=[174 * mm],
    )

    closing_note.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BACKGROUND),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(KeepTogether(closing_note))

    document.build(
        story,
        onFirstPage=draw_page_footer,
        onLaterPages=draw_page_footer,
    )

    return response