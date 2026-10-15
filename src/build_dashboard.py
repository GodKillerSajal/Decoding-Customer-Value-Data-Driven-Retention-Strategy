"""
D2C Founder Dashboard — FINAL rebuild using CustomerFeatures table
Fixes all 4 gaps vs. Problem Statement:
  Page 1: Customer Pyramid     (value_tier: Diamond/Gold/Silver/Bronze)
  Page 2: Promo vs. Loyalty    (promo_dependency_score by tier + loyalty flags)
  Page 3: Category Funnel      (avg prev purchases + promo score by category)
  Page 4: Geographic Opportunity (avg spend + promo score by location)
Table: CustomerFeatures  |  34 engineered columns  |  source: customer_features.csv
"""
import json, os, uuid, shutil

BASE  = r"c:\Users\91731\Desktop\Summer Projects IITG\SQL"
RD    = os.path.join(BASE, "dashboard.Report")
W, H  = 1280.0, 720.0

VIS_SCHEMA   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/1.4.0/schema.json"
PAGE_SCHEMA  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
PAGES_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

AGG_SUM = 0; AGG_AVG = 1; AGG_CNT = 4

def uid(): return uuid.uuid4().hex[:20]
def jwrite(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

NAVY  = "#1B3A5C"; TEAL  = "#0E7B72"; AMBER = "#F5A623"
CORAL = "#E74C3C"; GREEN = "#27AE60"; BLUE  = "#3498DB"
GOLD  = "#D4AF37"; SILVER= "#9E9E9E"; BRONZE= "#CD7F32"
DIAM  = "#5B8FCC"; WHITE = "#FFFFFF"; LGRAY = "#DDE5F0"
VIOLET= "#8E44AD"

TABLE = "CustomerFeatures"

# ── Field projection helpers ────────────────────────────────
def proj_col(col, label=None):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": TABLE}},
                                 "Property": col}},
            "queryRef": f"{TABLE}.{col}", "displayName": label or col}

def proj_agg(col, fn, label=None):
    fn_str = {0:"Sum",1:"Average",2:"Min",3:"Max",4:"CountNonNull",5:"Count"}[fn]
    return {"field": {"Aggregation": {
                "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": TABLE}},
                                          "Property": col}},
                "Function": fn}},
            "queryRef": f"{fn_str}({TABLE}[{col}])",
            "displayName": label or f"{fn_str} of {col}"}

def pos(x, y, w, h, z=0, tab=1000):
    return {"x":float(x),"y":float(y),"z":z,
            "height":float(h),"width":float(w),"tabOrder":tab}

# ── Generic visual builder ──────────────────────────────────
def _vis(vtype, position, query_state, objects=None):
    v = {"$schema": VIS_SCHEMA, "name": uid(), "position": position,
         "visual": {"visualType": vtype, "query": {"queryState": query_state}}}
    if objects: v["visual"]["objects"] = objects
    return v

# ── Object presets ──────────────────────────────────────────
def _bg_border(fill=WHITE, radius=8):
    return {
        "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                       "color": {"solid": {"color": fill}},
                                       "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
        "border":     [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                       "color": {"solid": {"color": LGRAY}},
                                       "radius": {"expr": {"Literal": {"Value": f"{radius}D"}}}}}]
    }

def card_obj():
    o = {"labels": [{"properties": {"color": {"solid": {"color": NAVY}},
                                     "fontSize": {"expr": {"Literal": {"Value": "24D"}}},
                                     "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}}}],
         "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                            "color": {"solid": {"color": "#5A6E8A"}},
                                            "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}]}
    o.update(_bg_border())
    return o

def chart_obj(colors=None):
    o = {"dataLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                         "fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}]}
    o.update(_bg_border())
    if colors:
        o["dataColors"] = [{"properties": {"fillColor": {"solid": {"color": c}}}} for c in colors]
    return o

def donut_obj(colors=None):
    palette = colors or [NAVY, TEAL, AMBER, CORAL, BLUE, GREEN]
    o = {"dataColors": [{"properties": {"fillColor": {"solid": {"color": c}}}} for c in palette],
         "dataLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                         "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}]}
    o.update(_bg_border())
    return o

