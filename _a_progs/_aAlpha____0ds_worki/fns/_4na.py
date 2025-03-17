print('NO OUTCOME')
# trigger_word = 'Analize'
# matched_role = 'Jr Data Scientist'
# company_name = 'Apple'
# position = 'Data Scientist'
# job_desc= '''HERE IS THE JD


# '''






# # comment all by ctr + / -> 
# #-----I---------------------------------------PACKAGES-------------------------------------------------------------------->
# #......................................................................................DATA MANIPULATION
# import docx;import pandas as pd;from docx2pdf import convert
# import numpy as np;from scipy import io

# #.......................................................................................TIMES
# from time import gmtime, strftime

# #.......................................................................................DATES
# import calendar;from datetime import date;import os;from datetime import date
# print('*** installed data and dates modules \n')


# #................................................................................................NLP
# from nltk.tokenize import sent_tokenize, word_tokenize
# from nltk.stem import WordNetLemmatizer;import nltk;import gensim
# nltk.download('punkt');nltk.download("stopwords");nltk.download('tagsets')
# nltk.download('averaged_perceptron_tagger');nltk.download('wordnet')
# from nltk.corpus import stopwords;from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer;from nltk.tokenize import word_tokenize
# #import ghostscript
# print('*** installed NLP modules \n')

# #.............................................................................................VIZUALIZATION
# import matplotlib.pyplot as plt
# print('*** installed VISUALS modules \n')

# today = date.today()
# date = today.strftime("%d_%m_%Y");year = f"{date[6:10]}"; month_number = f"{date[3:5]}";day = f"{date[0:2]}"
# month = calendar.month_name[int(month_number)]; written_date = f"{month} {day}, {year} "
# print ("❤ today is:", written_date, "or :) ", date)


# #-------------------------------------------------------------------------DATA SETS
# # paths
# #READ excel sheets
# #1
# direc_inp = '/Users/yerik/_apple_source/all_data/tables/_0ds/'
# df_exp_descriptions = pd.read_excel(open(f'{direc_inp}DS_jobs.xlsx', 'rb'),
#               sheet_name='Job_Descriptions')

# #2
# df_experience_info= pd.read_excel(open(f'{direc_inp}DS_jobs.xlsx', 'rb'),
#               sheet_name='Job_General') 
# #3
# df_python = pd.read_excel(open(f'{direc_inp}DS_jobs.xlsx', 'rb'),
#               sheet_name='Python')
# #4
# df_education = pd.read_excel(open(f'{direc_inp}DS_jobs.xlsx', 'rb'),
#              sheet_name='Education_Cert')

# #------------------------------------------------------------------------

# import pandas as pd
# from collections import Counter
# import re

# # Assuming job_desc and df_exp_descriptions are already defined

# # NLP for suggestions and other preprocessing (Placeholder for your NLP code)

# # Tokenize and count word frequency
# wordlist = job_desc.split()
# wordfreq = Counter(wordlist)

# # Convert to DataFrame and remove duplicates
# df_job_words = pd.DataFrame(wordfreq.items(), columns=['words', 'frequency']).drop_duplicates()

# # Ensure correct data types
# df_exp_descriptions['A_kw_realm'] = df_exp_descriptions['A_kw_realm'].astype(str)

# df_exp_descriptions['B_kw_subject'] = df_exp_descriptions['B_kw_subject'].astype(str)
# df_exp_descriptions['D_kw_industry'] = df_exp_descriptions['D_kw_industry'].astype(str)

# # # Combine keywords and use regular expressions for matching
# key_words = '|'.join(df_exp_descriptions['A_kw_realm'].tolist() + df_exp_descriptions['B_kw_subject'].tolist() + df_exp_descriptions['D_kw_industry'].tolist())
# pattern = re.compile(key_words)

# # # Filter and sort by frequency
# df_words_matched = df_job_words[df_job_words.words.str.contains(pattern)].sort_values(by=['frequency'], ascending=False)
# print(df_words_matched)

# # # Display settings for DataFrame
# pd.options.display.max_colwidth = 800

# # # Finding job descriptions with matched keywords
# kw_job_desc = '|'.join(df_words_matched['words'].tolist())
# df_exp_descriptions = df_exp_descriptions[df_exp_descriptions.Description.str.contains(kw_job_desc, flags=re.IGNORECASE)]
# df_matched = df_exp_descriptions[['CODE', 'Description']].sort_values(by=['CODE'], ascending=False).reset_index(drop=True)

