from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Set margins
sections = doc.sections
for section in sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

def add_section(title):
    heading = doc.add_paragraph()
    heading_run = heading.add_run(title)
    heading_run.font.size = Pt(13)
    heading_run.font.bold = True
    heading_run.font.name = 'Calibri'
    heading.paragraph_format.space_before = Pt(12)
    heading.paragraph_format.space_after = Pt(6)
    return heading

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.25 + (level * 0.25))
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Calibri'
    return p

# ========== NAME ==========
name = doc.add_paragraph()
name_run = name.add_run("MUDASSAR ABDUL KADER ANSARI")
name_run.font.size = Pt(20)
name_run.font.bold = True
name_run.font.name = 'Calibri'
name.alignment = WD_ALIGN_PARAGRAPH.CENTER
name.paragraph_format.space_after = Pt(0)

# ========== SUBTITLE ==========
subtitle = doc.add_paragraph()
subtitle_run = subtitle.add_run("Global Head of Supply Chain & Procurement Leadership")
subtitle_run.font.size = Pt(12)
subtitle_run.font.name = 'Calibri'
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.paragraph_format.space_after = Pt(0)

subtitle2 = doc.add_paragraph()
subtitle2_run = subtitle2.add_run("Luxury Restaurant · Premium F&B Retail · GCC & International Markets")
subtitle2_run.font.size = Pt(11)
subtitle2_run.font.name = 'Calibri'
subtitle2.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle2.paragraph_format.space_after = Pt(8)

# ========== CONTACT TABLE ==========
contact_table = doc.add_table(rows=1, cols=4)
contact_table.style = 'Table Grid'

contacts = ["📞 +971 564 018 627", "✉️ mudassar142@gmail.com", "📍 Dubai, UAE", "🚗 UAE Valid Driving Licence"]
for i, text in enumerate(contacts):
    cell = contact_table.rows[0].cells[i]
    cell.text = text
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if paragraph.runs:
            paragraph.runs[0].font.size = Pt(9)
            paragraph.runs[0].font.name = 'Calibri'

doc.add_paragraph()

# ========== KEY METRICS ==========
add_section("KEY METRICS")
metrics_table = doc.add_table(rows=2, cols=5)
metrics_table.style = 'Table Grid'

metrics_labels = ["Annual Spend", "Cost Savings", "Countries", "Outlets Supported", "Team Span"]
metrics_values = ["AED 90MM+", "AED 22.8M+", "7", "200+", "45 (Indirect)"]

for i, label in enumerate(metrics_labels):
    cell = metrics_table.rows[0].cells[i]
    cell.text = label
    for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.runs:
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(9)

for i, value in enumerate(metrics_values):
    cell = metrics_table.rows[1].cells[i]
    cell.text = value
    for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.runs:
            p.runs[0].font.size = Pt(10)
            p.runs[0].font.bold = True

doc.add_paragraph()

# ========== EXECUTIVE SUMMARY ==========
add_section("EXECUTIVE SUMMARY")
summary = ("A decisive, commercially astute Supply Chain & Procurement executive with 16+ years of progressive leadership across luxury restaurant brands, premium F&B retail, and multi-brand dining operations in the GCC and international markets. Recognised for architecting end-to-end procurement frameworks that drive measurable cost efficiencies, establishing governance structures that withstand KPMG and BRC scrutiny, and orchestrating multi-country supply chains with tangible bottom-line impact.")
p = doc.paragraphs[-1]
p.add_run(summary).font.size = Pt(10)

add_section("KEY DIFFERENTIATORS")
add_bullet("Delivered AED 22.8M+ cumulative cost savings across 3 organisations (2014-2024)")
add_bullet("Led supply chain for 200+ F&B outlets across 8 countries simultaneously")
add_bullet("Zero major audit findings across 4 KPMG and 6 BRC audits")

doc.add_paragraph()

# ========== CORE COMPETENCIES ==========
add_section("CORE COMPETENCIES")
comp_table = doc.add_table(rows=3, cols=2)
comp_table.style = 'Table Grid'