def slicer_obj():
    o = {"data":   [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
         "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}},
                                    "fontColor": {"solid": {"color": NAVY}},
                                    "fontSize":  {"expr": {"Literal": {"Value": "10D"}}}}}]}
    o.update(_bg_border())
    return o

# ── High-level visual factories ─────────────────────────────
def card(position, col, fn, label=None):
    return _vis("card", position, {"Values": {"projections": [proj_agg(col, fn, label)]}}, card_obj())

def bar(position, cat, val_col, val_fn, label=None, horiz=True, colors=None):
    vtype = "clusteredBarChart" if horiz else "clusteredColumnChart"
    qs = {"Category": {"projections": [proj_col(cat)]},
          "Y":        {"projections": [proj_agg(val_col, val_fn, label)]}}
    return _vis(vtype, position, qs, chart_obj(colors))

def donut(position, cat, val_col, val_fn, label=None, colors=None):
    qs = {"Category": {"projections": [proj_col(cat)]},
          "Y":        {"projections": [proj_agg(val_col, val_fn, label)]}}
    return _vis("donutChart", position, qs, donut_obj(colors))

def slicer(position, cat):
    return _vis("slicer", position, {"Values": {"projections": [proj_col(cat)]}}, slicer_obj())

def rect(position, fill=NAVY):
    return {"$schema": VIS_SCHEMA, "name": uid(), "position": position,
            "visual": {"visualType": "shape",
                       "objects": {"line": [{"properties": {
                                        "roundEdge": {"expr": {"Literal": {"Value": "0D"}}},
                                        "weight":    {"expr": {"Literal": {"Value": "0D"}}},
                                        "color":     {"solid": {"color": fill}}}}],
                                   "fill": [{"properties": {
                                        "show":      {"expr": {"Literal": {"Value": "true"}}},
                                        "fillColor": {"solid": {"color": fill}}}}]}}}

def textbox(position, text, size=15, color=WHITE):
    return {"$schema": VIS_SCHEMA, "name": uid(), "position": position,
            "visual": {"visualType": "textbox",
                       "objects": {"general": [{"properties": {"paragraphs": [{
                           "textRuns": [{"value": text, "textStyle": {
                               "fontWeight": "bold", "fontSize": f"{size}pt",
                               "color": color, "fontFamily": "Segoe UI"}}],
                           "horizontalTextAlignment": "Left"}]}}]}}}

# ── Page builder ────────────────────────────────────────────
def make_page(display_name, visuals):
    folder  = uid()
    pg_dir  = os.path.join(RD, "definition", "pages", folder)
    vis_dir = os.path.join(pg_dir, "visuals")
    jwrite(os.path.join(pg_dir, "page.json"), {
        "$schema": PAGE_SCHEMA, "name": folder,
        "displayName": display_name,
        "displayOption": "FitToPage", "height": H, "width": W})
    for v in visuals:
        jwrite(os.path.join(vis_dir, v["name"], "visual.json"), v)
    print(f"  [OK] '{display_name}' — {len(visuals)} visuals")
    return folder

# ── Wipe old pages ──────────────────────────────────────────
pages_dir = os.path.join(RD, "definition", "pages")
for item in os.listdir(pages_dir):
    if item == "pages.json": continue
    full = os.path.join(pages_dir, item)
    if os.path.isdir(full): shutil.rmtree(full)
print("[OK] Old pages cleared\n")

pages_order = []

