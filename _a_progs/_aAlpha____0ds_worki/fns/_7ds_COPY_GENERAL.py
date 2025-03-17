import pandas as pd

# Creating a dictionary with the provided information
data = {
    "CODE": ["GRAL_INFO"],
    "Title": ["Mr."],
    "First Name": ["Yeriko"],
    "Middle": ["Ghebra"],
    "Last Name": ["Vargas"],
    "Suffix": ["na"],
    "Former Name": ["na"],
    "Primary Phone": ["6467716111"],
    "Secondary Phone": ["na"],
    "Country": ["United States"],
    "Address 1": ["1365 Southfield Rd."],
    "Address 2": ["na"],
    "City": ["Birmingham"],
    "State / Province": ["Michigan"],
    "Zip / Postal Code": ["48009"],
    "Willing to relocate": ["yes"],

}


# Converting the dictionary into a DataFrame


import pandas as pd
df = pd.DataFrame(data)

import pandas as pd
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

print("\n\n\n\n\n\n\n\n*Done - with - GENERAL \n\n")

# READ CUSTOM EXPERIENCES
cust_desc_path = '/Users/yerik/_apple_source/all_data/temp/_0ds/_0_ds_Employment'

# Read the content of the file CAI
with open(f'{cust_desc_path}/CAI_custom_task_desk.txt', "r") as file:
    cai_cust_desc = file.read()

# Read the content of the file FORD
with open(f'{cust_desc_path}/FORD_custom_task_desk.txt', "r") as file:
    ford_cust_desc = file.read()

# Read the content of the file SA
with open(f'{cust_desc_path}/SA_custom_task_desk.txt', "r") as file:
    sa_cust_desc = file.read()

# Read the content of the file ODS
with open(f'{cust_desc_path}/ODS_custom_task_desk.txt', "r") as file:
    ods_cust_desc = file.read()

# Read the content of the file FCA
with open(f'{cust_desc_path}/FCA_custom_task_desk.txt', "r") as file:
    fca_cust_desc = file.read()



data = {
    'CODE': ["CAI", "FORD", "SA", "ODS", "FCA"],
    'Job Title': [
        "ML/AI Data Scientist", 
        "Lead Data Scientist (contract)", 
        "Junior AI and Machine Learning Analyst - Automotive & Insurance (full time)", 
        "Business Data Analyst with AI Expertise (contract)", 
        "Deep Learning Analyst - Automotive Optimization (contract)"
    ],
    'Company': [
        "Creative Audio Innovations", 
        "FORD", 
        "Soothsayer Analytics", 
        "Official Driving School", 
        "Fiat Chrysler Automotive"
    ],
    'Location': [
        "Detroit, MI", 
        "Dearborn, MI", 
        "Livonia, MI", 
        "Royal Oak, MI", 
        "Auburn Hills, MI"
    ],
    'From': ["12/2023", "03/2022", "05/2021", "08/2020", "06/2019"],
    'To': ["Present", "11/2023", "02/2022", "04/2021", "04/2020"],


    
    'Role Description': [
        f"At CAI, my role as an ML/AI Data Scientist involved developing sophisticated financial forecasting algorithms using Python and Deep Learning. I leveraged Large Language Models for sentiment analysis of tweets and news, enhancing price predictions. I built efficient Python pipelines incorporating TensorFlow and scikit-learn for audio data analytics and NLP. A key contribution was the creation of a Voice Assistant for podcast episode summaries and recommendations, highlighting my skills in audio categorization and premium revenue analytics. \n <<{cai_cust_desc}>> ", 

        
        f"As Lead Data Scientist at FORD, I managed large datasets from the CVDOS database, utilizing Python and AWS SageMaker. My responsibilities included data transformation, visualization, and daily statistical reporting. I collaborated on machine learning projects for identifying car defects using Cluster Analysis and PCA methodology, and automated data transfer processes, reducing human error and enhancing efficiency. \n <<{ford_cust_desc}>>  ", 

        
        f"At Soothsayer Analytics, I focused on applying Machine Learning to fraud detection and customer segmentation. I used Python for data mining and visualization, improving model accuracy with SHAP and Random Forest models. My role involved anomaly detection in service shops across 500 locations, using tools like Tableau, matplotlib, and Power BI for effective visualization.\n <<{sa_cust_desc}>> ", 

        
        f"At Official Driving School, I leveraged data visualization tools like pivot tables and ggplot2 in Rstudio to create dynamic business dashboards. My role included developing R-Keras machine learning models to forecast sales and optimize marketing strategies, blending business intelligence with AI-driven approaches for enhanced outcomes.\n <<{ods_cust_desc}>> ", 

        
        f"My role as a Deep Learning Analyst at Fiat Chrysler Automotive involved developing models using R-Keras and Python to forecast profitable vehicle configurations. I analyzed data from half a million vehicles, applying Neural Networks to optimize automotive storage, significantly saving costs by identifying optimal car configurations.\n <<{fca_cust_desc}>> "
    ]
}

