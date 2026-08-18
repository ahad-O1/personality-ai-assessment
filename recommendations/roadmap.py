"""
Career Roadmap Generator Module.

Provides instant, highly structured learning roadmaps for all career paths
without blocking HTTP network calls during view rendering.
"""

import logging

logger = logging.getLogger(__name__)

ROADMAP_MAP = {
    "software engineer": [
        "Learn Python or JavaScript fundamentals",
        "Study Object-Oriented Programming & Principles",
        "Learn Data Structures and Algorithms",
        "Build web applications using Django or Node.js",
        "Master Git, GitHub, SQL databases, and deployment",
        "Create 3 to 5 full-stack portfolio projects",
    ],
    "ai engineer": [
        "Master Python programming & linear algebra",
        "Study Data Science libraries (NumPy, Pandas, Matplotlib)",
        "Learn Supervised & Unsupervised Machine Learning",
        "Study Deep Learning, Neural Networks & PyTorch/TensorFlow",
        "Build NLP, RAG, and Computer Vision applications",
        "Deploy AI models using FastAPI and Cloud APIs",
    ],
    "data scientist": [
        "Master Python, SQL, and Exploratory Data Analysis",
        "Study Probability, Statistics, and Hypothesis Testing",
        "Build Machine Learning models with Scikit-Learn",
        "Learn Data Visualization (Seaborn, Power BI, Tableau)",
        "Master Feature Engineering and Model Tuning",
        "Complete end-to-end data science portfolio projects",
    ],
    "machine learning engineer": [
        "Master Python and statistical modeling",
        "Study core supervised and unsupervised algorithms",
        "Learn Scikit-Learn, PyTorch, and Model Evaluation",
        "Study Feature Store management and Pipeline Building",
        "Learn MLOps, Docker, and Model Deployment",
        "Build scalable end-to-end ML production pipelines",
    ],
    "cybersecurity analyst": [
        "Learn Networking Fundamentals & TCP/IP Protocols",
        "Master Linux Command Line & System Administration",
        "Study Ethical Hacking, Penetration Testing & Wireshark",
        "Learn SIEM Tools, Firewalls & Threat Analysis",
        "Study Incident Response & Security Frameworks",
        "Earn CompTIA Security+ or CEH Certification",
    ],
    "web developer": [
        "Learn HTML5, CSS3, and JavaScript (ES6+)",
        "Build responsive, mobile-friendly frontend layouts",
        "Learn React.js, Vue, or modern JS frameworks",
        "Build backend REST APIs with Django or Node.js",
        "Master SQL Databases, Authentication & Security",
        "Deploy full-stack web applications on Vercel/AWS",
    ],
    "mobile app developer": [
        "Learn Mobile Development with Flutter or React Native",
        "Study Mobile UI Design Patterns & State Management",
        "Implement REST APIs, Local Storage & Push Notifications",
        "Learn Native Features (Camera, GPS, Firebase Auth)",
        "Optimize App Performance, Testing & Security",
        "Publish apps to Google Play Store & Apple App Store",
    ],
    "cloud engineer": [
        "Learn Networking, Linux System Administration & Bash",
        "Master Amazon Web Services (AWS) or Microsoft Azure",
        "Learn Infrastructure as Code (Terraform, CloudFormation)",
        "Master Containerization with Docker & Kubernetes",
        "Study Cloud Security, IAM & Cost Optimization",
        "Earn AWS Certified Solutions Architect Certification",
    ],
    "devops engineer": [
        "Learn Linux Administration, Shell Scripting & Git",
        "Master CI/CD Pipelines (GitHub Actions, Jenkins)",
        "Learn Containerization with Docker & Kubernetes",
        "Master Infrastructure as Code using Terraform & Ansible",
        "Learn System Monitoring with Prometheus & Grafana",
        "Implement Automated Cloud Deployment Pipelines",
    ],
    "database administrator": [
        "Master SQL, Relational Database Design & Normalization",
        "Study PostgreSQL, MySQL & Microsoft SQL Server",
        "Learn Query Optimization, Indexing & Execution Plans",
        "Master Database Backup, Recovery & Disaster Planning",
        "Study High Availability, Clustering & Database Security",
        "Manage enterprise multi-node database clusters",
    ],
    "ui ux designer": [
        "Study User Experience (UX) Principles & Information Architecture",
        "Master Figma, Wireframing & Interactive Prototyping",
        "Conduct User Research, Personas & Usability Testing",
        "Build Design Systems, Typography & Color Palettes",
        "Design responsive Web & Mobile UI Interfaces",
        "Build a professional UX/UI Design Portfolio",
    ],
    "graphic designer": [
        "Master Graphic Design Principles, Typography & Color Theory",
        "Learn Adobe Photoshop, Illustrator & InDesign",
        "Create Brand Identity, Logo Design & Marketing Assets",
        "Study Digital Vector Illustration & Composition",
        "Design Social Media Graphics & Print Collateral",
        "Publish an Online Design Portfolio on Behance/Dribbble",
    ],
    "animator": [
        "Study 12 Principles of Animation & Motion Theory",
        "Learn Storyboarding, Character Rigging & Keyframing",
        "Master Adobe After Effects, Blender or Maya",
        "Practice 2D & 3D Character Motion Techniques",
        "Learn Lighting, Rendering & Post-Production Editing",
        "Create a professional Animation Showreel",
    ],
    "video editor": [
        "Master Video Editing in Adobe Premiere Pro or DaVinci Resolve",
        "Study Storytelling, Pacing & Audio Syncing",
        "Learn Color Grading, Correction & Audio Noise Removal",
        "Master Motion Graphics & Visual Effects in After Effects",
        "Edit Short-Form & Long-Form Video Content",
        "Create a High-Impact Video Editing Portfolio",
    ],
    "photographer": [
        "Master Camera Settings (ISO, Aperture, Shutter Speed)",
        "Study Lighting, Composition & Rule of Thirds",
        "Learn Professional Photo Editing in Adobe Lightroom",
        "Practice Portrait, Product & Event Photography",
        "Build a Curated Online Photography Portfolio",
        "Set up Commercial Studio Operations & Client Management",
    ],
    "content writer": [
        "Improve English Grammar, Style & Tone Versatility",
        "Learn Search Engine Optimization (SEO) Writing Rules",
        "Practice Blog Posts, Articles & Technical Writing",
        "Learn Copywriting for Landing Pages & Ads",
        "Study Content Strategy & Keyword Research Tools",
        "Build a Published Portfolio on Medium or Personal Website",
    ],
    "journalist": [
        "Study News Gathering, Fact-Checking & Investigative Research",
        "Improve Interviewing Skills & Media Ethics",
        "Practice News Writing for Digital & Print Media",
        "Learn Digital Publishing Tools & Mobile Journalism",
        "Build Relationships with Industry Sources",
        "Publish Articles & Investigative Reporting Pieces",
    ],
    "digital marketing specialist": [
        "Learn Digital Marketing Fundamentals & Funnels",
        "Master SEO, Keyword Strategy & Google Search Console",
        "Learn Social Media Marketing & Paid Ads (Meta, Google Ads)",
        "Master Email Marketing & Lead Nurturing Campaigns",
        "Learn Google Analytics 4 & Campaign ROI Tracking",
        "Manage Real Digital Marketing Campaigns & Case Studies",
    ],
    "doctor": [
        "Complete Medical Degree (MBBS / MD)",
        "Master Human Anatomy, Physiology & Pathology",
        "Complete Clinical Rotations & Hospital Internship",
        "Pass National Medical Licensing Examinations",
        "Specialize in Selected Medical Subfield",
        "Obtain Medical Registration & Practice Medicine",
    ],
    "surgeon": [
        "Complete Undergraduate Medical Degree (MBBS/MD)",
        "Complete Clinical Surgical Residency & Rotations",
        "Master Surgical Techniques, Anatomy & Patient Care",
        "Pass Surgical Board Licensing Examinations",
        "Complete Specialized Surgical Fellowship",
        "Perform Supervised Surgical Operations & Practice",
    ],
    "dentist": [
        "Complete Bachelor of Dental Surgery (BDS)",
        "Master Dental Anatomy, Diagnostics & Oral Surgery",
        "Complete Clinical Dental Residency Internship",
        "Obtain Dental Board Licensing & Registration",
        "Learn Dental Practice Management & Patient Care",
        "Establish or Join a Professional Dental Clinic",
    ],
    "pharmacist": [
        "Complete Doctor of Pharmacy (PharmD) Degree",
        "Master Pharmacology, Medicinal Chemistry & Dosage",
        "Complete Clinical Pharmacy & Hospital Internship",
        "Pass Pharmacy Council Licensing Examination",
        "Learn Patient Counseling & Prescription Safety",
        "Practice in Community or Clinical Pharmacy Settings",
    ],
    "nurse": [
        "Complete Nursing Degree (BSN / RN)",
        "Master Patient Care, Triage & Medical Equipment",
        "Complete Hospital Nursing Clinical Rotations",
        "Pass Nursing Board Licensing Examination",
        "Develop Patient Communication & Critical Care Skills",
        "Practice Professional Nursing in Hospital Setting",
    ],
    "physiotherapist": [
        "Complete Bachelor of Physical Therapy (DPT)",
        "Master Musculoskeletal Anatomy & Biomechanics",
        "Complete Clinical Rehabilitation Internship",
        "Obtain Physical Therapy Council Licensing",
        "Develop Customized Patient Treatment & Exercise Plans",
        "Practice Physical Therapy in Clinic or Sports Setting",
    ],
    "nutritionist": [
        "Complete Degree in Clinical Nutrition & Dietetics",
        "Master Human Metabolism & Nutritional Biochemistry",
        "Learn Personalized Meal Planning & Dietary Assessment",
        "Complete Hospital Clinical Internship",
        "Obtain Registered Dietitian/Nutritionist Credentials",
        "Provide Nutritional Counseling & Wellness Coaching",
    ],
    "psychologist": [
        "Complete Degree in Clinical Psychology",
        "Master Cognitive Behavioral Therapy & Diagnostics",
        "Complete Clinical Psychology Supervised Internship",
        "Obtain Professional Licensing & Registration",
        "Master Psychological Assessment & Counseling",
        "Conduct Therapy Sessions & Clinical Practice",
    ],
    "teacher": [
        "Complete Bachelor of Education (B.Ed) or Subject Degree",
        "Master Curriculum Design & Classroom Pedagogy",
        "Develop Lesson Planning & Student Evaluation Skills",
        "Complete Supervised Student Teaching Practice",
        "Earn State Teaching Certification & License",
        "Teach in Elementary, Secondary or High School Settings",
    ],
    "lecturer": [
        "Complete Master's Degree in Academic Field",
        "Develop Higher Education Pedagogy & Lecture Skills",
        "Design University Course Syllabi & Assessments",
        "Publish Academic Research Papers",
        "Gain University Teaching & Assistantship Experience",
        "Obtain University Faculty Appointment",
    ],
    "professor": [
        "Complete Ph.D. in Specialized Academic Discipline",
        "Publish Original Research in Peer-Reviewed Journals",
        "Secure Research Grants & Academic Funding",
        "Teach Undergraduate & Post-Graduate Courses",
        "Supervise Ph.D. Candidates & Research Thesis Work",
        "Attain Tenured Professorship & Academic Leadership",
    ],
    "researcher": [
        "Complete Postgraduate Degree (M.S. or Ph.D.)",
        "Master Quantitative & Qualitative Research Methods",
        "Conduct Literature Reviews & Experimental Studies",
        "Master Statistical Analysis Software (SPSS, R, Python)",
        "Publish Research Papers in Peer-Reviewed Journals",
        "Present Research Findings at International Conferences",
    ],
    "hr manager": [
        "Learn Human Resource Management Fundamentals",
        "Master Talent Acquisition, Recruitment & Onboarding",
        "Study Labor Laws, Compliance & Workplace Policies",
        "Learn Performance Management & Employee Engagement",
        "Master HR Software (HRIS, Workday, BambooHR)",
        "Lead HR Operations & Organizational Development",
    ],
    "marketing manager": [
        "Learn Strategic Marketing & Brand Management",
        "Master Market Research, Competitor Analysis & Segmentation",
        "Plan Integrated Marketing Campaigns (Digital & Offline)",
        "Manage Marketing Budgets & Campaign Analytics",
        "Lead Creative Teams, Copywriters & Designers",
        "Drive Business Growth & Customer Acquisition Strategy",
    ],
    "business analyst": [
        "Learn Business Process Modeling & Requirements Gathering",
        "Master SQL, Excel & Data Modeling",
        "Learn Wireframing & Documentation (BRD, FRD, User Stories)",
        "Master Data Visualization in Power BI or Tableau",
        "Learn Agile / Scrum Methodologies & Jira",
        "Bridge Gaps Between Business Teams & Software Developers",
    ],
    "financial analyst": [
        "Master Financial Modeling, Valuation & Accounting",
        "Learn Advanced Microsoft Excel (VBA, Financial Functions)",
        "Study Corporate Finance, Capital Budgeting & Cash Flow",
        "Master Financial Statement Analysis (P&L, Balance Sheet)",
        "Learn Financial Forecasting & Investment Analysis",
        "Prepare Financial Reports & Strategic Recommendations",
    ],
    "sales manager": [
        "Master Sales Strategy, Pipeline Management & Pitching",
        "Learn Lead Generation, Qualification & Closing Skills",
        "Master CRM Software (Salesforce, HubSpot)",
        "Learn Team Coaching, Territory Planning & Quota Management",
        "Develop Client Relationships & High-Value Negotiations",
        "Drive Enterprise Revenue Growth & Sales Operations",
    ],
    "project manager": [
        "Master Project Management Methodologies (Agile, Waterfall, Scrum)",
        "Learn Scope Management, WBS & Scheduling",
        "Master Project Management Tools (Jira, Asana, MS Project)",
        "Learn Risk Assessment, Budgeting & Resource Allocation",
        "Earn PMP (Project Management Professional) or CAPM Certification",
        "Deliver Complex Projects On Time & Within Budget",
    ],
    "civil engineer": [
        "Complete Bachelor's Degree in Civil Engineering",
        "Master Structural Analysis & Fluid Mechanics",
        "Learn AutoCAD, Revit & Civil Design Software",
        "Study Construction Management & Site Safety",
        "Earn Professional Engineer (PE) License",
        "Supervise Infrastructure & Building Projects",
    ],
    "mechanical engineer": [
        "Complete Degree in Mechanical Engineering",
        "Master Thermodynamics, Fluid Dynamics & CAD",
        "Learn SolidWorks, ANSYS & Finite Element Analysis",
        "Study Manufacturing Processes & Materials Science",
        "Design Mechanical Components & Prototyping",
        "Execute Engineering Projects & Quality Testing",
    ],
    "electrical engineer": [
        "Complete Degree in Electrical Engineering",
        "Master Circuit Theory, Power Systems & Electronics",
        "Learn MATLAB, LabVIEW & Electrical CAD",
        "Study Embedded Systems & Microcontrollers",
        "Design Power Distribution or Electronic Hardware",
        "Complete Engineering Projects & Safety Testing",
    ],
    "architect": [
        "Complete Bachelor of Architecture (B.Arch) Degree",
        "Master Architectural Design & Building Codes",
        "Learn AutoCAD, Revit, SketchUp & 3D Rendering",
        "Study Sustainable Building & Structural Systems",
        "Complete Architecture Firm Internship Hours",
        "Earn Architect License & Design Building Projects",
    ],
    "lawyer": [
        "Complete Law Degree (LL.B. / J.D.)",
        "Master Legal Research, Case Analysis & Writing",
        "Study Constitutional, Civil & Criminal Law",
        "Pass Bar Examination & Obtain Law License",
        "Practice Trial Advocacy & Client Representation",
        "Represent Clients in Legal Disputes & Courtroom",
    ],
    "police officer": [
        "Complete Police Academy Training & Law Program",
        "Master Criminal Law, Evidence & Public Safety",
        "Complete Physical Fitness & Defensive Tactics Training",
        "Learn Patrol Operations & Emergency Response",
        "Practice Incident Reporting & Community Policing",
        "Maintain Public Order & Investigate Crimes",
    ],
    "pilot": [
        "Obtain Student Pilot Certificate & Medical Fitness Pass",
        "Earn Private Pilot License (PPL) Flight Hours",
        "Earn Instrument Rating (IR) & Commercial Pilot License (CPL)",
        "Complete Multi-Engine Flight Training Hours",
        "Pass Airline Transport Pilot (ATP) Examinations",
        "Fly Commercial Airlines or Corporate Aircraft",
    ],
}


