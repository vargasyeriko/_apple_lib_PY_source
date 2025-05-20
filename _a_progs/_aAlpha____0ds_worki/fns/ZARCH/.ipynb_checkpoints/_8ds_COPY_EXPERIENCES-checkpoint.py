
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