skills = [
    "Strategic Procurement & Sourcing", "Demand Planning & Forecasting",
    "Multi-Country Supply Chain", "Vendor Development & Negotiation",
    "Warehouse & 3PL Management", "Capex & OS&E Governance",
    "Cost Engineering & Optimisation", "ERP Implementation & Rollout",
    "P&L & Budget Management", "Team Leadership (up to 45 indirect)",
    "BRC & KPMG Audit Compliance", "GCC Import / Export Regulations"
]

for i, skill in enumerate(skills):
    row = i // 2
    col = i % 2
    if i >= 2 and i % 2 == 0:
        comp_table.add_row()
    cell = comp_table.rows[row].cells[col]
    cell.text = f"• {skill}"
    for p in cell.paragraphs:
        if p.runs:
            p.runs[0].font.size = Pt(9)

doc.add_paragraph()

# ========== CRISIS MANAGEMENT ==========
add_section("CRISIS MANAGEMENT & RESILIENCE")
add_bullet("COVID-19: Secured alternative airfreight corridors (China-UAE within 72 hours); maintained 98% menu availability")
add_bullet("Red Sea Disruption (2024): Pre-positioned inventory via Jebel Ali and Salalah; rerouted 40+ containers with zero impact")
add_bullet("Inflation Management: Locked 12-month pricing with top 20 suppliers; implemented monthly commodity hedging reviews")

doc.add_paragraph()

# ========== BOARD MANAGEMENT ==========
add_section("BOARD & STAKEHOLDER MANAGEMENT")
add_bullet("Present quarterly Supply Chain performance to CEO/COO/Investors — cost savings, risk register, Capex governance")
add_bullet("Led 3 successful Capex approvals totalling AED 8.5M (warehouse automation, cold chain expansion)")
add_bullet("Negotiated payment term extensions from 30 to 60 days across 65% of supplier base — releasing AED 12M+ working capital")

doc.add_paragraph()

# ========== TECHNOLOGY ==========
add_section("TECHNOLOGY & DIGITAL TRANSFORMATION")
tech_table = doc.add_table(rows=6, cols=2)
tech_table.style = 'Table Grid'

tech_data = [
    ("ERP Implementation", "Navision (Bateel) — full lifecycle; trained 45 users"),
    ("Business Intelligence", "Built dashboards (Notion/Excel); reduced reporting from 5 days to 2 hours"),
    ("Supplier Portal", "Vendor self-service — reduced query volume by 40%"),
    ("Inventory Optimisation", "Fidelio — reduced stock cover from 45 to 32 days"),
    ("Next (Planned)", "Power BI migration + demand forecasting ML pilot (Q4 2026)")
]

for i, (capability, outcome) in enumerate(tech_data):
    if i > 0:
        tech_table.add_row()
    tech_table.rows[i].cells[0].text = capability
    tech_table.rows[i].cells[1].text = outcome
    for row in tech_table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if p.runs:
                    p.runs[0].font.size = Pt(9)

doc.add_paragraph()

# ========== SUSTAINABILITY ==========
add_section("SUSTAINABILITY & ETHICAL SOURCING")
add_bullet("Reduced single-use plastic by 78% across Ladurée packaging (2023-2024)")
add_bullet("Achieved zero organic waste to landfill from 6 warehouses through composting partnerships")
add_bullet("Implemented Halal certification governance across all GCC suppliers — 100% compliance")
add_bullet("BRC 'AA' grade achieved (Bateel, 2020) — top 5% globally")

doc.add_paragraph()

# ========== PROFESSIONAL EXPERIENCE ==========
add_section("PROFESSIONAL EXPERIENCE")

