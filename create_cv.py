from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# ========== NAME ==========
name = doc.add_paragraph()
name_run = name.add_run("MUDASSAR ABDUL KADER ANSARI")
name_run.font.size = Pt(18)
name_run.font.bold = True
name.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.add_run("Global Head of Supply Chain & Procurement Leadership").font.size = Pt(12)
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle2 = doc.add_paragraph()
subtitle2.add_run("Luxury Restaurant · Premium F&B Retail · GCC & International Markets").font.size = Pt(11)
subtitle2.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

# ========== CONTACT TABLE ==========
contact_table = doc.add_table(rows=1, cols=4)
contact_table.style = 'Table Grid'
contacts = [
    "📞 +971 564 018 627",
    "✉️ mudassar142@gmail.com",
    "📍 Dubai, UAE",
    "🚗 UAE Valid Driving Licence"
]
for i, text in enumerate(contacts):
    cell = contact_table.rows[0].cells[i]
    cell.text = text
    for para in cell.paragraphs:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.font.size = Pt(9)

doc.add_paragraph()


def add_section(title):
    h = doc.add_paragraph()
    r = h.add_run(title)
    r.font.size = Pt(13)
    r.font.bold = True


# ========== EXECUTIVE SUMMARY ==========
add_section("EXECUTIVE SUMMARY")
doc.add_paragraph(
    "A decisive, commercially astute Supply Chain & Procurement executive with 16+ years of progressive "
    "leadership across luxury restaurant brands, premium F&B retail, and multi-brand dining operations in "
    "the GCC and international markets. Recognised for architecting end-to-end procurement frameworks that "
    "drive measurable cost efficiencies, establishing governance structures that withstand KPMG and BRC "
    "scrutiny, and orchestrating multi-country supply chains with tangible bottom-line impact. Adept at "
    "building high-performing teams, institutionalising vendor ecosystems, and translating operational "
    "complexity into strategic advantage."
)
doc.add_paragraph()

# ========== CORE COMPETENCIES ==========
add_section("CORE COMPETENCIES")
skills = [
    ("Strategic Procurement & Sourcing",   "Demand Planning & Forecasting"),
    ("Multi-Country Supply Chain",          "Vendor Development & Negotiation"),
    ("Warehouse & 3PL Management",          "Capex & OS&E Governance"),
    ("Cost Engineering & Optimisation",     "ERP Implementation & Rollout"),
    ("P&L & Budget Management",             "Team Leadership (up to 10)"),
    ("BRC & KPMG Audit Compliance",         "GCC Import / Export Regulations"),
]
comp_table = doc.add_table(rows=len(skills), cols=2)
comp_table.style = 'Table Grid'
for row_idx, (left, right) in enumerate(skills):
    comp_table.rows[row_idx].cells[0].text = f"• {left}"
    comp_table.rows[row_idx].cells[1].text = f"• {right}"

doc.add_paragraph()

# ========== TECHNOLOGY ==========
add_section("TECHNOLOGY")
doc.add_paragraph(
    "ERP Navision · Finop · Fidelio Material Control System · MS Office · Notion SC Dashboards"
)
doc.add_paragraph()

# ========== PROFESSIONAL EXPERIENCE ==========
add_section("PROFESSIONAL EXPERIENCE")