def generate_career_roadmap(career):
    """
    Generate a practical learning roadmap for a career INSTANTLY
    without making slow HTTP network calls during view rendering.
    """
    title = career.title.strip().lower()

    if title in ROADMAP_MAP:
        return ROADMAP_MAP[title]

    # Partial title matching fallback
    for key, steps in ROADMAP_MAP.items():
        if key in title or title in key:
            return steps

    # Skill-based fallback generation (Instant execution)
    skills = [
        s.strip()
        for s in career.skills.split(",")
        if s.strip()
    ]

    roadmap = [
        f"Learn {skill} fundamentals & best practices"
        for skill in skills[:4]
    ]

    if len(roadmap) < 4:
        roadmap.append(f"Study core concepts of {career.title}")
        roadmap.append("Develop hands-on technical proficiency")

    roadmap.append("Build real-world portfolio projects")
    roadmap.append(f"Prepare for {career.title} interviews & placement")

    return roadmap[:6]


import urllib.parse


def get_step_subtopics(step_text):
    text = step_text.lower()

    if "excel" in text:
        return [
            "Cell Formatting, Formulas (SUM, AVERAGE, IF) & Data Entry",
            "Advanced Functions (VLOOKUP, XLOOKUP, INDEX MATCH)",
            "Pivot Tables, Interactive Charts & Dashboards",
        ]
    elif "sql" in text:
        return [
            "SELECT Queries, WHERE Clauses, ORDER BY & Filtering",
            "JOIN Operations (INNER, LEFT, RIGHT) & GroupBy Aggregations",
            "Database Schema Design, Subqueries & Window Functions",
        ]
    elif "python" in text:
        return [
            "Python Syntax, Variables, Control Flow & Data Types",
            "Functions, Modules & Object-Oriented Programming (OOP)",
            "File Handling, Virtual Environments & Package Management (pip)",
        ]
    elif "pandas" in text or "data science" in text or "analytics" in text:
        return [
            "Data Cleaning, Handling Missing Values & Type Conversion",
            "Exploratory Data Analysis (EDA) & Data Wrangling",
            "Data Visualization with Seaborn, Matplotlib & Plotly",
        ]
    elif "machine learning" in text or "ml" in text or "ai" in text:
        return [
            "Supervised Learning (Regression & Classification Algorithms)",
            "Feature Engineering, Scaling & Model Evaluation Metrics",
            "Model Hyperparameter Tuning, PyTorch & Deployment",
        ]
    elif "web" in text or "django" in text or "html" in text or "react" in text:
        return [
            "HTML5 Structure, CSS3 Flexbox & Grid Responsive Layouts",
            "JavaScript ES6+ Syntax, DOM Manipulation & Fetch API",
            "Backend REST APIs, Database Models & Authentication",
        ]
    elif "portfolio" in text or "project" in text:
        return [
            "Selecting Real-World Industry Problems & Datasets",
            "Writing Clean Modular Code with Documentation & README",
            "Deploying Applications Live on Vercel, GitHub Pages or AWS",
        ]
    elif "interview" in text or "placement" in text or "cv" in text:
        return [
            "Building a Tailored Resume & Optimizing LinkedIn Profile",
            "Practicing Technical & Behavioral Interview Questions",
            "Networking, Mock Interviews & Job Application Strategy",
        ]
    else:
        return [
            f"Core Concepts & Foundational Principles of {step_text[:35]}",
            "Practical Exercises & Hands-on Case Studies",
            "Industry Best Practices, Tools & Applied Skills",
        ]


