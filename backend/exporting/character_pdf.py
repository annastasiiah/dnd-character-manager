
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_character_pdf(character: dict) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph(
            escape(character["name"]),
            styles["Title"],
        )
    )
    content.append(Spacer(1, 8 * mm))

    details = [
        ["Level", str(character["level"])],
        ["Race", character["race"]],
        ["Class", character["character_class"]],
        ["Background", character["background"]],
    ]

    content.append(Table(details, colWidths=[45 * mm, 100 * mm]))
    content.append(Spacer(1, 8 * mm))
    content.append(Paragraph("Ability Scores", styles["Heading2"]))

    abilities = [
        ["Strength", "Dexterity", "Constitution"],
        [
            str(character["strength"]),
            str(character["dexterity"]),
            str(character["constitution"]),
        ],
        ["Intelligence", "Wisdom", "Charisma"],
        [
            str(character["intelligence"]),
            str(character["wisdom"]),
            str(character["charisma"]),
        ],
    ]

    table = Table(abilities, colWidths=[48 * mm] * 3)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8DDF5")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#E8DDF5")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#352744")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    content.append(table)

    content.append(Spacer(1, 8 * mm))
    content.append(Paragraph("Spells", styles["Heading2"]))

    spells = character.get("spells", [])

    if not spells:
        content.append(
            Paragraph("No spells added.", styles["BodyText"])
        )
    else:
        for spell in spells:
            content.append(
                Paragraph(
                    escape(spell["name"]),
                    styles["Heading3"],
                )
            )

            details = (
                f"Level: {spell['level']} | "
                f"School: {escape(spell['school'])}<br/>"
                f"Casting time: {escape(spell['casting_time'])} | "
                f"Range: {escape(spell['spell_range'])}<br/>"
                f"Duration: {escape(spell['duration'])}<br/>"
                f"{escape(spell['description'])}"
            )

            content.append(
                Paragraph(details, styles["BodyText"])
            )
            content.append(Spacer(1, 4 * mm))
            
    document.build(content)

    return buffer.getvalue()