experiences = [
    {
        "title":   "Global Head of Supply Chain",
        "company": "Ladurée Paris — French Coffee Spirit LLC | Dubai, UAE | Nov 2022 – Present",
        "bullets": [
            "Lead end-to-end supply chain governance for Ladurée's luxury macaron, pastry, chocolate, and café portfolio across six sovereign markets, driving procurement centralisation from UAE as regional hub.",
            "Engineered comprehensive procurement, warehousing, logistics, and transportation SOPs, establishing unified compliance across all territories.",
            "Delivered AED 1.5 million in verified cost savings in FY2023 through supplier renegotiations, demand-signal consolidation, and freight optimisation.",
            "Manage perishable luxury SKU inventory across six warehouses, maintaining optimal Stock Cover Days and zero-waste targets.",
        ],
    },
    {
        "title":   "Head of Regional Procurement",
        "company": "Bateel International LLC | Dubai, UAE | Jun 2016 – Oct 2022",
        "bullets": [
            "Orchestrated procurement of AED 90 million annually across premium boutiques, airport duty shops, and café network.",
            "Delivered AED 21.3 million cumulative savings (2017-2020) through strategic vendor consolidation and TCO modelling.",
            "Architected KPMG-aligned procurement governance framework; led BRC audit programme to successful certification.",
            "Drove full-cycle ERP (Navision) implementation and global sourcing across China, USA, UK, France, and Italy.",
        ],
    },
    {
        "title":   "Procurement & Purchase Manager",
        "company": "Marka PJSC — Fine & Casual Dining | Dubai, UAE | Dec 2014 – May 2016",
        "bullets": [
            "Established procurement division from inception for DFM-listed hospitality group.",
            "Implemented vendor qualification, QA, and 3PL frameworks; realised AED 610,258 in savings within first twelve months.",
        ],
    },
    {
        "title":   "Regional Supply Chain Manager",
        "company": "Gourmet Gulf Company | UAE & GCC | Aug 2010 – Nov 2014",
        "bullets": [
            "Sole supply chain custodian for 7 brands (CPK, Yo Sushi, Panda Express, GBK, Morelli's Gelato, Azkadenya, Hummingbird) across 6 countries.",
            "Reduced cost of sale by 1.6% YoY and extended supplier credit terms to improve working capital.",
            "Established greenfield supply chain in KSA, Bahrain, and Oman; commissioned Dubai warehouse hub with ERP integration.",
        ],
    },
    {
        "title":   "Supply Chain Officer",
        "company": "M. H. Alshaya Group | UAE | Mar 2008 – Jul 2010",
        "bullets": [
            "Managed supply planning and volume fulfilment across Alshaya's entire UAE F&B portfolio (Cheesecake Factory, PF Chang's, Texas Roadhouse, Dean & Deluca, LPQ); led S&OP process.",
        ],
    },
    {
        "title":   "Receiving In-Charge → Store Keeper → Supply Chain Officer",
        "company": "Taj Lands End (TATA Group) & M. H. Alshaya | India / UAE | Apr 2006 – Feb 2008",
        "bullets": [
            "Progressed from luxury hotel receiving management at 5-star Taj Lands End to Supply Chain Officer at Alshaya within four months based on exceptional initiative.",
        ],
    },
]

for exp in experiences:
    p = doc.add_paragraph()
    p.add_run(exp["title"]).bold = True
    p.add_run(f" | {exp['company']}")
    for bullet in exp["bullets"]:
        doc.add_paragraph(bullet, style='List Bullet')
    doc.add_paragraph()

# ========== EDUCATION ==========
add_section("EDUCATION")
doc.add_paragraph("B.Com — Finance & Accounting | Mumbai University, India | [Add Year]")
doc.add_paragraph()

# ========== CERTIFICATIONS ==========
add_section("CERTIFICATIONS")
doc.add_paragraph(
    "Food Material Control System · Halal Food Certification · BRC — British Retail Consortium "
    "· ERP Navision Finop · Hospitality Degree Course"
)
doc.add_paragraph()

# ========== MARKET COVERAGE ==========
add_section("MARKET COVERAGE")
doc.add_paragraph("UAE · KSA · Kuwait · Qatar · Bahrain · Oman · Egypt · China")
doc.add_paragraph()

# ========== LANGUAGES ==========
add_section("LANGUAGES")
doc.add_paragraph("English (Fluent) | Hindi (Fluent) | Urdu (Fluent) | Arabic [Add Level]")
doc.add_paragraph()

# ========== ADDITIONAL INFORMATION ==========
add_section("ADDITIONAL INFORMATION")
doc.add_paragraph(
    "References available upon request · Indian Passport · UAE Valid Driving Licence · Based in Dubai, UAE"
)

doc.save("Mudassar_Ansari_CV.docx")
print("✅ CV saved as 'Mudassar_Ansari_CV.docx'")
