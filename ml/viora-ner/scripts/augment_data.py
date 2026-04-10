"""
Viora NER — Data Augmentation Pipeline.

Generates high-quality synthetic training data by:
  1. Entity Substitution — swap skills/orgs/names with realistic alternatives
  2. Template Generation — create new resumes from domain-specific templates
  3. Contextual Shuffling — reorder resume sections

Covers ALL professional domains for production use:
  IT, Healthcare, Engineering, Finance, Education, Marketing,
  Legal, Manufacturing, Media, Hospitality, etc.

Usage:
    python scripts/augment_data.py \\
        --input data/processed/train.jsonl \\
        --output data/processed/train_augmented.jsonl \\
        --target-count 15000
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import re
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# MULTI-DOMAIN ENTITY BANKS
# ═══════════════════════════════════════════════════════════

PERSON_NAMES = {
    "first": [
        # English
        "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
        "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
        "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen",
        "Daniel", "Emily", "Matthew", "Ashley", "Anthony", "Amanda",
        # Indian
        "Abhishek", "Priya", "Rajesh", "Sunita", "Vikram", "Anita", "Arjun",
        "Deepa", "Rahul", "Kavitha", "Sanjay", "Meera", "Amit", "Pooja",
        # Arabic
        "Ahmed", "Fatima", "Mohammed", "Aisha", "Ali", "Noor", "Omar",
        "Layla", "Hassan", "Maryam", "Khalid", "Sara", "Youssef", "Rania",
        # East Asian
        "Wei", "Mei", "Jun", "Yuki", "Hiroshi", "Sakura", "Min",
        "Jing", "Kenji", "Hana", "Chen", "Li", "Park", "Kim",
        # European
        "Pierre", "Marie", "Hans", "Anna", "Carlos", "Maria", "Ivan",
        "Olga", "Marco", "Sofia", "Stefan", "Elena", "Lars", "Ingrid",
    ],
    "last": [
        # English
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas",
        "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
        # Indian
        "Sharma", "Patel", "Kumar", "Singh", "Jha", "Gupta", "Verma",
        "Reddy", "Nair", "Iyer", "Chopra", "Mehta", "Bhat", "Das",
        # Arabic
        "Al-Hassan", "Al-Rashid", "Mansour", "Ibrahim", "Khalil",
        "Bakri", "Nasser", "Saleh", "Haddad", "Farouk",
        # East Asian
        "Wang", "Zhang", "Liu", "Chen", "Yang", "Tanaka", "Sato",
        "Suzuki", "Park", "Choi", "Nguyen", "Tran",
        # European
        "Mueller", "Schmidt", "Dubois", "Laurent", "Rossi", "Ferrari",
        "Petrov", "Svensson", "Nielsen", "Berg",
    ],
}

LOCATIONS = [
    # US
    "New York", "San Francisco", "Los Angeles", "Chicago", "Seattle",
    "Austin", "Boston", "Denver", "Miami", "Atlanta", "Dallas",
    "Washington DC", "Portland", "Phoenix", "Houston",
    # India
    "Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune",
    "Kolkata", "Ahmedabad", "Jaipur", "Noida", "Gurgaon",
    # Middle East
    "Dubai", "Abu Dhabi", "Riyadh", "Jeddah", "Doha", "Kuwait City",
    "Manama", "Muscat", "Amman", "Beirut", "Cairo",
    # Europe
    "London", "Berlin", "Paris", "Amsterdam", "Dublin", "Munich",
    "Zurich", "Stockholm", "Barcelona", "Milan", "Vienna", "Prague",
    # Asia Pacific
    "Singapore", "Tokyo", "Sydney", "Melbourne", "Auckland",
    "Hong Kong", "Seoul", "Shanghai", "Beijing", "Taipei",
    # Canada
    "Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary",
    # Other
    "São Paulo", "Mexico City", "Lagos", "Nairobi", "Cape Town",
]

ORGANIZATIONS = {
    "tech": [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix",
        "Salesforce", "Oracle", "IBM", "Intel", "Adobe", "Cisco",
        "SAP", "VMware", "Nvidia", "Uber", "Spotify", "Airbnb",
        "Twitter", "LinkedIn", "Stripe", "Shopify", "Atlassian",
        "ServiceNow", "Workday", "Snowflake", "Datadog", "Palantir",
        "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
        "Accenture", "Cognizant", "Capgemini", "Deloitte Digital",
    ],
    "healthcare": [
        "Mayo Clinic", "Johns Hopkins Hospital", "Cleveland Clinic",
        "Massachusetts General Hospital", "Stanford Health Care",
        "Pfizer", "Johnson & Johnson", "Roche", "Novartis", "Merck",
        "AstraZeneca", "Moderna", "Abbott Laboratories", "Medtronic",
        "UnitedHealth Group", "Anthem", "Cigna", "Humana",
        "Apollo Hospitals", "Fortis Healthcare", "Max Healthcare",
    ],
    "finance": [
        "JP Morgan Chase", "Goldman Sachs", "Morgan Stanley",
        "Bank of America", "Citigroup", "Wells Fargo", "HSBC",
        "Barclays", "Deutsche Bank", "UBS", "Credit Suisse",
        "BlackRock", "Vanguard", "Fidelity", "Charles Schwab",
        "Visa", "Mastercard", "PayPal", "Square", "Stripe",
        "Bloomberg", "Reuters", "S&P Global",
    ],
    "consulting": [
        "McKinsey & Company", "Boston Consulting Group", "Bain & Company",
        "Deloitte", "PwC", "EY", "KPMG", "Accenture",
        "Oliver Wyman", "Roland Berger", "A.T. Kearney",
    ],
    "manufacturing": [
        "General Electric", "Siemens", "Bosch", "3M", "Honeywell",
        "Caterpillar", "John Deere", "Toyota", "BMW", "Volkswagen",
        "Boeing", "Airbus", "Lockheed Martin", "Raytheon",
        "Procter & Gamble", "Unilever", "Nestle", "Coca-Cola",
    ],
    "education": [
        "Harvard University", "Stanford University", "MIT",
        "Oxford University", "Cambridge University", "Yale University",
        "Princeton University", "Columbia University", "UC Berkeley",
        "Coursera", "Udemy", "edX", "Khan Academy",
        "Pearson Education", "McGraw-Hill", "Wiley",
    ],
    "media": [
        "Disney", "Warner Bros", "NBC Universal", "Sony Pictures",
        "Netflix Studios", "Viacom", "BBC", "CNN", "Al Jazeera",
        "The New York Times", "The Washington Post", "Reuters",
        "Publicis Groupe", "WPP", "Omnicom Group",
    ],
    "energy": [
        "ExxonMobil", "Shell", "BP", "Chevron", "TotalEnergies",
        "Saudi Aramco", "ADNOC", "ConocoPhillips",
        "NextEra Energy", "Enel", "Vestas", "First Solar",
        "Siemens Gamesa", "Tesla Energy", "Enphase Energy",
    ],
}

SKILLS_BY_DOMAIN = {
    "software": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
        "Spring Boot", "Express.js", "Next.js", "FastAPI",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
        "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI",
        "REST API", "GraphQL", "gRPC", "Microservices",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "Natural Language Processing", "Computer Vision",
        "Data Analysis", "Data Engineering", "Apache Spark", "Kafka",
        "Agile", "Scrum", "JIRA", "Confluence", "Git", "Linux",
    ],
    "healthcare": [
        "Patient Care", "Clinical Research", "Electronic Health Records",
        "HIPAA Compliance", "Medical Coding", "ICD-10", "CPT Coding",
        "Pharmacology", "Clinical Trials", "GCP Guidelines",
        "Nursing", "Pediatrics", "Cardiology", "Oncology", "Radiology",
        "Surgical Procedures", "Emergency Medicine", "Telemedicine",
        "Medical Imaging", "Laboratory Testing", "Phlebotomy",
        "Epic Systems", "Cerner", "HL7", "FHIR", "DICOM",
        "Infection Control", "Patient Safety", "Quality Improvement",
        "Evidence-Based Practice", "Healthcare Management",
    ],
    "finance": [
        "Financial Analysis", "Financial Modeling", "Valuation",
        "Risk Management", "Portfolio Management", "Asset Management",
        "Investment Banking", "Mergers and Acquisitions", "IPO",
        "Equity Research", "Fixed Income", "Derivatives", "Options",
        "Bloomberg Terminal", "Excel", "VBA", "Financial Reporting",
        "GAAP", "IFRS", "Auditing", "Tax Planning", "Compliance",
        "Anti-Money Laundering", "KYC", "Basel III",
        "Quantitative Analysis", "Algorithmic Trading", "FinTech",
        "Blockchain", "Cryptocurrency", "Regulatory Compliance",
    ],
    "marketing": [
        "Digital Marketing", "Content Marketing", "SEO", "SEM",
        "Google Analytics", "Google Ads", "Facebook Ads",
        "Social Media Marketing", "Email Marketing", "Mailchimp",
        "HubSpot", "Salesforce Marketing Cloud", "A/B Testing",
        "Brand Management", "Market Research", "Consumer Behavior",
        "Product Marketing", "Growth Hacking", "Lead Generation",
        "CRM", "Marketing Automation", "Copywriting",
        "Adobe Creative Suite", "Canva", "Figma",
        "Public Relations", "Event Management", "Influencer Marketing",
    ],
    "engineering": [
        "AutoCAD", "SolidWorks", "CATIA", "ANSYS", "MATLAB",
        "Finite Element Analysis", "CFD", "CAD", "CAM",
        "Project Management", "PMP", "Lean Manufacturing", "Six Sigma",
        "Quality Assurance", "ISO 9001", "ISO 14001",
        "Mechanical Design", "Electrical Engineering", "PCB Design",
        "Civil Engineering", "Structural Analysis", "Building Codes",
        "Process Engineering", "Chemical Engineering", "Thermodynamics",
        "Hydraulics", "Pneumatics", "PLC Programming", "SCADA",
        "Supply Chain Management", "Logistics", "ERP Systems",
    ],
    "education": [
        "Curriculum Development", "Lesson Planning", "Classroom Management",
        "Student Assessment", "Differentiated Instruction",
        "Special Education", "ESL Teaching", "STEM Education",
        "Educational Technology", "Learning Management Systems",
        "Blackboard", "Canvas LMS", "Google Classroom", "Moodle",
        "Research Methodology", "Academic Writing", "Grant Writing",
        "Statistical Analysis", "SPSS", "Stata", "NVivo",
        "Online Teaching", "Blended Learning", "Instructional Design",
        "Tutoring", "Mentoring", "Educational Psychology",
    ],
    "legal": [
        "Contract Law", "Corporate Law", "Intellectual Property",
        "Litigation", "Arbitration", "Mediation", "Legal Research",
        "Legal Writing", "Due Diligence", "Regulatory Compliance",
        "Employment Law", "Immigration Law", "Tax Law", "Real Estate Law",
        "Mergers and Acquisitions", "Securities Law",
        "LexisNexis", "Westlaw", "Case Management",
        "Client Counseling", "Negotiation", "Trial Advocacy",
    ],
    "hr": [
        "Talent Acquisition", "Recruiting", "Interviewing",
        "Onboarding", "Employee Relations", "Performance Management",
        "Compensation and Benefits", "Payroll", "HRIS",
        "Workday", "SAP SuccessFactors", "ADP", "BambooHR",
        "Training and Development", "Organizational Development",
        "Diversity and Inclusion", "Labor Relations",
        "Employment Law", "Workforce Planning", "Succession Planning",
    ],
    "data_science": [
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Statistical Modeling", "A/B Testing",
        "Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn",
        "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM",
        "Data Visualization", "Tableau", "Power BI", "Matplotlib",
        "Big Data", "Apache Spark", "Hadoop", "Hive", "Airflow",
        "Feature Engineering", "Model Deployment", "MLOps",
        "Time Series Analysis", "Recommendation Systems",
        "Reinforcement Learning", "GANs", "Transformers",
    ],
    "design": [
        "UI Design", "UX Design", "User Research", "Wireframing",
        "Prototyping", "Figma", "Sketch", "Adobe XD", "InVision",
        "Adobe Photoshop", "Adobe Illustrator", "After Effects",
        "Graphic Design", "Typography", "Color Theory", "Layout Design",
        "Motion Graphics", "3D Modeling", "Blender", "Cinema 4D",
        "Responsive Design", "Design Systems", "Accessibility",
        "Interaction Design", "Information Architecture",
    ],
}

JOB_TITLES_BY_DOMAIN = {
    "software": [
        "Software Engineer", "Senior Software Engineer", "Staff Engineer",
        "Principal Engineer", "Frontend Developer", "Backend Developer",
        "Full Stack Developer", "DevOps Engineer", "SRE",
        "Mobile Developer", "iOS Developer", "Android Developer",
        "Cloud Architect", "Solutions Architect", "Technical Lead",
        "Engineering Manager", "VP of Engineering", "CTO",
        "QA Engineer", "Test Automation Engineer", "Security Engineer",
    ],
    "healthcare": [
        "Registered Nurse", "Nurse Practitioner", "Physician",
        "Surgeon", "Pharmacist", "Medical Technologist",
        "Clinical Research Coordinator", "Healthcare Administrator",
        "Medical Director", "Chief Medical Officer",
        "Physical Therapist", "Occupational Therapist",
        "Radiologic Technologist", "Lab Technician",
        "Dental Hygienist", "Paramedic", "EMT",
    ],
    "finance": [
        "Financial Analyst", "Senior Financial Analyst",
        "Investment Banker", "Portfolio Manager", "Risk Analyst",
        "Compliance Officer", "Auditor", "Tax Consultant",
        "CFO", "Controller", "Treasurer", "Credit Analyst",
        "Quantitative Analyst", "Actuary", "Wealth Manager",
        "Financial Advisor", "Accounts Manager",
    ],
    "marketing": [
        "Marketing Manager", "Digital Marketing Specialist",
        "Content Strategist", "SEO Specialist", "Social Media Manager",
        "Brand Manager", "Product Marketing Manager",
        "Growth Marketing Manager", "CMO", "Creative Director",
        "Copywriter", "Media Planner", "PR Specialist",
    ],
    "engineering": [
        "Mechanical Engineer", "Civil Engineer", "Electrical Engineer",
        "Chemical Engineer", "Industrial Engineer", "Project Engineer",
        "Design Engineer", "Process Engineer", "Quality Engineer",
        "Plant Manager", "Manufacturing Engineer",
        "Structural Engineer", "Environmental Engineer",
    ],
    "education": [
        "Teacher", "Professor", "Lecturer", "Teaching Assistant",
        "School Principal", "Dean", "Academic Advisor",
        "Curriculum Designer", "Instructional Designer",
        "Research Assistant", "Research Fellow", "Postdoctoral Researcher",
    ],
    "legal": [
        "Attorney", "Associate Attorney", "Partner",
        "Legal Counsel", "General Counsel", "Paralegal",
        "Legal Assistant", "Compliance Manager", "Contract Manager",
    ],
    "hr": [
        "HR Manager", "HR Director", "Recruiter", "Talent Acquisition Specialist",
        "HR Business Partner", "Compensation Analyst",
        "Learning and Development Manager", "CHRO",
    ],
    "data_science": [
        "Data Scientist", "Senior Data Scientist", "ML Engineer",
        "Data Engineer", "Data Analyst", "Business Intelligence Analyst",
        "AI Research Scientist", "NLP Engineer", "Computer Vision Engineer",
        "Head of Data Science", "Chief Data Officer",
    ],
    "design": [
        "UX Designer", "UI Designer", "Product Designer",
        "Graphic Designer", "Visual Designer", "Design Lead",
        "Creative Director", "UX Researcher", "Interaction Designer",
    ],
}

CREDENTIALS_BY_DOMAIN = {
    "general": [
        "B.S.", "B.A.", "M.S.", "M.A.", "MBA", "Ph.D.", "M.D.",
        "B.E.", "B.Tech", "M.Tech", "M.Eng",
    ],
    "software": [
        "AWS Certified Solutions Architect", "AWS Certified Developer",
        "Google Cloud Professional", "Azure Solutions Architect",
        "Certified Kubernetes Administrator", "CISSP",
        "CompTIA Security+", "Oracle Certified Professional",
        "Certified ScrumMaster", "PMP",
    ],
    "healthcare": [
        "RN", "BSN", "MSN", "DNP", "ACLS", "BLS", "PALS",
        "Board Certified", "USMLE", "NCLEX",
    ],
    "finance": [
        "CFA", "CPA", "FRM", "CAIA", "Series 7", "Series 63",
        "CFP", "ACCA", "CIMA",
    ],
    "engineering": [
        "PE", "FE", "PMP", "Six Sigma Green Belt", "Six Sigma Black Belt",
        "LEED AP", "Certified Quality Engineer",
    ],
    "hr": [
        "SHRM-CP", "SHRM-SCP", "PHR", "SPHR",
    ],
}

EXPERIENCE_PHRASES = [
    "{years} years of experience in {domain}",
    "{years}+ years of professional experience",
    "{years} years in {domain} industry",
    "Over {years} years of hands-on experience",
    "{years} years of expertise in {domain}",
    "Proven {years}-year track record in {domain}",
    "{years} years working in {domain}",
    "Seasoned professional with {years} years in {domain}",
]

DOMAIN_LABELS = [
    "software development", "healthcare", "financial services",
    "digital marketing", "mechanical engineering", "education",
    "legal services", "human resources", "data science",
    "product design", "civil engineering", "pharmaceutical research",
    "supply chain management", "consulting", "media production",
    "hospitality management", "real estate", "telecommunications",
    "renewable energy", "automotive engineering",
]


# ═══════════════════════════════════════════════════════════
# AUGMENTATION STRATEGIES
# ═══════════════════════════════════════════════════════════

def get_random_domain() -> str:
    """Pick a random domain for augmentation."""
    domains = list(SKILLS_BY_DOMAIN.keys())
    return random.choice(domains)


def entity_substitution(record: dict) -> dict | None:
    """
    Strategy 1: Replace entities with alternatives from the same category.
    Keeps the structure intact but changes the content.
    """
    new_rec = copy.deepcopy(record)
    tokens = new_rec["tokens"]
    tags = new_rec["bio_tags"]
    changed = False

    i = 0
    while i < len(tokens):
        tag = tags[i]

        if tag == "O":
            i += 1
            continue

        # Collect the full entity span
        entity_type = tag[2:]  # Remove B- or I-
        prefix = tag[:2]  # B- or I-
        span_start = i
        span_tokens = [tokens[i]]
        i += 1
        while i < len(tokens) and tags[i] == f"I-{entity_type}":
            span_tokens.append(tokens[i])
            i += 1
        span_end = i

        original_text = " ".join(span_tokens)

        # Generate replacement based on entity type
        replacement = None
        if entity_type == "PERSON" and prefix == "B-":
            first = random.choice(PERSON_NAMES["first"])
            last = random.choice(PERSON_NAMES["last"])
            replacement = [first, last]
        elif entity_type == "LOCATION" and prefix == "B-":
            loc = random.choice(LOCATIONS)
            replacement = loc.split()
        elif entity_type == "ORG" and prefix == "B-":
            domain = get_random_domain()
            org_key = random.choice(list(ORGANIZATIONS.keys()))
            org = random.choice(ORGANIZATIONS[org_key])
            replacement = org.split()
        elif entity_type == "SKILL" and prefix == "B-":
            domain = get_random_domain()
            skill = random.choice(SKILLS_BY_DOMAIN[domain])
            replacement = skill.split()
        elif entity_type == "JOB_TITLE" and prefix == "B-":
            domain = random.choice(list(JOB_TITLES_BY_DOMAIN.keys()))
            title = random.choice(JOB_TITLES_BY_DOMAIN[domain])
            replacement = title.split()
        elif entity_type == "CREDENTIAL" and prefix == "B-":
            cat = random.choice(list(CREDENTIALS_BY_DOMAIN.keys()))
            cred = random.choice(CREDENTIALS_BY_DOMAIN[cat])
            replacement = cred.split()

        if replacement and len(replacement) > 0 and " ".join(replacement) != original_text:
            # Replace tokens and tags
            new_tokens = tokens[:span_start] + replacement + tokens[span_end:]
            new_tags = tags[:span_start]
            new_tags.append(f"B-{entity_type}")
            for _ in range(len(replacement) - 1):
                new_tags.append(f"I-{entity_type}")
            new_tags.extend(tags[span_end:])

            tokens = new_tokens
            tags = new_tags
            i = span_start + len(replacement)
            changed = True

    if not changed:
        return None

    new_rec["tokens"] = tokens
    new_rec["bio_tags"] = tags
    new_rec["text"] = " ".join(tokens)
    # Rebuild entities from tokens+tags
    new_rec["entities"] = extract_entities_from_bio(tokens, tags)
    return new_rec


def extract_entities_from_bio(tokens: list[str], tags: list[str]) -> list[dict]:
    """Extract entity list from BIO tags."""
    entities = []
    i = 0
    char_offset = 0
    char_positions = []

    # Calculate character offsets
    for tok in tokens:
        char_positions.append(char_offset)
        char_offset += len(tok) + 1  # +1 for space

    while i < len(tokens):
        if tags[i].startswith("B-"):
            ent_type = tags[i][2:]
            start_idx = i
            i += 1
            while i < len(tokens) and tags[i] == f"I-{ent_type}":
                i += 1
            end_idx = i

            ent_text = " ".join(tokens[start_idx:end_idx])
            start_char = char_positions[start_idx]
            end_char = start_char + len(ent_text)

            entities.append({
                "text": ent_text,
                "start": start_char,
                "end": end_char,
                "label": ent_type,
            })
        else:
            i += 1

    return entities


def generate_from_template(domain: str, record_id: str) -> dict:
    """
    Strategy 2: Generate a realistic resume from templates.
    Creates complete synthetic records with proper BIO tags.
    Produces 200-500 token resumes with natural connecting text.
    """

    first = random.choice(PERSON_NAMES["first"])
    last = random.choice(PERSON_NAMES["last"])
    location = random.choice(LOCATIONS)
    email_domain = random.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'protonmail.com'])
    email = f"{first.lower()}.{last.lower()}@{email_domain}"
    phone = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

    # Pick domain-specific content
    domain_key = domain if domain in SKILLS_BY_DOMAIN else random.choice(list(SKILLS_BY_DOMAIN.keys()))
    jt_key = domain if domain in JOB_TITLES_BY_DOMAIN else random.choice(list(JOB_TITLES_BY_DOMAIN.keys()))

    job_title = random.choice(JOB_TITLES_BY_DOMAIN[jt_key])
    org_key = random.choice(list(ORGANIZATIONS.keys()))
    org1 = random.choice(ORGANIZATIONS[org_key])
    org2 = random.choice(ORGANIZATIONS[random.choice(list(ORGANIZATIONS.keys()))])
    org3 = random.choice(ORGANIZATIONS[random.choice(list(ORGANIZATIONS.keys()))])

    num_skills = random.randint(8, 16)
    skills = random.sample(SKILLS_BY_DOMAIN[domain_key],
                          min(num_skills, len(SKILLS_BY_DOMAIN[domain_key])))

    years = random.randint(2, 20)

    cred_cat = random.choice(list(CREDENTIALS_BY_DOMAIN.keys()))
    credential = random.choice(CREDENTIALS_BY_DOMAIN[cred_cat])

    location2 = random.choice(LOCATIONS)
    location3 = random.choice(LOCATIONS)
    job_title2 = random.choice(JOB_TITLES_BY_DOMAIN[
        random.choice(list(JOB_TITLES_BY_DOMAIN.keys()))
    ])
    job_title3 = random.choice(JOB_TITLES_BY_DOMAIN[
        random.choice(list(JOB_TITLES_BY_DOMAIN.keys()))
    ])

    # Build tokens and tags
    tokens = []
    tags = []

    def add_entity(text: str, label: str):
        words = text.split()
        for j, w in enumerate(words):
            tokens.append(w)
            tags.append(f"B-{label}" if j == 0 else f"I-{label}")

    def add_text(text: str):
        for w in text.split():
            tokens.append(w)
            tags.append("O")

    # Action verbs for bullet points
    action_verbs = [
        "Developed", "Implemented", "Designed", "Led", "Managed",
        "Collaborated", "Optimized", "Delivered", "Conducted", "Established",
        "Spearheaded", "Streamlined", "Architected", "Mentored", "Automated",
        "Facilitated", "Coordinated", "Analyzed", "Built", "Maintained",
    ]

    team_sizes = ["3", "5", "8", "10", "12", "15", "20", "25"]
    metrics = [
        "resulting in 30% improvement in efficiency",
        "reducing costs by 25%",
        "increasing revenue by 40%",
        "improving customer satisfaction by 35%",
        "achieving 99.9% uptime",
        "serving over 10000 daily active users",
        "decreasing response time by 50%",
        "with zero critical incidents",
        "ahead of schedule and under budget",
        "supporting business growth of 200%",
    ]

    # === HEADER ===
    add_entity(f"{first} {last}", "PERSON")
    add_text("|")
    add_entity(job_title, "JOB_TITLE")
    add_text("|")
    add_entity(location, "LOCATION")
    add_text("|")
    add_entity(email, "CONTACT")
    add_text("|")
    add_entity(phone, "CONTACT")

    # === PROFESSIONAL SUMMARY ===
    add_text("PROFESSIONAL SUMMARY")
    summary_intros = [
        f"Results-driven professional with",
        f"Highly motivated and detail-oriented specialist with",
        f"Accomplished and dedicated professional with over",
        f"Experienced and versatile professional bringing",
        f"Dynamic and innovative leader with",
    ]
    add_text(random.choice(summary_intros))
    add_entity(f"{years} years of experience in {random.choice(DOMAIN_LABELS)}", "EXPERIENCE")
    add_text(".")

    # Add 2-3 skills mentioned in context within summary
    summary_skills = random.sample(skills, min(3, len(skills)))
    skill_contexts = [
        "Proficient in {skill} with a strong background in delivering scalable solutions.",
        "Expertise in {skill} demonstrated through multiple successful projects.",
        "Skilled in {skill} and committed to continuous professional development.",
        "Deep knowledge of {skill} applied across diverse business environments.",
    ]
    for sk in summary_skills:
        ctx = random.choice(skill_contexts).split("{skill}")
        if len(ctx) == 2:
            add_text(ctx[0].strip())
            add_entity(sk, "SKILL")
            add_text(ctx[1].strip())

    # === CORE COMPETENCIES / SKILLS ===
    section_titles = ["CORE COMPETENCIES", "TECHNICAL SKILLS", "KEY SKILLS", "AREAS OF EXPERTISE"]
    add_text(random.choice(section_titles))

    # Skills in groups with connecting text
    skill_groups = [skills[i:i+4] for i in range(0, len(skills), 4)]
    group_intros = [
        "Programming Languages and Frameworks:",
        "Tools and Technologies:",
        "Methodologies and Practices:",
        "Domain Knowledge:",
    ]
    for g_idx, group in enumerate(skill_groups):
        if g_idx < len(group_intros):
            add_text(group_intros[g_idx])
        for sk in group:
            add_entity(sk, "SKILL")
            if sk != group[-1]:
                add_text(random.choice([",", "|", "-"]))

    # === WORK EXPERIENCE ===
    add_text("WORK EXPERIENCE")

    # -- Job 1 (current) --
    add_entity(job_title, "JOB_TITLE")
    add_text("|")
    add_entity(org1, "ORG")
    add_text("|")
    add_entity(location, "LOCATION")
    start_month = random.choice(["January", "March", "June", "September", "April", "July"])
    start_year = random.randint(2019, 2024)
    add_entity(f"{start_month} {start_year} - Present", "EXPERIENCE")

    # Bullet points for job 1
    num_bullets = random.randint(3, 5)
    used_skills_j1 = random.sample(skills, min(num_bullets, len(skills)))
    for b_idx in range(num_bullets):
        verb = random.choice(action_verbs)
        metric = random.choice(metrics)
        if b_idx < len(used_skills_j1):
            patterns = [
                f"{verb} and maintained robust solutions utilizing",
                f"{verb} comprehensive systems leveraging",
                f"{verb} cross-functional initiatives involving",
                f"{verb} high-impact projects featuring",
                f"{verb} enterprise-grade applications using",
            ]
            add_text(random.choice(patterns))
            add_entity(used_skills_j1[b_idx], "SKILL")
            add_text(f"{metric}.")
        else:
            add_text(f"{verb} team of {random.choice(team_sizes)} professionals {metric}.")

    # -- Job 2 (previous) --
    add_entity(job_title2, "JOB_TITLE")
    add_text("|")
    add_entity(org2, "ORG")
    add_text("|")
    add_entity(location2, "LOCATION")
    end_year = start_year - random.randint(0, 1)
    start_year2 = end_year - random.randint(2, 5)
    end_month = random.choice(["February", "May", "August", "November", "December"])
    start_month2 = random.choice(["January", "March", "June", "October"])
    add_entity(f"{start_month2} {start_year2} - {end_month} {end_year}", "EXPERIENCE")

    num_bullets2 = random.randint(2, 4)
    used_skills_j2 = random.sample(skills, min(num_bullets2, len(skills)))
    for b_idx in range(num_bullets2):
        verb = random.choice(action_verbs)
        metric = random.choice(metrics)
        if b_idx < len(used_skills_j2):
            patterns = [
                f"{verb} scalable solutions with",
                f"{verb} critical infrastructure using",
                f"{verb} and deployed systems based on",
                f"{verb} key deliverables incorporating",
            ]
            add_text(random.choice(patterns))
            add_entity(used_skills_j2[b_idx], "SKILL")
            add_text(f"{metric}.")
        else:
            add_text(f"{verb} operational processes {metric}.")

    # -- Job 3 (optional, adds length) --
    if random.random() > 0.3:
        add_entity(job_title3, "JOB_TITLE")
        add_text("|")
        add_entity(org3, "ORG")
        add_text("|")
        add_entity(location3, "LOCATION")
        end_year3 = start_year2 - random.randint(0, 1)
        start_year3 = end_year3 - random.randint(1, 4)
        add_entity(f"{random.choice(['January', 'May', 'September'])} {start_year3} - {random.choice(['March', 'July', 'December'])} {end_year3}", "EXPERIENCE")

        for _ in range(random.randint(2, 3)):
            verb = random.choice(action_verbs)
            add_text(f"{verb} departmental objectives and contributed to organizational growth {random.choice(metrics)}.")

    # === EDUCATION ===
    add_text("EDUCATION")
    add_entity(credential, "CREDENTIAL")
    add_text("in")
    major = random.choice([
        "Computer Science", "Business Administration", "Engineering",
        "Healthcare Management", "Finance", "Marketing", "Education",
        "Information Technology", "Data Science", "Economics",
        "Mechanical Engineering", "Electrical Engineering",
    ])
    add_text(major)
    edu_org = random.choice(ORGANIZATIONS["education"])
    add_entity(edu_org, "ORG")
    grad_year = start_year3 if 'start_year3' in dir() else start_year2 - random.randint(0, 2)
    add_entity(random.choice(LOCATIONS), "LOCATION")
    add_entity(f"Graduated {grad_year}", "EXPERIENCE")
    add_text(f"GPA: {random.choice(['3.5', '3.6', '3.7', '3.8', '3.9', '4.0'])}/4.0")

    # === CERTIFICATIONS ===
    if random.random() > 0.25:
        add_text("CERTIFICATIONS")
        cert_cat = domain_key if domain_key in CREDENTIALS_BY_DOMAIN else "general"
        if cert_cat in CREDENTIALS_BY_DOMAIN:
            certs = random.sample(CREDENTIALS_BY_DOMAIN[cert_cat],
                                  min(random.randint(1, 3), len(CREDENTIALS_BY_DOMAIN[cert_cat])))
            for cert in certs:
                add_entity(cert, "CREDENTIAL")
                add_text(f"- Obtained {random.randint(2018, 2024)}")

    # === ADDITIONAL SKILLS ===
    if random.random() > 0.35:
        add_text("ADDITIONAL SKILLS AND COMPETENCIES")
        other_domain = random.choice([d for d in SKILLS_BY_DOMAIN.keys() if d != domain_key])
        extra_skills = random.sample(SKILLS_BY_DOMAIN[other_domain],
                                    min(random.randint(3, 6), len(SKILLS_BY_DOMAIN[other_domain])))
        soft_skill_intros = [
            "Additional technical proficiency in",
            "Complementary experience with",
            "Also skilled in",
            "Hands-on experience with",
        ]
        add_text(random.choice(soft_skill_intros))
        for idx, s in enumerate(extra_skills):
            add_entity(s, "SKILL")
            if idx < len(extra_skills) - 1:
                add_text(random.choice(["and", ",", "as well as"]))
        add_text(".")

    # Soft skills
    if random.random() > 0.5:
        add_text("Strong interpersonal abilities including leadership communication teamwork and problem-solving.")

    text = " ".join(tokens)
    entities = extract_entities_from_bio(tokens, tags)

    return {
        "id": record_id,
        "source": f"synthetic_{domain}",
        "text": text,
        "tokens": tokens,
        "bio_tags": tags,
        "entities": entities,
    }


def section_shuffle(record: dict) -> dict | None:
    """
    Strategy 3: Reorder sections of a resume.
    Finds section boundaries (O-tagged headers) and shuffles them.
    """
    tokens = record["tokens"]
    tags = record["bio_tags"]

    # Find section boundaries (sequences of 2+ O tokens before entities)
    sections = []
    current_section_start = 0

    for i in range(1, len(tokens)):
        # Heuristic: new section starts at O token after entity
        if (tags[i] == "O" and tags[i-1].startswith(("B-", "I-"))
                and i > 5):
            sections.append((current_section_start, i))
            current_section_start = i

    if current_section_start < len(tokens):
        sections.append((current_section_start, len(tokens)))

    if len(sections) < 3:
        return None

    # Keep header (first section), shuffle the rest
    header = sections[0]
    rest = sections[1:]
    random.shuffle(rest)
    shuffled = [header] + rest

    new_tokens = []
    new_tags = []
    for start, end in shuffled:
        new_tokens.extend(tokens[start:end])
        new_tags.extend(tags[start:end])

    new_rec = copy.deepcopy(record)
    new_rec["tokens"] = new_tokens
    new_rec["bio_tags"] = new_tags
    new_rec["text"] = " ".join(new_tokens)
    new_rec["entities"] = extract_entities_from_bio(new_tokens, new_tags)
    return new_rec


# ═══════════════════════════════════════════════════════════
# MAIN AUGMENTATION PIPELINE
# ═══════════════════════════════════════════════════════════

def augment(
    input_path: str,
    output_path: str,
    target_count: int = 15000,
    seed: int = 42,
):
    """Run full augmentation pipeline."""
    random.seed(seed)

    print(f" Loading original data: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        original = [json.loads(line.strip()) for line in f if line.strip()]
    print(f"   Original records: {len(original)}")

    all_records = list(original)  # Start with originals
    aug_count = {"substitution": 0, "template": 0, "shuffle": 0}

    # -- Phase 1: Entity Substitution (2-3x originals) --
    print("\n Phase 1: Entity Substitution...")
    sub_target = min(len(original) * 3, target_count - len(all_records))
    attempts = 0
    while aug_count["substitution"] < sub_target and attempts < sub_target * 3:
        rec = random.choice(original)
        augmented = entity_substitution(rec)
        if augmented:
            augmented["id"] = f"aug_sub_{aug_count['substitution']}"
            augmented["source"] = "augmented_substitution"
            all_records.append(augmented)
            aug_count["substitution"] += 1
        attempts += 1
    print(f"   Generated: {aug_count['substitution']} records")

    # -- Phase 2: Template Generation (fill remaining) --
    print("\n Phase 2: Template Generation...")
    domains = list(SKILLS_BY_DOMAIN.keys())
    while len(all_records) < target_count:
        domain = random.choice(domains)
        rec_id = f"aug_tmpl_{aug_count['template']}"
        record = generate_from_template(domain, rec_id)
        all_records.append(record)
        aug_count["template"] += 1
    print(f"   Generated: {aug_count['template']} records")

    # -- Phase 3: Section Shuffle (bonus from originals) --
    print("\n Phase 3: Section Shuffle...")
    shuffle_target = min(len(original), 500)
    for rec in random.sample(original, min(shuffle_target, len(original))):
        shuffled = section_shuffle(rec)
        if shuffled:
            shuffled["id"] = f"aug_shuf_{aug_count['shuffle']}"
            shuffled["source"] = "augmented_shuffle"
            all_records.append(shuffled)
            aug_count["shuffle"] += 1
    print(f"   Generated: {aug_count['shuffle']} records")

    # -- Validate & Save --
    print(f"\n Validating {len(all_records)} records...")
    valid = []
    invalid = 0
    for rec in all_records:
        tokens = rec.get("tokens", [])
        tags = rec.get("bio_tags", [])
        if tokens and tags and len(tokens) == len(tags) and len(tokens) >= 5:
            valid.append(rec)
        else:
            invalid += 1

    # Shuffle all records
    random.shuffle(valid)

    print(f"   Valid: {len(valid)}, Invalid: {invalid}")

    # -- Save --
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for rec in valid:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # -- Report --
    print(f"\n{'='*60}")
    print(f"  AUGMENTATION REPORT")
    print(f"{'='*60}")
    print(f"  Original records:     {len(original)}")
    print(f"  Entity Substitution:  +{aug_count['substitution']}")
    print(f"  Template Generation:  +{aug_count['template']}")
    print(f"  Section Shuffle:      +{aug_count['shuffle']}")
    print(f"  ────────────────────────────────")
    print(f"  Total output:         {len(valid)} records")
    print(f"  Saved to:             {output_path}")

    # Domain distribution
    sources = {}
    for rec in valid:
        src = rec.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    print(f"\n  Source distribution:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"    {src}: {count}")

    return valid


def main():
    parser = argparse.ArgumentParser(description="Viora NER Data Augmentation")
    parser.add_argument("--input", type=str, required=True,
                        help="Input JSONL file (original training data)")
    parser.add_argument("--output", type=str, required=True,
                        help="Output JSONL file (augmented)")
    parser.add_argument("--target-count", type=int, default=15000,
                        help="Target total record count")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    augment(args.input, args.output, args.target_count, args.seed)


if __name__ == "__main__":
    main()
