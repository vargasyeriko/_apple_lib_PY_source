import pandas as pd

# Creating the DataFrame from the provided skill set
data = [
    
    # General skills
    ("Machine Learning Proficiency", "Developing and implementing complex ML algorithms, focus on NLP, predictive modeling, automated code generation", "GRAL"),
    ("Data Linguistics Competence", "Strong foundation in data linguistics for analyzing language-based datasets", "GRAL"),
    ("Image Data Analysis", "Proficient in processing and interpreting visual data sets, utilizing image analysis techniques", "GRAL"),
    ("Proficiency in Python", "Advanced skills in Python for data analysis, model building, algorithm development", "GRAL"),
    ("Analytical Project Leadership", "Leading and managing data-driven projects, ensuring timely delivery, balancing multiple priorities", "GRAL"),
    # Other general skills...
    
    # CAI | Detroit, MI - ML/AI Data Scientist
    ("Financial Forecasting and Analysis", "Developed algorithms using Python and deep learning for financial forecasting", "CAI"),
    ("Advanced Audio Data Analytics", "Built Python pipelines for enhanced podcast content quality", "CAI"),
    ("NLP and Sentiment Analysis Expertise", "Utilized NLP for market predictions via social media analysis", "CAI"),
    ("Voice Assistant Development", "Created voice assistants for automated episode summaries using ML", "CAI"),
    ("Large Language Model Application", "Implemented LLMs for diverse analytical tasks", "CAI"),

    # FORD | Dearborn, MI - Lead Data Scientist
    ("Big Data Management", "Managed large datasets using Python and AWS SageMaker", "FORD"),
    ("Data Visualization and Reporting", "Transformed and visualized data for statistical reporting", "FORD"),
    ("Machine Learning Solutions", "Developed ML solutions for automotive defect identification", "FORD"),
    ("Data Automation", "Automated data transfer processes to improve efficiency", "FORD"),
    ("Collaborative Problem Solving", "Collaborated with engineers for data-driven solutions", "FORD"),

    # Soothsayer Analytics | Livonia, MI - Junior AI and ML Analyst
    ("Fraud Detection Methodologies", "Researched ML methods for fraud detection in auto and insurance sectors", "SA"),
    ("Data Mining and Preprocessing", "Performed data mining and preprocessing for ML model outputs", "SA"),
    ("Model Interpretability and Tuning", "Enhanced model accuracy using SHAP and LLMs", "SA"),
    ("Anomaly Detection", "Identified fraudulent activities through anomaly detection", "SA"),
    ("Advanced Data Visualization", "Excelled in complex data visualization using Tableau, matplotlib, Power BI", "SA"),

    # Official Driving School | Royal Oak, MI - Business Data Analyst with AI Expertise
    ("Data Visualization and Dashboard Development", "Crafted dynamic dashboards using pivot tables and ggplot2", "ODS"),
    ("Sales Prediction Modeling", "Developed R-Keras models for sales trend predictions", "ODS"),
    ("Business Intelligence Integration", "Blended AI strategies with traditional business intelligence", "ODS"),
    ("Data Infrastructure Establishment", "Established robust data infrastructure for data analysis", "ODS"),
    ("Strategic Data Analysis", "Analyzed business trends for strategic decision-making", "ODS"),

    # Fiat Chrysler Automotive | Auburn Hills, MI - Deep Learning Analyst
    ("Deep Learning for Profit Optimization", "Developed models for forecasting profitable configurations using R-Keras", "FCA"),
    ("AI Model Construction and Testing", "Tested various AI models for automotive analytics", "FCA"),
    ("Data-Driven Production Adjustments", "Adjusted car production based on data analysis", "FCA"),
    ("Neural Network Application", "Applied neural networks for automotive storage optimization", "FCA"),
    ("Data Validation and Analysis", "Validated and analyzed automotive data using Python packages", "FCA")
]

# Column names
columns = ['Skill', 'Description', 'CODE']


# Creating the DataFrame
df = pd.DataFrame(data, columns=columns)

# Rearranging the DataFrame to have 'CODE' as the first column
rearranged_columns = ['CODE', 'Skill', 'Description']
df = df[rearranged_columns]

import pyperclip



# Iterate through each row
for index, row in df.iterrows():
    # Ask user to input once per row, just press Enter to continue
    input(f"\n\n # <E> to start for company CODE : {row['CODE']} \n")
    
    # Iterate over each column from the second column onwards
    for col in df.columns[1:]:  # Skipping the first 'CODE' column
        print(f"COPIED field : {col} @{row['CODE']} \t::: {row[col]}")
        
        # Copy the value to clipboard
        pyperclip.copy(str(row[col]))

        # Ask user to press Enter between each column's value within the same row
        if col != df.columns[-1]:  # No input after the last column
            input("\n<E>< next >\n")

print("Done")