import pandas as pd
df = pd.DataFrame(data)

import pandas as pd
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

# import pandas as pd

# # Creating the DataFrame from the provided skill set
# data = [
    
#     # General skills
#     ("Machine Learning Proficiency", "Developing and implementing complex ML algorithms, focus on NLP, predictive modeling, automated code generation", "GRAL"),
#     ("Data Linguistics Competence", "Strong foundation in data linguistics for analyzing language-based datasets", "GRAL"),
#     ("Image Data Analysis", "Proficient in processing and interpreting visual data sets, utilizing image analysis techniques", "GRAL"),
#     ("Proficiency in Python", "Advanced skills in Python for data analysis, model building, algorithm development", "GRAL"),
#     ("Analytical Project Leadership", "Leading and managing data-driven projects, ensuring timely delivery, balancing multiple priorities", "GRAL"),
#     # Other general skills...
    
#     # CAI | Detroit, MI - ML/AI Data Scientist
#     ("Financial Forecasting and Analysis", "Developed algorithms using Python and deep learning for financial forecasting", "CAI"),
#     ("Advanced Audio Data Analytics", "Built Python pipelines for enhanced podcast content quality", "CAI"),
#     ("NLP and Sentiment Analysis Expertise", "Utilized NLP for market predictions via social media analysis", "CAI"),
#     ("Voice Assistant Development", "Created voice assistants for automated episode summaries using ML", "CAI"),
#     ("Large Language Model Application", "Implemented LLMs for diverse analytical tasks", "CAI"),

#     # FORD | Dearborn, MI - Lead Data Scientist
#     ("Big Data Management", "Managed large datasets using Python and AWS SageMaker", "FORD"),
#     ("Data Visualization and Reporting", "Transformed and visualized data for statistical reporting", "FORD"),
#     ("Machine Learning Solutions", "Developed ML solutions for automotive defect identification", "FORD"),
#     ("Data Automation", "Automated data transfer processes to improve efficiency", "FORD"),
#     ("Collaborative Problem Solving", "Collaborated with engineers for data-driven solutions", "FORD"),

#     # Soothsayer Analytics | Livonia, MI - Junior AI and ML Analyst
#     ("Fraud Detection Methodologies", "Researched ML methods for fraud detection in auto and insurance sectors", "SA"),
#     ("Data Mining and Preprocessing", "Performed data mining and preprocessing for ML model outputs", "SA"),
#     ("Model Interpretability and Tuning", "Enhanced model accuracy using SHAP and LLMs", "SA"),
#     ("Anomaly Detection", "Identified fraudulent activities through anomaly detection", "SA"),
#     ("Advanced Data Visualization", "Excelled in complex data visualization using Tableau, matplotlib, Power BI", "SA"),

#     # Official Driving School | Royal Oak, MI - Business Data Analyst with AI Expertise
#     ("Data Visualization and Dashboard Development", "Crafted dynamic dashboards using pivot tables and ggplot2", "ODS"),
#     ("Sales Prediction Modeling", "Developed R-Keras models for sales trend predictions", "ODS"),
#     ("Business Intelligence Integration", "Blended AI strategies with traditional business intelligence", "ODS"),
#     ("Data Infrastructure Establishment", "Established robust data infrastructure for data analysis", "ODS"),
#     ("Strategic Data Analysis", "Analyzed business trends for strategic decision-making", "ODS"),

#     # Fiat Chrysler Automotive | Auburn Hills, MI - Deep Learning Analyst
#     ("Deep Learning for Profit Optimization", "Developed models for forecasting profitable configurations using R-Keras", "FCA"),
#     ("AI Model Construction and Testing", "Tested various AI models for automotive analytics", "FCA"),
#     ("Data-Driven Production Adjustments", "Adjusted car production based on data analysis", "FCA"),
#     ("Neural Network Application", "Applied neural networks for automotive storage optimization", "FCA"),
#     ("Data Validation and Analysis", "Validated and analyzed automotive data using Python packages", "FCA")
# ]

# # Column names
# columns = ['Skill', 'Description', 'CODE']


# # Creating the DataFrame
# df = pd.DataFrame(data, columns=columns)

# # Rearranging the DataFrame to have 'CODE' as the first column
# rearranged_columns = ['CODE', 'Skill', 'Description']
# df = df[rearranged_columns]

# import pyperclip



# # Iterate through each row
# for index, row in df.iterrows():
#     # Ask user to input once per row, just press Enter to continue
#     input(f"\n\n # <E> to start for company CODE : {row['CODE']} \n")
    
#     # Iterate over each column from the second column onwards
#     for col in df.columns[1:]:  # Skipping the first 'CODE' column
#         print(f"COPIED field : {col} @{row['CODE']} \t::: {row[col]}")
        
#         # Copy the value to clipboard
#         pyperclip.copy(str(row[col]))

#         # Ask user to press Enter between each column's value within the same row
#         if col != df.columns[-1]:  # No input after the last column
#             input("\n<E>< next >\n")

# print("Done")