# # # Print matched information
# print(f"Matched Words: {kw_job_desc}")
# print("Descriptions Matching in df_matched:")
# print(df_matched)
# ##-------------------------------------------------------------------------------------------------------------------------------
# ##--------------------------------------------------VARIABLES-------------------------------------->
# ##--------------------------------------------------------------------------------------------------------------------------------
# ##-------------------------------------------------(a)-STATIONARY-VARIABLES----------------------------------------------------------



# #------------------------------------------------(c)-EDITABLE VARIABLES----------------------------------------------------------------

# #trigger skills 
# trigger_expertise_1="optimization"
# trigger_expertise_2="forecast"
# trigger_expertise_3="analysis"
#     #---> opportunities where I can use my {trigger_expertise_1}, {trigger_expertise_2}, and {trigger_expertise_3} expertises

    
# #EDIT SCRIPT SAY ONE OF MY MOST similiar projects then this and its description
# matched_company = "FCA"
# matched_project = ' '
# main_task_verb = "optimize"
# memberships = "ASA"
# desired_salary = 'My desired salary for this position is Negotiable'
# Salaries = '''Machine Learning Specialist: $150,000 per year or $76.92 per hour '''
# drivers_lis = 'V 622 951 018 846'
# Linked_In_Search ='''Machine Learning Specialist, Past 24hr, Associate & Mid-Senior level,Remote,under 10 applicant, <120,000 '''
# skillset = '''Machine Learning Methods
# Artificial Neural Network
# Computer Vision
# Feature Extraction
# Natural Language Processing
# Supervised Learning
# Deep Learning
# Machine Learning Tools
# Keras
# Amazon SageMaker
# SAS
# MATLAB
# TensorFlow
# PyTorch
# pandas
# Machine Learning Deliverables
# Model Optimization
# Machine Learning Model
# Machine Learning
# Data Science
# Data Science Consultation
# Machine Learning Techniques
# Anomaly Detection
# Classification
# Logistic Regression
# Linear Regression
# Principal Component Analysis
# Decision Tree
# Machine Learning Languages
# R
# Python
# Other skills
# Statistical ProgrammingData ProcessingData Analytics & Visualization Software '''

# #-----------------------------------------------------------------------------------------
# #Create Folder
# direc_arch = '/Users/yerik/_apple_source/d_OUT/zARCHIVE/_0ds/apply_now/'
# path_company_arch = f'{direc_arch}/{company_name}/{position}' #Create folder in Archive for Job
# if not os.path.exists(path_company_arch):
#     os.makedirs(path_company_arch)

# #-----------------------------------------------------------------------------------------------------------------
# #-------------------------------------------------Cover-Letter----------------------------------------------------------------
# #-----------------------------------------------------------------------------------------------------------------
# #-----------------------------------------------------------------------------------------------------#### 1
# #### 1 Give a killer headline: When in doubt, use: Trgger word + Adjective(size, texture, shape , feel) +keyword +Promise
# killer_Headline = f"""I was excited to find this job opportunity is still open! {trigger_word} has been on the surface 
# of my work as a {matched_role} more than ever before."""
# #-----\
# #-----/
# #f"I’ve been passionate about 
# #f"I was excited to learn of this job opportunity "
# #INSTRUCTOR# f“As a teacher, I believe every student deserves the opportunity to learn"  #INSTRUCTOR
# #-----\
# #-----/
# #-----------------------------------------------------------------------------------------------------#### 2
# #### 2 Personalized_Greetings: Research the name of HR manager or use Dear Sir/Madam
# Personalized_Greetings= f'''Dear Sir, I thank you for your time in reading this letter. I would love to introduce myself, 
# and related work experience that show my dedication and my hard work as {matched_role}. 

