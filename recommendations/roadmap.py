"""
Personalized learning-roadmap generation.
"""


def generate_career_roadmap(career):
    """Generate a practical learning roadmap for a career."""

    title = career.title.lower()

    roadmap_map = {
        "software engineer": [
            "Learn Python or JavaScript fundamentals",
            "Study Object-Oriented Programming",
            "Learn Data Structures and Algorithms",
            "Build web applications using Django or Node.js",
            "Learn Git, GitHub, SQL, and deployment",
            "Create 3 to 5 portfolio projects",
        ],
        "data analyst": [
            "Learn Microsoft Excel",
            "Learn SQL for data querying",
            "Study Python fundamentals",
            "Practice Pandas and NumPy",
            "Learn Power BI or Tableau",
            "Build data analysis portfolio projects",
        ],
        "ai engineer": [
            "Learn Python programming",
            "Study NumPy, Pandas, and Matplotlib",
            "Learn Machine Learning fundamentals",
            "Study Deep Learning and Neural Networks",
            "Learn TensorFlow or PyTorch",
            "Build AI, NLP, RAG, or computer vision projects",
        ],
        "machine learning engineer": [
            "Learn Python and statistics",
            "Study supervised and unsupervised learning",
            "Practice Scikit-learn",
            "Learn feature engineering and model evaluation",
            "Study deployment and MLOps",
            "Build end-to-end machine learning projects",
        ],
        "web developer": [
            "Learn HTML, CSS, and JavaScript",
            "Build responsive websites",
            "Learn React or another frontend framework",
            "Learn Django, Flask, or Node.js",
            "Study databases and REST APIs",
            "Deploy full-stack portfolio projects",
        ],
        "mobile app developer": [
            "Learn programming fundamentals",
            "Choose Flutter, React Native, Kotlin, or Swift",
            "Study mobile UI and navigation",
            "Learn APIs and local storage",
            "Build authentication and database features",
            "Publish portfolio applications",
        ],
        "sales manager": [
            "Improve communication and presentation skills",
            "Learn sales fundamentals",
            "Practice negotiation and customer handling",
            "Learn CRM tools",
            "Study sales analytics",
            "Gain team leadership experience",
        ],
        "marketing manager": [
            "Learn marketing fundamentals",
            "Study consumer behavior",
            "Learn digital marketing and social media",
            "Practice SEO and paid advertising",
            "Learn analytics and campaign reporting",
            "Build marketing campaign case studies",
        ],
        "journalist": [
            "Improve writing and grammar",
            "Learn news reporting and research",
            "Practice interviewing",
            "Study media ethics",
            "Learn digital publishing tools",
            "Build a writing portfolio",
        ],
        "photographer": [
            "Learn camera fundamentals",
            "Study lighting and composition",
            "Practice photo editing",
            "Learn Photoshop or Lightroom",
            "Build themed photography projects",
            "Create an online portfolio",
        ],
        "nutritionist": [
            "Study nutrition fundamentals",
            "Learn human anatomy and physiology",
            "Study diet planning",
            "Develop communication and counselling skills",
            "Gain practical experience",
            "Complete required professional certification",
        ],
        "business analyst": [
            "Learn business process analysis",
            "Study requirements gathering",
            "Learn SQL and Excel",
            "Practice documentation and UML",
            "Learn Power BI or reporting tools",
            "Complete business case projects",
        ],
    }

    if title in roadmap_map:
        return roadmap_map[title]

    skills = [
        skill.strip()
        for skill in career.skills.split(",")
        if skill.strip()
    ]

    roadmap = [
        f"Learn {skill}"
        for skill in skills[:5]
    ]

    roadmap.append(
        "Build practical projects and gain real-world experience"
    )

    return roadmap