# Role 1: Ladurée (CURRENT) - INCLUDES Paul Bakery Spain
p = doc.add_paragraph()
p.add_run("Global Head of Supply Chain").bold = True
p.add_run(" | Ladurée (Paris / Dubai) | Dubai, UAE | Nov 2022 – Present")
p.runs[1].font.size = Pt(10)
add_bullet("Key Achievement: Reduced landed cost per unit by 9% within 12 months despite 15% global freight inflation.", level=0)
add_bullet("Lead end-to-end supply chain governance for Ladurée's luxury macaron, pastry, chocolate, and café portfolio across six sovereign markets.", level=0)
add_bullet("Key Achievement: Added Paul Bakery (Spain) to portfolio — launched 4 locations (2 Barcelona, 2 Madrid) with 100% supply chain readiness and zero opening delays.", level=0)
add_bullet("Engineered comprehensive procurement, warehousing, logistics, and transportation SOPs across all territories.", level=0)
add_bullet("Delivered AED 1.5 million in verified cost savings in FY2023 through supplier renegotiations and freight optimisation.", level=0)
add_bullet("Manage perishable luxury SKU inventory across six warehouses, maintaining zero-waste targets.", level=0)
doc.add_paragraph()

# Role 2: Bateel
p = doc.add_paragraph()
p.add_run("Head of Regional Procurement").bold = True
p.add_run(" | Bateel International LLC | Dubai, UAE | Jun 2016 – Oct 2022")
p.runs[1].font.size = Pt(10)
add_bullet("Key Achievement: Transformed procurement from decentralised to centralised model, consolidating 340+ suppliers to 170 — compliance from 62% to 94% in 18 months.", level=0)
add_bullet("Orchestrated procurement of AED 90 million annually across premium boutiques, airport duty shops, and café network.", level=0)
add_bullet("Delivered AED 21.3 million cumulative savings (2017-2020) through strategic vendor consolidation and TCO modelling.", level=0)
add_bullet("Architected KPMG-aligned procurement governance framework; led BRC audit to successful certification.", level=0)
add_bullet("Drove full-cycle ERP (Navision) implementation and global sourcing across China, USA, UK, France, and Italy.", level=0)
doc.add_paragraph()

# Role 3: Marka PJSC
p = doc.add_paragraph()
p.add_run("Procurement & Purchase Manager").bold = True
p.add_run(" | Marka PJSC — Fine & Casual Dining | Dubai, UAE | Dec 2014 – May 2016")
p.runs[1].font.size = Pt(10)
add_bullet("Established procurement division from inception for DFM-listed hospitality group.", level=0)
add_bullet("Implemented vendor qualification, QA, and 3PL frameworks; realised AED 610,258 in savings within first twelve months.", level=0)
doc.add_paragraph()

# Role 4: Gourmet Gulf
p = doc.add_paragraph()
p.add_run("Regional Supply Chain Manager").bold = True
p.add_run(" | Gourmet Gulf Company | UAE & GCC | Aug 2010 – Nov 2014")
p.runs[1].font.size = Pt(10)
add_bullet("Key Achievement: Scaled supply chain from 1 to 6 countries in 3 years with 99.2% OTIF and zero stockouts.", level=0)
add_bullet("Sole supply chain custodian for 7 brands (CPK, Yo Sushi, Panda Express, GBK, Morelli's Gelato, Azkadenya, Hummingbird) across 6 countries.", level=0)
add_bullet("Reduced cost of sale by 1.6% YoY and extended supplier credit terms to improve working capital.", level=0)
add_bullet("Established greenfield supply chain in KSA, Bahrain, and Oman; commissioned Dubai warehouse hub with ERP integration.", level=0)
doc.add_paragraph()

# Role 5: Alshaya
p = doc.add_paragraph()
p.add_run("Supply Chain Officer").bold = True
p.add_run(" | M. H. Alshaya Group | UAE | Mar 2008 – Jul 2010")
p.runs[1].font.size = Pt(10)
add_bullet("Managed supply planning across Alshaya's UAE F&B portfolio (Cheesecake Factory, PF Chang's, Texas Roadhouse, Dean & Deluca, LPQ); led S&OP process.", level=0)
doc.add_paragraph()