# '''
# #-----\
# #-----/
# #UPWORK#
# #JOB# f'''Dear Sir, I thank you for your time in reading this letter and I would love to let you know how I can help {company_name} {main_task_verb}'''
# #JOB# f'''Dear Sir {hirm_name} It is with great enthusiasm that I write to you in response to the job posting Data Scientist. I learned of this position through Linked In '''
# #-----\
# #-----/
# #-----------------------------------------------------------------------------------------------------#### 3
# #### 3 Introduce Yourself:Open Strong and compliment the company
# P1_Introduce_yourself = f'''My name is Yeriko Vargas, I became a Statistician in May 2019 and since then 
# I have been involved in numerous projects involving {trigger_word}. I have decided to keep finding opportunities 
# where I can use my {trigger_expertise_1}, {trigger_expertise_2}, and {trigger_expertise_3} expertise. As I am 
# aware of your needs, I had to reach out and offer my services. I have 8+ years of involvement with statistics work and 5+ artificial neural network methodologies. '''
# #-----\
# #-----/

# #-----\
# #-----/
# #-----------------------------------------------------------------------------------------------------#### 4
# #### 4 Why you are a great fit for the company:Write a short Summaryof your career and skills, and tailor it to fit to company
# P2_Why_you_great_fit= f'''The opportunity of {position} at {company_name}, would be best if taken into my hands. 
# As {matched_role} I have had the opportunity to work with big data 
# by handling millions of rows, starting with EDA analysis till the deployment stage of Machine Learning and Deep 
# Learning models. 
# Aside from my 5+ years' experience in python and R programming skills, I have a powerful base of ML techniques and its 
# algorithms. These strong bases of math and statistics were transferred in my B.S. and M.S. in Applied Statistics from 
# teachers and advisors at Oakland University; in particular Dr. Ravindra Khattree. After much work in math and statistics, 
# I gave the most important switch in my career by deciding to do Deep Learning research. This decision took me to understand 
# the deep layers in neural networks, and how the logic of the perceptron theorem work. The main area of research was 
# {trigger_expertise_1}, and specifically what activation functions are best fitting the neural network models when 
# {trigger_expertise_1}, and {trigger_expertise_2} are needed. After creating so much momentum with this opportunity 
# I was taken into a path for similar projects working full time as {matched_role} for Ford, FCA, and 
# as a AI/ML Researcher for an AI consulting company; Soothsayer Analytics. 
# '''
# #-----\
# #-----/
# #f'''similarities within the duties and responsabilities for the {position} job description at {company_name} {position} needsat 
# #-----\
# #-----/
# #### 5 Why the COMPANY is  agreat fit for you:What excites you about working there? what do you want to learn there?
# P3_Why_company_great_fit = f'''I was so lucky to find the {position} position, I would really be a great {matched_role} 
# at {company_name}. I know that {trigger_word} projects are a great fit for me. Please consider taking the next step. 
# I want to make sure to tell you that I am huge in organization, very self-driven and really creative; when it comes 
# to data, I believe every data set can be considered as a story to tell. I have the ability to tackle enormous 
# {trigger_word} problems. I have experienced {trigger_word} work in detailed and I have gained so much understanding 
# around this topic, and I can assure you I have what it takes to help as {matched_role}. '''

# #### 6 Finish strong and stay in touch:Repeat why you are a great fit, explain how and when you are going to contact them
# Closing_stay_in_touch = f'''Thank you I believe that there is so much I could passionately talk 
# about other related experiences to the work needed here. I think that the 
# purpose of the {position} at {company_name} closely matches my career goals as well. I really would 
# be so happy and excited to have the chance to speak with someone and learn more about this position, as 
# I want to find a deal to work here at {company_name} as for the {position} position'''

# #### 7 All Best...
# All_the_best_name = f'''All best,
# Yeriko Vargas'''

# killer_Headline=killer_Headline.replace('\n', '')
# Personalized_Greetings = Personalized_Greetings.replace('\n', '')
# P1_Introduce_yourself = P1_Introduce_yourself.replace('\n', '')
# P2_Why_you_great_fit = P2_Why_you_great_fit.replace('\n', '')
# P3_Why_company_great_fit =P3_Why_company_great_fit.replace('\n', '')
# Closing_stay_in_touch = Closing_stay_in_touch.replace('\n', '')

# #-----------------------------------------------------------------------------------------------------------------

# # #Write txt document

# # text = f'''
# #  : 
# # Work SUMMARY :-------------------------------------------------------------------------------- SUMMARY for CHAT GPT ->

# # ## Job Search Summary

# # I'm on the hunt for **remote, part-time roles** where I can immerse myself in **audio and signal processing**. 

