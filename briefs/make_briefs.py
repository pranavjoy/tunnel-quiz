#!/usr/bin/env python3
"""Generate the two Tunnel Quiz briefs as branded PDFs."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer)

ORANGE = HexColor('#EA6F1C')
CREAM = HexColor('#EBE7C8')
GREEN = HexColor('#103B32')
BROWN = HexColor('#3B2A1F')
BLACK = HexColor('#131313')

W, H = A4

def draw_arch(c, x, y, w, color):
    """Brand arch mark, legs down, at (x, y) = bottom-left, width w."""
    h = w * 0.78
    t = w * 0.30          # stroke thickness
    r_out = w / 2
    r_in = (w - 2 * t) / 2
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x, y + h - r_out)
    p.arcTo(x, y + h - 2 * r_out, x + 2 * r_out, y + h, startAng=180, extent=-180)
    p.lineTo(x + w, y)
    p.lineTo(x + w - t, y)
    p.lineTo(x + w - t, y + h - r_out)
    p.arcTo(x + t, y + h - t - 2 * r_in, x + w - t, y + h - t,
            startAng=0, extent=180)
    p.lineTo(x + t, y)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, stroke=0, fill=1)

def page_decor(title):
    def _draw(c, doc):
        c.saveState()
        # cream page
        c.setFillColor(CREAM)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        # orange header band
        band_h = 34 * mm
        c.setFillColor(ORANGE)
        c.rect(0, H - band_h, W, band_h, stroke=0, fill=1)
        draw_arch(c, 18 * mm, H - band_h + 9 * mm, 13 * mm, CREAM)
        c.setFillColor(BLACK)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(38 * mm, H - band_h + 17 * mm, 'THE TUNNEL QUIZ')
        c.setFont('Helvetica-Bold', 11)
        c.drawString(38 * mm, H - band_h + 9.5 * mm, title.upper())
        # green footer band
        foot_h = 12 * mm
        c.setFillColor(GREEN)
        c.rect(0, 0, W, foot_h, stroke=0, fill=1)
        c.setFillColor(CREAM)
        c.setFont('Helvetica-Bold', 8.5)
        c.drawCentredString(W / 2, 4.6 * mm,
            'THE TUNNEL & CO.  ·  BILDERDIJKSTRAAT 186, AMSTERDAM  ·  EVERY SECOND WEDNESDAY  ·  19:30')
        c.restoreState()
    return _draw

def styles():
    h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=12.5,
                       leading=15, textColor=ORANGE, spaceBefore=11,
                       spaceAfter=4)
    body = ParagraphStyle('b', fontName='Helvetica', fontSize=10,
                          leading=14.5, textColor=BROWN)
    bullet = ParagraphStyle('bl', parent=body, leftIndent=6 * mm,
                            bulletIndent=1.5 * mm, spaceAfter=2.5)
    lead = ParagraphStyle('lead', parent=body, fontSize=11, leading=16,
                          textColor=BLACK)
    return h, body, bullet, lead

def build(filename, title, story_fn):
    doc = BaseDocTemplate(filename, pagesize=A4,
                          leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=42 * mm, bottomMargin=18 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id='main')
    doc.addPageTemplates([PageTemplate(id='p', frames=[frame],
                                       onPage=page_decor(title))])
    doc.build(story_fn())

H_, B_, BL_, LEAD_ = styles()
def hd(t): return Paragraph(t, H_)
def p(t): return Paragraph(t, B_)
def b(t): return Paragraph(t, BL_, bulletText='\u2013')
def lead(t): return Paragraph(t, LEAD_)
def gap(n=4): return Spacer(1, n)

# ---------------------------------------------------------------- bar brief
def bar_story():
    s = []
    s.append(lead('A biweekly pub quiz at The Tunnel &amp; Co., hosted by Pranav, '
                  'every second Wednesday at 19:30. Entry is \u20ac3 per person, '
                  'or \u20ac15 for a full table of six. Teams of two to six, three '
                  'rounds plus a rolling jackpot round. Built to fill the bar and '
                  'give people a reason to come back every other week.'))
    s.append(hd('The format'))
    s.append(b('Three rounds of eight questions each, then the jackpot round. '
               'The jackpot starts at \u20ac30 and rolls over until won.'))
    s.append(b('Runs 19:30 to roughly 21:45. Teams stay for the full evening.'))
    s.append(b("The hook: <b>Tonight's Special</b>. Every edition features a "
               'different guest co-host playing a comedic character for the night, '
               'drawn from the Amsterdam comedy scene. Each night stands alone, so '
               'first-timers are never behind, and regulars get a new show every '
               'time.'))
    s.append(hd('What the bar gets'))
    s.append(b('Predictable midweek traffic: booked tables of 2 to 6, every other '
               'Wednesday.'))
    s.append(b('A booking system is already live-ready: guests reserve on the quiz '
               'website, get an email confirmation, and nights are capped so the '
               'room never oversells. You get the guest list per edition.'))
    s.append(b('Fresh promotion every two weeks: a new Special means a new poster, '
               'a new chalkboard, and new social content, all in the house brand '
               '(site, posters, and an Instagram identity are already designed to '
               'the 2026 guidelines).'))
    s.append(b('Entry sales cover the winner\u2019s prize; the bar\u2019s upside '
               'is drink sales from full tables over a two-hour sitting.'))
    s.append(hd('What we need from the bar'))
    s.append(b('The room, PA and a microphone from 18:45; quiz area reserved '
               'until 19:25 for booked teams.'))
    s.append(b('The chalkboard A-frame outside for the Tonight\u2019s Special '
               'billing on quiz days.'))
    s.append(b('Winner\u2019s prize: one drink per team member for the winning '
               'team, with the cost covered from the entry sales.'))
    s.append(b('A home for the jackpot float and a named contact for quiz nights. '
               'How the jackpot is held and topped up: to agree together.'))
    s.append(gap(8))
    s.append(p('Contact: Pranav.'))
    return s

# --------------------------------------------------------- performer brief
def performer_story():
    s = []
    s.append(lead('The Tunnel Quiz is a biweekly pub quiz in Amsterdam West with '
                  'a double-act twist: every edition features one guest co-host, '
                  'billed as <b>Tonight\u2019s Special</b>, playing a character of '
                  'their own invention for the night. This brief is everything '
                  'you need. Prep should take you under an hour.'))
    s.append(hd('The premise'))
    s.append(b('You are the Special: a character on the menu for one night only. '
               'Example billing: "Quizantha Williams: Candle Maker '
               'Extraordinaire".'))
    s.append(b('Every night stands alone. No lore, no continuity, no watching '
               'previous editions. You inherit nothing and owe nothing.'))
    s.append(b('The host (Pranav) plays it straight and runs the actual quiz. '
               'You are his problem for the evening.'))
    s.append(hd('The frame: three fixed beats, the rest is yours'))
    s.append(b('<b>The Entrance.</b> You get a music cue and a menu-style '
               'introduction ("Every quiz needs a host. Ours comes with a '
               'side..."). Arrive in character.'))
    s.append(b('<b>The Slot.</b> You own one segment of the night: run one round '
               'your way, or guard the jackpot round and take the attempts on it '
               'personally. Your choice, agreed in advance.'))
    s.append(b('<b>The Verdict.</b> A short closing bit before final scores: '
               'your character\u2019s ruling on the evening.'))
    s.append(p('Everything inside those beats is your playground. Total mic time '
               'is roughly 15 to 20 minutes across the night.'))
    s.append(hd('Rules of the road'))
    s.append(b('The quiz wins ties. If a bit and the game collide, the game goes '
               'first; there is always another gap two minutes later.'))
    s.append(b('Punch at the host, not the teams. The teams are paying '
               'customers; the host signed up for this.'))
    s.append(b('Bar-friendly material: it is a mixed room of teams, not a late '
               'club spot.'))
    s.append(hd('What we need from you, and when'))
    s.append(b('By the Friday before: your character\u2019s name plus one '
               'menu-style description line. It goes on the poster, the '
               'chalkboard, and Instagram.'))
    s.append(b('Optional but recommended: a 20-minute coffee with Pranav to walk '
               'the three beats.'))
    s.append(hd('Logistics'))
    s.append(b('The Tunnel &amp; Co., Bilderdijkstraat 186, Amsterdam. Arrive '
               '18:45. Quiz runs 19:30 to roughly 21:45.'))
    s.append(b('Drinks arrangement is confirmed per night before you say yes.'))
    s.append(gap(8))
    s.append(p('<b>In short:</b> one night, one character, three beats, a seated '
               'and mildly competitive audience, and a straight man to work '
               'against. Bring someone strange.'))
    return s

build('/home/claude/tunnel-quiz/briefs/tunnel-quiz-bar-brief.pdf',
      'Concept brief for The Tunnel & Co.', bar_story)
build('/home/claude/tunnel-quiz/briefs/tunnel-quiz-performer-brief.pdf',
      "Tonight's Special: performer brief", performer_story)
print('built')
