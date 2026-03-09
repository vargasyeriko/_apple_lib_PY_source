# -----######-----###### CORE IMPORTABLE FUNCTION (Generate Data Science Portfolio PDF) -----######-----###### #

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


def _portfolio_0803_ds_consultant_GET_pdf():

    # -----------------------
    # VARIABLES
    # -----------------------

    output_path = "portfolio_ds_consultant.pdf"

    name = "Yeriko Vargas"
    title = "Data Science Consultant | Python | Statistics | Machine Learning"
    location = "Detroit, MI"
    email = "yeriko@email.com"
    linkedin = "https://linkedin.com/in/yeriko_vargas"
    github = "https://github.com/yeriko"

    intro_text = """
    Applied statistician and data scientist specializing in predictive modeling,
    analytics pipelines, and automation using Python. Experienced building
    scalable data workflows and helping students and businesses understand
    data-driven decision making.
    """

    # -----------------------
    # CONSULTING PROJECTS
    # -----------------------

    consulting_projects = [
        ("Retail Demand Forecasting", "Python / Prophet / Pandas",
         "Forecast demand for retail products using time series models.",
         "https://fake-link.com/project/forecasting_01"),

        ("Vehicle Pricing Analysis", "Python / SQL",
         "Built pricing anomaly detection model for automotive market data.",
         "https://fake-link.com/project/vehicle_pricing"),

        ("Customer Segmentation", "Python / Scikit-learn",
         "Clustered customers based on purchase behavior.",
         "https://fake-link.com/project/customer_segmentation"),

        ("Financial Time Series Modeling", "Python / Statsmodels",
         "Modeled stock returns and volatility patterns.",
         "https://fake-link.com/project/financial_models"),

        ("ETL Analytics Pipeline", "Python / Airflow",
         "Automated data ingestion and analytics reporting pipeline.",
         "https://fake-link.com/project/etl_pipeline")
    ]

    # -----------------------
    # MACHINE LEARNING PROJECTS
    # -----------------------

    ml_projects = [
        ("Fraud Detection Model", "Python / Random Forest",
         "Predict fraudulent financial transactions.",
         "https://fake-link.com/project/fraud_model"),

        ("Sales Prediction Model", "Python / XGBoost",
         "Forecast future product demand using historical sales.",
         "https://fake-link.com/project/sales_prediction"),

        ("Recommendation Engine", "Python / Collaborative Filtering",
         "Recommend products based on user similarity.",
         "https://fake-link.com/project/recommendation_engine"),

        ("Customer Churn Prediction", "Python / Logistic Regression",
         "Predict customers likely to leave subscription services.",
         "https://fake-link.com/project/churn_model"),

        ("Price Optimization Model", "Python / ML",
         "Estimate optimal pricing strategies using ML models.",
         "https://fake-link.com/project/price_optimization")
    ]

    # -----------------------
    # DATA ANALYSIS PROJECTS
    # -----------------------

    analysis_projects = [
        ("SQL Data Warehouse Analysis", "SQL / Python",
         "Query and analyze warehouse scale datasets.",
         "https://fake-link.com/project/sql_analysis"),

        ("Marketing Campaign Analysis", "Python / Pandas",
         "Analyze campaign performance and ROI.",
         "https://fake-link.com/project/marketing_analysis"),

        ("Automotive Market Trends", "Python / Visualization",
         "Analyze vehicle sales and demand patterns.",
         "https://fake-link.com/project/automotive_trends"),

        ("Customer Behavior Analysis", "Python / Pandas",
         "Understand purchasing patterns and user activity.",
         "https://fake-link.com/project/customer_behavior"),

        ("Operational KPI Dashboard", "Python / BI",
         "Track business performance metrics.",
         "https://fake-link.com/project/kpi_dashboard")
    ]

    # -----------------------
    # PYTHON AUTOMATION PROJECTS
    # -----------------------

    automation_projects = [
        ("Data Cleaning Automation", "Python",
         "Automate messy dataset processing pipelines.",
         "https://fake-link.com/project/data_cleaning"),

        ("File Processing System", "Python",
         "Batch processing pipeline for large datasets.",
         "https://fake-link.com/project/file_processing"),

        ("ETL Script Generator", "Python",
         "Generate reusable ETL pipelines.",
         "https://fake-link.com/project/etl_scripts"),

        ("API Data Collector", "Python",
         "Collect and process external API data.",
         "https://fake-link.com/project/api_collector"),

        ("Automated Reporting Tool", "Python",
         "Generate PDF and CSV reports automatically.",
         "https://fake-link.com/project/reporting_tool")
    ]

    # -----------------------
    # TUTORING PROJECTS
    # -----------------------

    tutoring_topics = [
        ("Python for Data Science", "Teach Pandas, NumPy, and real datasets",
         "https://fake-link.com/tutoring/python"),

        ("Statistics Fundamentals", "Regression, probability, inference",
         "https://fake-link.com/tutoring/statistics"),

        ("Machine Learning Basics", "Supervised learning and model building",
         "https://fake-link.com/tutoring/ml_basics"),

        ("SQL for Analysts", "Database querying and joins",
         "https://fake-link.com/tutoring/sql"),

        ("Data Science Interview Prep", "Technical interview preparation",
         "https://fake-link.com/tutoring/interview_prep")
    ]

    # -----------------------
    # PDF CREATION
    # -----------------------

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(name, styles['Title']))
    story.append(Paragraph(title, styles['Heading2']))
    story.append(Paragraph(location, styles['Normal']))
    story.append(Paragraph(email, styles['Normal']))
    story.append(Paragraph(linkedin, styles['Normal']))
    story.append(Paragraph(github, styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(intro_text, styles['BodyText']))
    story.append(Spacer(1, 30))

    def add_section(title, projects):
        story.append(Paragraph(title, styles['Heading2']))
        story.append(Spacer(1, 10))

        table_data = [["Project", "Tools", "Description", "Link"]]

        for p in projects:
            table_data.append(list(p))

        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 3*inch, 2*inch])
        story.append(table)
        story.append(Spacer(1, 25))

    add_section("Consulting Projects", consulting_projects)
    add_section("Machine Learning Projects", ml_projects)
    add_section("Data Analysis Projects", analysis_projects)
    add_section("Python Automation Projects", automation_projects)
    add_section("Tutoring Topics", tutoring_topics)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    doc.build(story)

    print("PDF generated:", output_path)