# ═══════════════════════════════════════════════════════════
# PAGE 1 — Customer Pyramid
# PS requirement: "how value is distributed across customer base"
# Shows: Diamond/Gold/Silver/Bronze tiers + revenue share + promo score per tier
# ═══════════════════════════════════════════════════════════
tier_colors = [DIAM, GOLD, SILVER, BRONZE]
p1 = [
    rect(pos(0,0,W,54,z=-2,tab=1), NAVY),
    textbox(pos(16,10,760,36,z=-1,tab=2),
            "Customer Pyramid  |  Value Distribution & Tier Analysis", 15, WHITE),
    # KPI row — all from CustomerFeatures engineered table
    card(pos(16,  68, 220, 92, tab=100), "customer_id",        AGG_CNT, "Total Customers"),
    card(pos(246, 68, 220, 92, tab=101), "purchase_amount_usd",AGG_SUM, "Total Revenue ($)"),
    card(pos(476, 68, 220, 92, tab=102), "composite_score",    AGG_AVG, "Avg Composite Score"),
    card(pos(706, 68, 220, 92, tab=103), "promo_dependency_score", AGG_AVG, "Avg Promo Score"),
    card(pos(936, 68, 220, 92, tab=104), "previous_purchases", AGG_AVG, "Avg Prev. Purchases"),
    # Slicers
    slicer(pos(16,  174, 160, 68, tab=200), "season"),
    slicer(pos(186, 174, 160, 68, tab=201), "gender"),
    slicer(pos(356, 174, 180, 68, tab=202), "value_tier"),
    # PYRAMID: Customers per value tier (horizontal bar — largest bar = most customers)
    bar(pos(16, 254, 580, 240, tab=300),
        "value_tier", "customer_id", AGG_CNT, "Customers",
        horiz=True, colors=tier_colors),
    # Revenue share per tier
    donut(pos(606, 254, 300, 240, tab=301),
          "value_tier", "purchase_amount_usd", AGG_SUM, "Revenue ($)",
          colors=tier_colors),
    # Avg Promo Score per tier (key PS insight: who depends on discounts by tier)
    bar(pos(916, 254, 348, 240, tab=302),
        "value_tier", "promo_dependency_score", AGG_AVG, "Avg Promo Score",
        horiz=False, colors=tier_colors),
    # Avg Composite Score per tier
    bar(pos(16, 506, 580, 196, tab=400),
        "value_tier", "composite_score", AGG_AVG, "Avg Composite Score",
        horiz=True, colors=tier_colors),
    # Avg Previous Purchases per tier (retention depth)
    bar(pos(606, 506, 658, 196, tab=401),
        "value_tier", "previous_purchases", AGG_AVG, "Avg Prev. Purchases",
        horiz=False, colors=tier_colors),
]
pages_order.append(make_page("Customer Pyramid", p1))