# # - **Position Level**: Senior or mid-level data scientist roles.
# # - **Company Type**: Small, innovative companies in the niche audio industry.
# # - **Compensation**: Aiming for an hourly rate of **$70-$88**.
# # - **Work Preference**: Focused on research and development within audio tech.
# # - **Professional Environment**: Companies that value remote work and are at the cutting edge of innovation.

# # ## What I Do

# # As a freelancer specializing in audio projects, I combine **data science with music** to enhance music production and curation. My work spans:

# # - Optimizing music libraries for DJs.
# # - Employing machine learning for sound enhancements.
# # - Creating smarter, more efficient music production and curation methods.

# # ## Ideal Company

# # I'm drawn to companies that prioritize:

# # - **Innovation and Remote Work**: Places where innovation drives the culture, and remote work is embraced.
# # - **Technology and Impact**: Opportunities to work with Python, R, SAS, and music software, focusing more on coding and creating than on meetings.

# # ## My Professional Interests

# # I am passionate about:

# # - **Data Analytics in Audio**: Using analytics to revolutionize the audio industry, from sound manipulation algorithms to immersive audio experiences.
# # - **AI-Driven Content Creation**: Leading the charge in audio engineering with a focus on AI and machine learning.

# # ## Bringing to the Table

# # - **Networking and Community Engagement**: Actively engaging with music and tech communities.
# # - **Continuous Learning**: Keeping up with audio data science trends to stay ahead.
# # - **Unique Blend of Music and Tech**: Offering a distinct perspective on enhancing music experiences through data.


# # Work experience:-------------------->(>3.5 years)--------------------YEARS OF EXPERIENCE ->

# # I graduated from my masters in stats May 19' since then I've worked non-stop in a variaty of DS projects.
# # By now I have over 3 and a half years of professional experience in the field of ML DL acting as a data scientist.

# #         BST:  3 months (intenship)
# #         FCA:  8 months (contract)
# #         ODS:  1yr 3 months (full-time)
# #         SA:   10 months(full-time)
# #         FORD: 6 months (contract)
        
# # Python R:--------------> 8 years
# # Stats and Math:--------> 10 years 
# # SQL and Hadoop :-------> 3 years
# # Tableau:---------------> 3 years


# # COVER LETTER ----------------------------------------------------------------COVER LETTER ->

# # Yeriko Vargas 
# # {matched_role} 
# # ygvargas93@gmail.com | in/yeriko-vargas/ | twitter.com/vargasyeriko | (646)-771-6111

# # {written_date}

# # {company_name}
# # re: {position}

# # {killer_Headline}

# # {Personalized_Greetings} {P1_Introduce_yourself}

# # {P2_Why_you_great_fit}

# # {P3_Why_company_great_fit}

# # {Closing_stay_in_touch}

# # {All_the_best_name}


# # &&&&&&&&&
# # &&&&&&&&
# # &&&&&&
# # &&&&&
# # &&&&
# # &&&
# # &&
# # &
# # -----I---------------------------------JOB DESCRIPTIONS--------------------------------------->
# # &
# # &&
# # &&&
# # &&&&
# # &&&&&
# # &&&&&&
# # &&&&&&&&
# # &&&&&&&&&    

# # *0* GENERAL:::-----------------------------------------------------------------------GENEREAL->
        
# #         {df_matched['Description'][df_matched.CODE == 'General'].to_string(index=False)}
        
        
# # *1* CAI:::--------------------------------------------------------------------------------CAI->

# #         {df_experience_info.iloc[6,1]} - {df_experience_info.iloc[6,2]} ({df_experience_info.iloc[6,8]}) - {df_experience_info.iloc[6,9]} - {df_experience_info.iloc[6,10]}
# #         {df_experience_info.iloc[6,3]} {df_experience_info.iloc[6,4]} {df_experience_info.iloc[6,5]}, {df_experience_info.iloc[6,6]},  {df_experience_info.iloc[6,7]} ||| supervisor_1: {df_experience_info.iloc[6,11]} {df_experience_info.iloc[6,12]} {df_experience_info.iloc[6,13]}  ||| supervisor_2: {df_experience_info.iloc[6,14]}  {df_experience_info.iloc[6,15]} {df_experience_info.iloc[6,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'CAI'].to_string(index=False)}
# #         B###