from urllib.parse import quote


def get_step_youtube_resource(step_text, career_title):
    """
    Dynamically generates YouTube search results links that pre-fill YouTube's search bar
    with the exact step title and target career role keyword, preventing broken video errors.
    """
    clean_step = (step_text or "").strip()
    clean_title = (career_title or "").strip()

    query_str = f"{clean_step} {clean_title} full course tutorial"
    encoded_query = quote(query_str)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

    return {
        "channel": f"YouTube: {clean_step[:30]}...",
        "url": search_url,
        "alt_1": search_url,
        "alt_2": search_url,
    }




def get_embed_url(yt_url):
    """Convert standard YouTube watch/playlist URLs into privacy-enhanced embeddable URLs."""
    if "watch?v=" in yt_url:
        video_id = yt_url.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
    elif "playlist?list=" in yt_url:
        list_id = yt_url.split("playlist?list=")[-1].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/videoseries?list={list_id}&rel=0"
    else:
        return "https://www.youtube-nocookie.com/embed/kqtD5dpn9C8?rel=0"


def generate_structured_roadmap(career):
    """
    Generate enriched node-graph roadmap structure with phase titles,
    estimated duration, subtopics list, and YouTube video search link.
    """
    raw_steps = generate_career_roadmap(career)
    phases = [
        "Phase 1: Fundamentals & Concepts",
        "Phase 2: Core Skill Development",
        "Phase 3: Applied Tools & Libraries",
        "Phase 4: Advanced Architecture",
        "Phase 5: Real-World Portfolio Project",
        "Phase 6: Placement & Practice",
    ]
    durations = ["Weeks 1-3", "Weeks 4-7", "Weeks 8-11", "Weeks 12-15", "Weeks 16-19", "Weeks 20+"]
    resources = ["Video Courses & Docs", "Hands-on Tutorials", "Build Project & Practice", "Advanced Guides", "GitHub Open Source", "Mock Interviews & CV"]

    nodes = []
    for idx, step_text in enumerate(raw_steps):
        phase = phases[idx] if idx < len(phases) else f"Phase {idx+1}"
        duration = durations[idx] if idx < len(durations) else "2-4 Weeks"
        resource = resources[idx] if idx < len(resources) else "Guided Practice"
        subtopics = get_step_subtopics(step_text)
        yt_data = get_step_youtube_resource(step_text, career.title)
        embed_url = get_embed_url(yt_data["url"])
        alt_embed_1 = get_embed_url(yt_data.get("alt_1", yt_data["url"]))
        alt_embed_2 = get_embed_url(yt_data.get("alt_2", yt_data["url"]))

        nodes.append({
            "index": idx,
            "phase": phase,
            "title": step_text,
            "duration": duration,
            "resource": resource,
            "subtopics": subtopics,
            "youtube_url": yt_data["url"],
            "youtube_embed_url": embed_url,
            "alt_embed_url_1": alt_embed_1,
            "alt_embed_url_2": alt_embed_2,
            "youtube_channel": yt_data["channel"],
        })

    return nodes