# ═══════════════════════════════════════════════════════════
# PAGE 2 — Promo Dependency vs. Loyalty
# PS requirement: "promo dependency vs retention rate, plotted by segment"
# Shows: promo score by tier, loyalty_a/loyalty_b flags, discount rate by category
# ═══════════════════════════════════════════════════════════
p2 = [
    rect(pos(0,0,W,54,z=-2,tab=1), CORAL),
    textbox(pos(16,10,760,36,z=-1,tab=2),
            "Promo Dependency vs. Organic Loyalty  |  Segment Analysis", 15, WHITE),
    card(pos(16,  68, 220, 92, tab=100), "customer_id",           AGG_CNT, "Total Customers"),
    card(pos(246, 68, 220, 92, tab=101), "loyalty_a",             AGG_SUM, "Loyalty A (Organic)"),
    card(pos(476, 68, 220, 92, tab=102), "loyalty_b",             AGG_SUM, "Loyalty B (Value)"),
    card(pos(706, 68, 220, 92, tab=103), "promo_dependency_score",AGG_AVG, "Avg Promo Score"),
    card(pos(936, 68, 220, 92, tab=104), "purchase_amount_usd",   AGG_SUM, "Total Revenue ($)"),
    slicer(pos(16,  174, 170, 68, tab=200), "value_tier"),
    slicer(pos(196, 174, 170, 68, tab=201), "season"),
    # Promo dependency score by value tier (core PS metric: who needs discounts by segment)
    bar(pos(16, 254, 580, 240, tab=300),
        "value_tier", "promo_dependency_score", AGG_AVG, "Avg Promo Score (0=organic, 3=promo-only)",
        horiz=True, colors=[DIAM, GOLD, SILVER, BRONZE]),
    # Loyalty A (organic loyal) vs Loyalty B (value loyal) counts
    donut(pos(606, 254, 300, 240, tab=301),
          "discount_applied", "customer_id", AGG_CNT, "Customers",
          colors=[TEAL, CORAL]),
    # Avg promo score by category (which categories attract promo hunters)
    bar(pos(916, 254, 348, 240, tab=302),
        "category", "promo_dependency_score", AGG_AVG, "Avg Promo Score",
        horiz=False, colors=[NAVY, TEAL, AMBER, CORAL]),
    # Promo dependency by age bracket
    bar(pos(16, 506, 580, 196, tab=400),
        "age_bracket", "promo_dependency_score", AGG_AVG, "Avg Promo Score",
        horiz=True, colors=[NAVY, TEAL, AMBER, CORAL, BLUE]),
    # Promo score by frequency — frequent buyers: organic or promo-driven?
    bar(pos(606, 506, 658, 196, tab=401),
        "frequency_of_purchases", "promo_dependency_score", AGG_AVG, "Avg Promo Score",
        horiz=False, colors=[NAVY, TEAL, AMBER, CORAL, BLUE, GREEN, VIOLET]),
]
pages_order.append(make_page("Promo vs. Organic Loyalty", p2))

# ═══════════════════════════════════════════════════════════
# PAGE 3 — Category Funnel (Entry vs. Retention)
# PS requirement: "which categories associated with low vs. high purchase history"
# Shows: avg prev purchases per category + promo sensitivity per category
# ═══════════════════════════════════════════════════════════
p3 = [
    rect(pos(0,0,W,54,z=-2,tab=1), TEAL),
    textbox(pos(16,10,760,36,z=-1,tab=2),
            "Category Funnel  |  Entry Point vs. Retention Categories", 15, WHITE),
    card(pos(16,  68, 280, 92, tab=100), "previous_purchases",    AGG_AVG, "Avg Prev. Purchases"),
    card(pos(306, 68, 280, 92, tab=101), "customer_id",           AGG_CNT, "Total Customers"),
    card(pos(592, 68, 280, 92, tab=102), "purchase_amount_usd",   AGG_AVG, "Avg Spend ($)"),
    card(pos(882, 68, 282, 92, tab=103), "promo_dependency_score",AGG_AVG, "Avg Promo Score"),
    slicer(pos(16,  174, 178, 68, tab=200), "season"),
    slicer(pos(204, 174, 178, 68, tab=201), "value_tier"),
    # FUNNEL: Avg Previous Purchases by category — higher = retention category
    # Lower avg = entry-point category (customers are newer / fewer past purchases)
    bar(pos(16, 254, 580, 240, tab=300),
        "category", "previous_purchases", AGG_AVG, "Avg Prev. Purchases (Higher = Retention)",
        horiz=True, colors=[NAVY, TEAL, AMBER, CORAL]),
    # Avg Spend by category
    bar(pos(606, 254, 658, 240, tab=301),
        "category", "purchase_amount_usd", AGG_AVG, "Avg Spend ($)",
        horiz=False, colors=[TEAL, AMBER, CORAL, NAVY]),
    # Promo score by category: which categories attract promo-dependent buyers?
    bar(pos(16, 506, 580, 196, tab=400),
        "category", "promo_dependency_score", AGG_AVG, "Avg Promo Dependency (Lower = More Organic)",
        horiz=True, colors=[CORAL, AMBER, TEAL, NAVY]),
    # Avg prev purchases by age bracket (which demographics are newer vs. loyal)
    bar(pos(606, 506, 658, 196, tab=401),
        "age_bracket", "previous_purchases", AGG_AVG, "Avg Prev. Purchases by Age",
        horiz=False, colors=[NAVY, TEAL, AMBER, CORAL, BLUE]),
]
pages_order.append(make_page("Category Funnel", p3))

