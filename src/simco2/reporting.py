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


def render_pdf(run: dict, lang: str = "fr") -> bytes:
    if lang not in ("fr", "en"):
        raise ValueError("Unsupported report language")
    en = lang == "en"
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=18*mm,
                            leftMargin=18*mm, topMargin=20*mm, bottomMargin=18*mm,
                            title="Passenger transport simulation" if en else "Étude transport voyageurs - Simulation",
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
    i18n = {
        "title": ("Simulation transport voyageurs | TCO & CO₂e", "Passenger transport simulation | TCO & CO₂e"),
        "disclaimer": ("RAPPORT DE PROTOTYPE - Données et modes non homologués.",
                       "PROTOTYPE REPORT - Data and calculation methods not certified."),
        "scenario": ("Scénario", "Scenario"), "run": ("Exécution", "Run"),
        "date": ("Date", "Date"), "engine": ("moteur", "engine"),
        "scope": ("Périmètre", "Scope"), "to": ("au", "to"),
        "snapshot": ("Entrée figée (SHA-256)", "Frozen input (SHA-256)"),
        "indicators": ("Résultat et indicateurs", "Results and indicators"),
        "status": ("Statut", "Status"),
        "optimality": ("L'optimalité générale n'est pas prouvée.", "Global optimality is not proven."),
        "passengers": ("Voyageurs servis / demandés", "Passengers served / requested"),
        "vehicles": ("Véhicules utilisés / courses", "Vehicles used / trips"),
        "distance": ("Kilomètres en charge", "Passenger-carrying distance"),
        "empty": ("Kilomètres à vide", "Empty distance"),
        "energy": ("Énergie consommée", "Energy consumed"),
        "cost": ("Coût TCO du périmètre retenu", "TCO cost for selected scope"),
        "passenger_cost": ("Coût par voyageur", "Cost per passenger"),
        "emissions": ("CO₂e du périmètre retenu", "CO₂e within selected scope"),
        "emissions_pkm": ("CO₂e passager-km", "CO₂e per passenger-km"),
        "na": ("non applicable", "not applicable"),
        "breakdown": ("Périmètres et ventilation", "Scope and cost breakdown"),
        "consumption": ("conso", "consumption"), "schedule": ("planning", "schedule"),
        "trip": ("Course", "Trip"), "vehicle": ("Véhicule", "Vehicle"),
        "depart": ("Départ (UTC)", "Departure (UTC)"), "arrive": ("Arrivée (UTC)", "Arrival (UTC)"),
        "trips": ("Courses calculées", "Computed trips"),
        "no_solution": ("Aucun montant ni émission calculé en absence de solution valide.",
                        "No costs or emissions computed without a valid solution."),
        "sources": ("Sources et fiabilité", "Sources and reliability"),
        "route": ("Route", "Route"), "towards": ("vers", "to"),
        "source_method": ("distance/durée fournies par", "distance/duration supplied by"),
        "source": ("source", "source"), "source_date": ("date source", "source date"),
        "quality": ("qualité", "quality"), "unknown": ("inconnue", "unknown"),
        "warnings": ("Avertissements et limites", "Warnings and limitations"),
        "fallback_warning": ("Le périmètre métier complet n'est pas simulé : voir diagnostics et spécifications ouvertes.",
                             "The complete business scope is not simulated: see diagnostics and open specifications."),
        "audit": ("Rapport généré depuis une exécution enregistrée ; les référentiels courants ne modifient pas ces chiffres.",
                  "Report generated from a saved run; changes to current reference data do not alter these figures."),
        "footer": ("SimCO2 - Rapport de prototype non certifié", "SimCO2 - Uncertified prototype report"),
        "page": ("Page", "Page"),
    }
    def tr(key):
        return i18n[key][1 if en else 0]
    status_labels = {
        "feasible_not_proven": "Feasible, not proven optimal",
        "infeasible_proven": "Infeasible",
        "invalid_input": "Invalid input",
        "provider_error": "Routing provider error",
    }
    shown_status = status_labels.get(result["status"], result["status"]) if en else result["status"]
    story = [P(tr("title"), "SimTitle"),
             P(tr("disclaimer"), "SimWarn"),
             P(f"{tr('scenario')} : {scenario['name']}"),
             P(f"{tr('run')} : {run['id']}"),
             P(f"{tr('date')} : {run['created_at']} | {tr('engine')} : {snap['solver_version']}"),
             P(f"{tr('scope')} : {scenario['country_iso']} / {scenario['timezone']} | "
               f"{scenario['start_date']} {tr('to')} {scenario['end_date']}"),
             P(f"{tr('snapshot')} : {run['snapshot_sha256']}", "SimSmall"),
             P(tr("indicators"), "SimSub"),
             P(f"{tr('status')} : {shown_status}. {tr('optimality')}"),
             ]
    totals = result.get("totals")
    if totals:
        data = [
            [tr('passengers'), f"{totals['passengers_served']} / {totals['passengers_requested']}"],
            [tr('vehicles'), f"{totals['vehicles_used']} / {totals['trips']}"],
            [tr('distance'), f"{totals['distance_passenger_m']} m"],
            [tr('empty'), f"{totals['distance_empty_m']} m"],
            [tr('energy'), f"{totals['energy_consumed']} {totals['energy_unit']}"],
            [tr('cost'), f"{totals['eur_total']} EUR"],
            [tr('passenger_cost'), str(totals['eur_per_passenger'] or tr('na')) + ' EUR'],
            [tr('emissions'), f"{totals['kgco2e_total']} kgCO2e"],
            [tr('emissions_pkm'), str(totals['gco2e_per_passenger_km'] or tr('na')) + ' gCO2e/p.km'],
        ]
        story.append(grid(data, [260, 232]))
        story.append(P(tr('breakdown'), 'SimSub'))
        scope = result['scope']
        story.append(P(f"TCO : {scope['tco']}; CO₂e : {scope['emissions']}; "
                       f"{tr('consumption')} : {scope['consumption']}; {tr('schedule')} : {scope['schedule']}"))
        breakdown = result['cost_breakdown']
        story.append(grid([[key, str(val) + ' EUR'] for key, val in breakdown.items()], [260, 232]))
        trips = result['trips']
        rows = [[tr('trip'), tr('vehicle'), 'Pax', tr('depart'), tr('arrive')]]
        for trip in trips:
            rows.append([trip['trip_id'], trip['vehicle_instance'], str(trip['passengers']),
                         trip['depart_utc'], trip['arrive_utc']])
        story.append(KeepTogether([P(tr('trips'), 'SimSub'),
                                   grid(rows, [62, 66, 41, 161, 162], header=True)]))
    else:
        for issue in result.get('constraints', []):
            story.append(P(f"{issue.get('code', 'diagnostic')} : {issue.get('message', '')}", 'SimWarn'))
        story.append(P(tr('no_solution')))

    story.append(P(tr('sources'), 'SimSub'))
    route = scenario['route']
    energy = snap['energy_version']
    vehicle = snap['vehicle_version']
    story.append(P(f"{tr('route')} : {route['origin']} {tr('towards')} {route['destination']} ; "
                   f"{tr('source_method')} : {route['source']}"))
    story.append(P(f"{tr('energy')} v{energy['revision']} [{energy['id']}] ; "
                   f"{tr('source')} : {energy['payload']['source']} ; "
                   f"{tr('source_date')} : {energy['payload']['source_date']} ; "
                   f"{tr('quality')} : {energy['payload'].get('quality', tr('unknown'))}"))
    story.append(P(f"{tr('vehicle')} v{vehicle['revision']} [{vehicle['id']}] ; "
                   f"{tr('source')} : {vehicle['payload']['source']}"))
    story.append(P(tr('warnings'), 'SimSub'))
    warnings = result.get('warnings') or [tr('fallback_warning')]
    translations = {
        'PROTOTYPE : monoligne, 1 jour, aucune réutilisation de véhicule.':
            'PROTOTYPE: one route, one day, no vehicle reuse.',
        'Aucun détour, retour dépôt, temps de pause ou recharge pris en charge.':
            'No detours, depot returns, breaks or charging included.',
        "Aucune minimisation du coût n'est prouvée : affectation baseline seulement.":
            'Cost minimization is not proven: baseline assignment only.',
        'Tarifs et facteurs sont des hypothèses non vérifiées ; pas des données nationales officielles.':
            'Energy prices and factors are unverified assumptions, not official national figures.',
        'Données de véhicule non vérifiées.': 'Vehicle data is unverified.',
        'TCO complet limité aux postes saisis, sans coût d’exploitation non paramétré.':
            'Complete TCO is limited to entered costs.',
    }
    for warning in warnings:
        story.append(P('• ' + (translations.get(warning, warning) if en else warning), 'SimWarn'))
    story.append(Spacer(1, 6*mm))
    story.append(P(tr('audit'), 'SimSmall'))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT, 7)
        canvas.setFillColor(colors.HexColor('#657687'))
        canvas.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm)
        canvas.drawString(18*mm, 10*mm, tr('footer'))
        canvas.drawRightString(A4[0]-18*mm, 10*mm, f"{tr('page')} {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