# # *2* FORD:::--------------------------------------------------------------------------------FORD->

# #         {df_experience_info.iloc[5,1]} - {df_experience_info.iloc[5,2]} ({df_experience_info.iloc[5,8]}) - {df_experience_info.iloc[5,9]} - {df_experience_info.iloc[5,10]}
# #         {df_experience_info.iloc[5,3]} {df_experience_info.iloc[5,4]} {df_experience_info.iloc[5,5]}, {df_experience_info.iloc[5,6]},  {df_experience_info.iloc[5,7]} ||| supervisor_1: {df_experience_info.iloc[5,11]} {df_experience_info.iloc[5,12]} {df_experience_info.iloc[5,13]}  ||| supervisor_2: {df_experience_info.iloc[5,14]}  {df_experience_info.iloc[5,15]} {df_experience_info.iloc[5,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'FORD'].to_string(index=False)}
# #         B###
        
# # *3* SA:::--------------------------------------------------------------------------------SA->

# #         {df_experience_info.iloc[4,1]} - {df_experience_info.iloc[4,2]} ({df_experience_info.iloc[4,8]}) - {df_experience_info.iloc[4,9]} - {df_experience_info.iloc[4,10]}
# #         {df_experience_info.iloc[4,3]} {df_experience_info.iloc[4,4]} {df_experience_info.iloc[4,5]}, {df_experience_info.iloc[4,6]},  {df_experience_info.iloc[4,7]} ||| supervisor_1: {df_experience_info.iloc[4,11]} {df_experience_info.iloc[4,12]} {df_experience_info.iloc[4,13]}  ||| supervisor_2: {df_experience_info.iloc[4,14]}  {df_experience_info.iloc[4,15]} {df_experience_info.iloc[4,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'SA'].to_string(index=False)}
# #         B###
        
# # *4* ODS::: --------------------------------------------------------------------------------ODS->

# #         {df_experience_info.iloc[3,1]} - {df_experience_info.iloc[3,2]} ({df_experience_info.iloc[3,8]}) - {df_experience_info.iloc[3,9]} - {df_experience_info.iloc[3,10]}
# #         {df_experience_info.iloc[3,3]} {df_experience_info.iloc[3,4]} {df_experience_info.iloc[3,5]}, {df_experience_info.iloc[3,6]},  {df_experience_info.iloc[3,7]} ||| supervisor_1: {df_experience_info.iloc[3,11]} {df_experience_info.iloc[3,12]} {df_experience_info.iloc[3,13]}  ||| supervisor_2: {df_experience_info.iloc[3,14]}  {df_experience_info.iloc[3,15]} {df_experience_info.iloc[3,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'ODS'].to_string(index=False)}
# #         B###

# # *5* FCA:::--------------------------------------------------------------------------------FCA->

# #         {df_experience_info.iloc[2,1]} - {df_experience_info.iloc[2,2]} ({df_experience_info.iloc[2,8]}) - {df_experience_info.iloc[2,9]} - {df_experience_info.iloc[2,10]}
# #         {df_experience_info.iloc[2,3]} {df_experience_info.iloc[2,4]} {df_experience_info.iloc[2,5]}, {df_experience_info.iloc[2,6]},  {df_experience_info.iloc[2,7]} ||| supervisor_1: {df_experience_info.iloc[2,11]} {df_experience_info.iloc[2,12]} {df_experience_info.iloc[2,13]}  ||| supervisor_2: {df_experience_info.iloc[2,14]}  {df_experience_info.iloc[2,15]} {df_experience_info.iloc[2,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'FCA'].to_string(index=False)}
# #         B###
        
# # *6* BST::: --------------------------------------------------------------------------------BST->

# #         {df_experience_info.iloc[1,1]} - {df_experience_info.iloc[1,2]} ({df_experience_info.iloc[1,8]}) - {df_experience_info.iloc[1,9]} - {df_experience_info.iloc[1,10]}
# #         {df_experience_info.iloc[1,3]} {df_experience_info.iloc[1,4]} {df_experience_info.iloc[1,5]}, {df_experience_info.iloc[1,6]},  {df_experience_info.iloc[1,7]} ||| supervisor_1: {df_experience_info.iloc[1,11]} {df_experience_info.iloc[1,12]} {df_experience_info.iloc[1,13]}  ||| supervisor_2: {df_experience_info.iloc[1,14]}  {df_experience_info.iloc[1,15]} {df_experience_info.iloc[1,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'BST'].to_string(index=False)}
# #         B###
        