# ═══════════════════════════════════════════════════════════
# PAGE 4 — Geographic Opportunity Map
# PS requirement: "high spend AND low promo dependency by region"
# Shows: avg spend by state + avg promo score by state (genuine brand pull)
# ═══════════════════════════════════════════════════════════
p4 = [
    rect(pos(0,0,W,54,z=-2,tab=1), AMBER),
    textbox(pos(16,10,760,36,z=-1,tab=2),
            "Geographic Opportunity  |  Brand Pull vs. Discount-Driven Demand", 15, NAVY),
    card(pos(16,  68, 278, 92, tab=100), "customer_id",           AGG_CNT, "Total Customers"),
    card(pos(304, 68, 278, 92, tab=101), "purchase_amount_usd",   AGG_AVG, "Avg Spend ($)"),
    card(pos(592, 68, 278, 92, tab=102), "promo_dependency_score",AGG_AVG, "Avg Promo Score"),
    card(pos(880, 68, 284, 92, tab=103), "previous_purchases",    AGG_AVG, "Avg Prev. Purchases"),
    slicer(pos(16,  174, 178, 68, tab=200), "season"),
    slicer(pos(204, 174, 178, 68, tab=201), "category"),
    # AVG SPEND by State — which states have high genuine spend?
    bar(pos(16, 254, 634, 226, tab=300),
        "location", "purchase_amount_usd", AGG_AVG, "Avg Spend ($) — Higher = More Valuable",
        horiz=True, colors=[NAVY]),
    # AVG PROMO SCORE by State — which states are discount-driven vs. organic?
    # Low promo score + high spend = genuine brand pull (geographic opportunity)
    bar(pos(16, 490, 634, 212, tab=400),
        "location", "promo_dependency_score", AGG_AVG, "Avg Promo Score — Lower = More Organic",
        horiz=True, colors=[CORAL]),
    # Gender split
    donut(pos(660, 254, 308, 210, tab=301),
          "gender", "customer_id", AGG_CNT, "Customers",
          colors=[NAVY, TEAL]),
    # Value tier distribution geographically (avg composite score by top regions)
    bar(pos(660, 474, 604, 228, tab=401),
        "value_tier", "purchase_amount_usd", AGG_AVG, "Avg Spend by Tier ($)",
        horiz=False, colors=[DIAM, GOLD, SILVER, BRONZE]),
]
pages_order.append(make_page("Geographic Opportunity", p4))

# ── Update pages.json ───────────────────────────────────────
jwrite(os.path.join(pages_dir, "pages.json"), {
    "$schema": PAGES_SCHEMA,
    "pageOrder": pages_order,
    "activePageName": pages_order[0]
})

print()
print("=" * 68)
print("  FINAL dashboard built — all 4 PS requirements addressed!")
print("=" * 68)
print()
print("  Page 1: Customer Pyramid       (Diamond/Gold/Silver/Bronze tiers)")
print("  Page 2: Promo vs. Organic      (promo score by segment, loyalty flags)")
print("  Page 3: Category Funnel        (entry vs. retention by avg purchases)")
print("  Page 4: Geographic Opportunity (avg SPEND + avg PROMO SCORE by state)")
print()
print("  Data source: CustomerFeatures table -> customer_features.csv")
print("                (34 engineered columns, auto-linked)")
print()
print("  Close Power BI Desktop completely, then re-open dashboard.pbip")
print("=" * 68)
