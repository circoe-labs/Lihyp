"""PDF de diagnostic issu exclusivement d'un RunResult persistant."""
from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether


FONT = "Helvetica"
BOLD = "Helvetica-Bold"
FONT_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD_FILE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if FONT_FILE.exists() and BOLD_FILE.exists():
    pdfmetrics.registerFont(TTFont("SimSans", str(FONT_FILE)))
    pdfmetrics.registerFont(TTFont("SimSansBold", str(BOLD_FILE)))
    pdfmetrics.registerFontFamily("SimSans", normal="SimSans", bold="SimSansBold")
    FONT, BOLD = "SimSans", "SimSansBold"


def render_pdf(run: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=18*mm,
                            leftMargin=18*mm, topMargin=20*mm, bottomMargin=18*mm,
                            title="Étude transport voyageurs - Simulation",
                            author="SimCO2 - prototype")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SimTitle", fontName=BOLD, fontSize=17, leading=22,
                              textColor=colors.HexColor("#16354d"), spaceAfter=13))
    styles.add(ParagraphStyle(name="SimSub", fontName=BOLD, fontSize=10, leading=14,
                              textColor=colors.HexColor("#16354d"), spaceBefore=15, spaceAfter=7))
    styles.add(ParagraphStyle(name="SimBody", fontName=FONT, fontSize=8.7, leading=13,
                              spaceAfter=5))
    styles.add(ParagraphStyle(name="SimSmall", fontName=FONT, fontSize=7.2, leading=10,
                              textColor=colors.HexColor("#475467")))
    styles.add(ParagraphStyle(name="SimWarn", fontName=FONT, fontSize=8.3, leading=12,
                              textColor=colors.HexColor("#7c3c12"), spaceAfter=6))
    styles.add(ParagraphStyle(name="SimCell", fontName=FONT, fontSize=8, leading=11))

    def P(s, style="SimBody"):
        return Paragraph(escape(str(s)), styles[style])

    def grid(data, widths, *, header=False):
        table = Table([[P(v, "SimCell") for v in row] for row in data],
                      colWidths=widths, hAlign="LEFT", repeatRows=1 if header else 0)
        ops = [
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LINEBELOW", (0,0), (-1,-1), .35, colors.HexColor("#dde4eb")),
        ]
        if header:
            ops.extend([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eff4f7")),
                        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#16354d"))])
        table.setStyle(TableStyle(ops))
        return table

    snap = run["snapshot"]
    scenario = snap["scenario"]
    result = run["result"]
    story = [P("Simulation transport voyageurs | TCO & CO₂e", "SimTitle"),
             P("RAPPORT DE PROTOTYPE — Données et modes non homologués.", "SimWarn"),
             P(f"Scénario : {scenario['name']}"),
             P(f"Exécution : {run['id']}"),
             P(f"Date : {run['created_at']} | moteur : {snap['solver_version']}"),
             P(f"Périmètre : {scenario['country_iso']} / {scenario['timezone']} | "
               f"{scenario['start_date']} au {scenario['end_date']}"),
             P(f"Entrée figée (SHA-256) : {run['snapshot_sha256']}", "SimSmall"),
             P("Résultat et indicateurs", "SimSub"),
             P(f"Statut : {result['status']}. L'optimalité générale n'est pas prouvée."),
             ]
    totals = result.get("totals")
    if totals:
        data = [
            ["Voyageurs servis / demandés",
             f"{totals['passengers_served']} / {totals['passengers_requested']}"],
            ["Véhicules utilisés / courses", f"{totals['vehicles_used']} / {totals['trips']}"],
            ["Kilomètres en charge", f"{totals['distance_passenger_m']} m"],
            ["Kilomètres à vide", f"{totals['distance_empty_m']} m"],
            ["Énergie consommée", f"{totals['energy_consumed']} {totals['energy_unit']}"],
            ["Coût TCO du périmètre retenu", f"{totals['eur_total']} EUR"],
            ["Coût par voyageur", str(totals['eur_per_passenger'] or "non applicable") + " EUR"],
            ["CO2e du périmètre retenu", f"{totals['kgco2e_total']} kgCO2e"],
            ["CO2e passager-km", str(totals["gco2e_per_passenger_km"] or "non applicable") + " gCO2e/p.km"],
        ]
        story.append(grid(data, [260, 232]))
        story.append(P("Périmètres et ventilation", "SimSub"))
        scope = result["scope"]
        story.append(P(f"TCO : {scope['tco']}; CO2e : {scope['emissions']}; "
                       f"conso : {scope['consumption']}; planning : {scope['schedule']}"))
        breakdown = result["cost_breakdown"]
        story.append(grid([[key, str(val) + " EUR"] for key, val in breakdown.items()],
                          [260, 232]))
        trips = result["trips"]
        header = ["Course", "Véhicule", "Pax", "Départ (UTC)", "Arrivée (UTC)"]
        records = [header]
        for t in trips:
            records.append([t["trip_id"], t["vehicle_instance"], str(t["passengers"]),
                            t["depart_utc"], t["arrive_utc"]])
        story.append(KeepTogether([P("Courses calculées", "SimSub"),
                                   grid(records, [62, 66, 41, 161, 162], header=True)]))
    else:
        issues = result.get("constraints", [])
        for issue in issues:
            story.append(P(f"{issue.get('code', 'diagnostic')} : {issue.get('message', '')}", "SimWarn"))
        story.append(P("Aucun montant ni émission calculé en absence de solution valide."))

    story.append(P("Sources et fiabilité", "SimSub"))
    route = scenario["route"]
    energy = snap["energy_version"]
    vehicle = snap["vehicle_version"]
    story.append(P(f"Route : {route['origin']} vers {route['destination']} ; "
                   f"distance/durée fournies par : {route['source']}."))
    story.append(P(f"Énergie v{energy['revision']} [{energy['id']}] ; "
                   f"source : {energy['payload']['source']} ; "
                   f"date source : {energy['payload']['source_date']} ; "
                   f"qualité : {energy['payload'].get('quality', 'inconnue')}"))
    story.append(P(f"Véhicule v{vehicle['revision']} [{vehicle['id']}] ; "
                   f"source : {vehicle['payload']['source']}"))
    story.append(P("Avertissements et limites", "SimSub"))
    warnings = result.get("warnings") or [
        "Le périmètre métier complet n'est pas simulé : voir diagnostics et spécifications ouvertes."]
    for warning in warnings:
        story.append(P("• " + warning, "SimWarn"))
    story.append(Spacer(1, 6*mm))
    story.append(P("Rapport généré depuis une exécution enregistrée ; les référentiels "
                   "courants ne modifient pas ces chiffres.", "SimSmall"))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT, 7)
        canvas.setFillColor(colors.HexColor("#657687"))
        canvas.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm)
        canvas.drawString(18*mm, 10*mm, "SimCO2 — Rapport de prototype non certifié")
        canvas.drawRightString(A4[0]-18*mm, 10*mm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