# # *7* OUMATH::: --------------------------------------------------------------------------------OUMATH->

# #         {df_experience_info.iloc[0,1]} - {df_experience_info.iloc[0,2]} ({df_experience_info.iloc[0,8]}) - {df_experience_info.iloc[6,9]} - {df_experience_info.iloc[0,10]}
# #         {df_experience_info.iloc[0,3]} {df_experience_info.iloc[0,4]} {df_experience_info.iloc[0,5]}, {df_experience_info.iloc[6,6]},  {df_experience_info.iloc[0,7]} ||| supervisor_1: {df_experience_info.iloc[0,11]} {df_experience_info.iloc[0,12]} {df_experience_info.iloc[0,13]}  ||| supervisor_2: {df_experience_info.iloc[0,14]}  {df_experience_info.iloc[0,15]} {df_experience_info.iloc[0,16]}

# #         A###
# #         {df_matched['Description'][df_matched.CODE == 'OUMATH'].to_string(index=False)}
# #         B###

# # &&&&&&&&&
# # &&&&&&&&
# # &&&&&&
# # &&&&&
# # &&&&
# # &&&
# # &&
# # &
# # ----II---------------------------------------EDUCATION-lINKS-------------------------------------->
# # &
# # &&
# # &&&
# # &&&&
# # &&&&&
# # &&&&&&
# # &&&&&&&&
# # &&&&&&&&&

# # *1* EDUCATION:::------------------------------------------------------------------------------EDUCATION->

# # Master of Science in Applied Statistics   - Oakland University, Auburn Hills, MI      May   2020   GPA: 
# # *-----*
# # Activities and societies: Teacher Assistant for Algebra and Precalculus classes, MEDlife member: Volunteering in Service Learning public health eventsActivities and societies: Teacher Assistant for Algebra and Precalculus classes, MEDlife member: Volunteering in Service Learning public health events
# # The MS program's primary goal is to provide the basis for the skilled and competent application of modern statistical methods. Areas of methodology in the program, include design of experiments, regression analysis, discrete data, statistical computing, statistical process control, non-parametric, multivariate, reliability, sample survey and time series methodology
# # Volunteer: Medlife

# # Bachelor of Science in Applied Statistics    -  Oakland University, Auburn Hills, MI      April 2017   GPA:
# # *------*
# # Activities and societies: Leadership OU, (HALO) Hispanic American Leadership Association , Spanish Club, International Oasis, International Scholars, International Allies, (PUB) Project Upward BoundActivities and societies: Leadership OU, (HALO) Hispanic American Leadership Association , Spanish Club, International Oasis, International Scholars, International Allies, (PUB) Project Upward Bound
# # The Bachelor of Science degree stresses both the theoretical and the applied sides of the subject and is one of the few undergraduate statistics programs in the country. In addition to extensive course work in statistics, the student is exposed to computer science, ethics, and advanced writing skills


# # *2* LINKS:::---------------------------------------------------------------------------------------LINKS->

# # linked in::: https://www.linkedin.com/in/yeriko-vargas/
# # twitter:::  https://twitter.com/VargasYeriko
# # github::: https://github.com/vargasyeriko
# # portfolio url::: http://customaimodels.com/
# # website::: http://customaimodels.com/

# # *3* ADITIONAL INFO:::-----------------------------------------------------------------------ADITIONAL INFO->

# # anything else you want to share:

# # &&&&&&&&&
# # &&&&&&&&
# # &&&&&&
# # &&&&&
# # &&&&
# # &&&
# # &&
# # &
# # ------III---------------------------{company_name}-JOB-DESCRIPTION------------------------------------->
# # &
# # &&
# # &&&
# # &&&&
# # &&&&&
# # &&&&&&
# # &&&&&&&&
# # &&&&&&&&&
# # ---------------------------------------------------------------------------------------------------------{company_name}
# # ---------------------------------------------------------------------------------------------------------JD
# # {job_desc}
# # ---------------------------------------------------------------------------------------------------------{company_name}
# # ---------------------------------------------------------------------------------------------------------JD



