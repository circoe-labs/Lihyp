"""Contracts for the approved screens, not just cosmetic CSS snapshots."""
from pathlib import Path
from html.parser import HTMLParser

UI=Path(__file__).resolve().parents[1]/'src/simco2/ui'

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[];self.forms=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag=='button' and attrs.get('id')=='scenario-submit':
            self.forms.append((attrs.get('form'),attrs.get('type')))


def test_comparison_is_one_right_pane_and_submits_the_left_form():
    html=(UI/'index.html').read_text(encoding='utf-8')
    js=(UI/'app.js').read_text(encoding='utf-8')
    structure=Structure();structure.feed(html)
    assert len(structure.ids)==len(set(structure.ids)), 'Duplicate IDs break event targeting'
    assert structure.forms==[('scenario-form','submit')]
    assert '<div class="simulator-side ux-sim-side">' in html
    for target in ('ux-route-distance','ux-route-time','ux-route-station','ux-route-detour','ux-route-trips',
                   'comparison-results','comparison-timeline','ux-timeline-vehicle','ux-timeline-content'):
        assert target in html or target in js
    assert 'scheduleTiles(comparison)' not in js, 'No duplicate stack of results cards'
    assert 'ux-day-timeline' in js
    assert 'result.status' in js, 'Status must come from the backend, not demo UI'


def test_vehicle_library_and_registered_catalogue_use_exclusive_tabs():
    html=(UI/'index.html').read_text(encoding='utf-8')
    js=(UI/'app.js').read_text(encoding='utf-8')
    css=(UI/'style.css').read_text(encoding='utf-8')
    assert html.count('id="reference-library"')==1
    assert html.count('id="vehicle-table"')==1
    assert html.count('id="vehicle-form"')==1
    assert 'id="ux-tab-library"' in html and 'id="ux-tab-registered"' in html
    assert 'data-view-reference' in js and 'data-view-vehicle' in js
    assert "classList.toggle('hidden',!library)" in js
    assert "classList.toggle('hidden',library)" in js
    assert 'getBoundingClientRect' not in js, 'No JS-driven floating content clones'
    assert '.ux-vehicle-workspace{display:grid' in css
    assert 'overflow:hidden!important' in css, 'Map tiles must be clipped'