# Role 6: Early Career
p = doc.add_paragraph()
p.add_run("Receiving In-Charge → Store Keeper → Supply Chain Officer").bold = True
p.add_run(" | Taj Lands End (TATA Group) & M. H. Alshaya | India / UAE | Apr 2006 – Feb 2008")
p.runs[1].font.size = Pt(10)
add_bullet("Progressed from luxury hotel receiving at 5-star Taj Lands End to Supply Chain Officer at Alshaya within four months.", level=0)

doc.add_paragraph()

# ========== EDUCATION ==========
add_section("EDUCATION")
p = doc.add_paragraph()
p.add_run("B.Com — Finance & Accounting").bold = True
p.add_run(" | Mumbai University, India | 2014")
p.runs[0].font.size = Pt(10)

# ========== CERTIFICATIONS ==========
add_section("CERTIFICATIONS & PROFESSIONAL DEVELOPMENT")
cert_table = doc.add_table(rows=5, cols=3)
cert_table.style = 'Table Grid'

certs = [
    ("BRC Global Standard (Food)", "2020, 2022, 2024", "British Retail Consortium"),
    ("ERP Navision (Advanced User)", "2018", "Microsoft"),
    ("Halal Food Certification (Lead Auditor)", "2019", "ESMA/GAC"),
    ("Supply Chain Risk Management", "2022", "CIPS / [Add issuer]"),
    ("Inventory & Warehouse Management", "2021", "[Add issuer]")
]

headers = ["Certification", "Year", "Issuer"]
for i, header in enumerate(headers):
    cert_table.rows[0].cells[i].text = header
    for p in cert_table.rows[0].cells[i].paragraphs:
        if p.runs:
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(9)

for i, (cert, year, issuer) in enumerate(certs):
    row = i + 1
    cert_table.add_row()
    cert_table.rows[row].cells[0].text = cert
    cert_table.rows[row].cells[1].text = year
    cert_table.rows[row].cells[2].text = issuer
    for cell in cert_table.rows[row].cells:
        for p in cell.paragraphs:
            if p.runs:
                p.runs[0].font.size = Pt(9)

p = doc.add_paragraph()
p.add_run("In Progress (2026): CSCP (APICS) or CPSM (ISM)")
p.runs[0].font.size = Pt(9)
p.runs[0].italic = True

doc.add_paragraph()

# ========== MARKET COVERAGE ==========
add_section("MARKET COVERAGE")
p = doc.add_paragraph()
p.add_run("UAE · KSA · Kuwait · Qatar · Bahrain · Oman · Egypt · China · Morocco")
p.runs[0].font.size = Pt(10)
p = doc.add_paragraph()
p.add_run("Spain (Paul Bakery — Barcelona 2 locations + Madrid 2 locations)")
p.runs[0].font.size = Pt(9)
p.runs[0].italic = True

# ========== LANGUAGES ==========
add_section("LANGUAGES")
p = doc.add_paragraph()
p.add_run("English (Fluent) | Hindi (Fluent) | Urdu (Fluent)")
p.runs[0].font.size = Pt(10)

# ========== ADDITIONAL INFO ==========
add_section("ADDITIONAL INFORMATION")
p = doc.add_paragraph()
p.add_run("References available upon request · Indian Passport · UAE Valid Driving Licence · Based in Dubai, UAE")
p.runs[0].font.size = Pt(10)

# ========== SAVE ==========
doc.save("Mudassar_Ansari_CV_Final_Corrected.docx")
print("✅ FINAL CORRECTED CV saved as 'Mudassar_Ansari_CV_Final_Corrected.docx'")
print("\n📝 Key corrections made:")
print("   • Ladurée: Removed 'French Coffee Spirit LLC' — now just 'Ladurée (Paris / Dubai)'")
print("   • Paul Bakery Spain (4 locations) moved from Gourmet Gulf → Ladurée (current role)")
print("   • Gourmet Gulf: Paul Bakery removed (now only original 7 brands)")
print("   • Market Coverage: Spain added with Paul Bakery details")