# # &&&&&&&&&
# # &&&&&&&&
# # &&&&&&
# # &&&&&
# # &&&&
# # &&&
# # &&
# # &
# # ---------------------------------> PYTHON 
# # &
# # &&
# # &&&
# # &&&&
# # &&&&&
# # &&&&&&
# # &&&&&&&&
# # &&&&&&&&&
# # {df_python}




# # &&&&&&&&
# # &&&&&&
# # &&&&&
# # &&&&
# # &&&
# # &&
# # &
# # ---------------------------------> INTERVIEW-EMAIL-FOLLOW-UP 
# # &
# # &&
# # &&&
# # &&&&
# # &&&&&
# # &&&&&&
# # &&&&&&&&
# # &&&&&&&&&

# # FOLLOW UP LINK: 

# # REMIDERS: 
# # * Go to their social and follow them 

# # AFTER HERE ADD /interview stuff/ checkbox add them in social medias that I gave!

# # #ADD SUMMARIES AND ALL FOR DIFFERENT EXPERIENCES - Cover letter on the fly 
# # Picture of myself profesionally
# # '''
# # print(text)



# # # #--------------------------------------------------------------- (1) after modifying avobe -> 5-10 min
# # # #Write txt file to Desktop Apply NOW
# # # textfile = open(f'C:/Users/yerik/OneDrive/Desktop/COM_APPLY.txt', 'w' )
# # # textfile.write( text + "\n")
# # # textfile.close()

# # # #Save it to apply now - save to erase anytime
# # # textfile = open(f'C:/Users/yerik/OneDrive/_Source/Jobs/Apply_Now/apply to {company_name}-{position}{date}.txt', 'w')
# # # textfile.write( text + "\n")
# # # textfile.close()

# # # #Save it to archive company folder 
# # # textfile = open(f'{path_company_arch}/apply to {company_name}-{position}{date}.txt', 'w')
# # # textfile.write( text + "\n")
# # # textfile.close()



# # # #---------------------------------------------------------------  (2) after modifying RESUME -> 15-30 min
# # # #ARCHIVE

# # # #Import word resume doc
# # # my_resume = docx.Document(f"{path_source}/Jobs/Resume_Yeriko_Vargas.docx")

# # # #Export resume with the changed position
# # # doc = my_resume.save(f"{path_company_arch}/Yeriko Vargas -{date}{position} - Resume.docx")

# # # #Change it to in a pdf file
# # # convert(f"{path_company_arch}/Yeriko Vargas -{date}{position} - Resume.docx",f"{path_company_arch}/Yeriko Vargas - {date}{position} - Resume.pdf" )

# # # #RESUME to "Apply Now"

# # # #take modified Resume and bring it to APPLY NOW
# # # doc = my_resume.save(f"{path_apply_now}/Yeriko Vargas - {position} - Resume.docx")

# # # #Change Resume to in a pdf file
# # # convert(f"{path_apply_now}/Yeriko Vargas - {position} - Resume.docx", f"{path_apply_now}/Yeriko Vargas - {position} - Resume.pdf" )


# # # #---------------------------------------------------------------  (3) after modifying COVER LETTER -> 30-45 min
# # # #ARCHIVE

# # # #Import word cv doc
# # # my_cv = docx.Document(f"{path_source}/Jobs/Cover_Letter_Yeriko_Vargas.docx")

# # # #Export cv with the changed position
# # # doc = my_cv.save(f"{path_company_arch}/Yeriko Vargas - {date} {position} - Cover Letter.docx")

# # # #Change it to in a pdf file in same folder
# # # convert(f"{path_company_arch}/Yeriko Vargas - {date} {position} - Cover Letter.docx",f"{path_company_arch}/Yeriko Vargas - {date} {position} - Cover Letter.pdf" )

# # # #CoverLetter to "Apply Now"

# # # #take modified CV and bring it to APPLY NOW
# # # doc = my_cv.save(f"{path_apply_now}/Yeriko Vargas - {position} - Cover Letter.docx")

# # # #Change it to in a pdf file
# # # convert(f"{path_apply_now}/Yeriko Vargas - {position} - Cover Letter.docx", f"{path_apply_now}/Yeriko Vargas - {position} - Cover Letter.pdf" )

# # # #-----------------------Print
# # # print(text)
# # # print(job_desc)
