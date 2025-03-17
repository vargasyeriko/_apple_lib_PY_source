########################################################
########################################################
########################################################
# 

########################################################
########################################################
########################################################

def resume(job_desc):
    ########################################################
    ########################################################
    ########################################################

    import pandas as pd
    import re
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    import nltk
    
    # Ensure you have the necessary NLTK resources
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    ########################################################

    direc_inp = '/Users/yerik/_apple_source/all_data/tables/_0ds/'
    df_exp_descriptions = pd.read_excel(open(f'{direc_inp}DS_jobs.xlsx', 'rb'),
                  sheet_name='Job_Descriptions')
    ########################################################


    def preprocess_text(text):
        """Tokenize, remove stopwords, and lemmatize a given text."""
        tokens = word_tokenize(text.lower())
        stopwords_list = stopwords.words('english')
        lemmatizer = WordNetLemmatizer()
        processed_tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalpha() and word not in stopwords_list]
        return " ".join(processed_tokens)

    def get_keyword_frequencies(job_desc, df_exp_descriptions):
        """Return a sorted list of keywords by their frequency in the job description."""
        processed_desc = preprocess_text(job_desc)
        all_keywords = pd.concat([df_exp_descriptions['A_kw_realm'], df_exp_descriptions['B_kw_subject'], df_exp_descriptions['D_kw_industry']]).unique()
        all_keywords = [preprocess_text(keyword) for keyword in all_keywords if keyword]
        keyword_freq = {keyword: processed_desc.count(keyword) for keyword in all_keywords if keyword in processed_desc}
        return sorted(keyword_freq, key=keyword_freq.get, reverse=True)

    def match_descriptions(job_desc, df_exp_descriptions, top_n=5):
        """Match job descriptions based on keyword frequency and relevance."""
        keywords = get_keyword_frequencies(job_desc, df_exp_descriptions)
        pattern = re.compile('|'.join(map(re.escape, keywords)), flags=re.IGNORECASE)

        # Score each description based on the presence of keywords
        df_exp_descriptions['score'] = df_exp_descriptions['Description'].apply(lambda desc: sum(pattern.findall(preprocess_text(desc)).count(keyword) for keyword in keywords))

        # Sort by score to get top matching descriptions
        top_matches = df_exp_descriptions.sort_values(by='score', ascending=False).head(top_n)

        return top_matches[['CODE', 'Description', 'rate', 'score']]

    # Sample usage, assuming job_desc and df_exp_descriptions are defined
    df_top_desc= match_descriptions(job_desc, df_exp_descriptions, top_n=23)
    print("Top 23 Matched Descriptions:",len(df_top_desc))

    
    
    ########################################################
    # Create a function to select top 5 rows for each 'CODE'
    def select_top_5_rows(df):
        result = pd.DataFrame()

        # Iterate over unique 'CODE' values
        unique_codes = df['CODE'].unique()
        for code in unique_codes:
            # Filter rows for the current 'CODE'
            code_df = df[df['CODE'] == code]

            # Sort the filtered DataFrame by 'score' and then by 'rate' in descending order
            code_df = code_df.sort_values(by=['score', 'rate'], ascending=[False, False])

            # Take the top 5 rows (or all rows if less than 5 are available)
            result = result.append(code_df.head(5))

        return result

    # Get the selected rows
    df_pick_rows = select_top_5_rows(df_top_desc)

    # Print the selected rows
    print('AFTER PICKING 5 MAX rows for each CODE : ',len(df_pick_rows))#.head()
    
    
    ########################################################
    # PICK ANY ROWS WITH CAI and FORD first & general
    # Filter the original DataFrame for 'CODE' values 'FORD' and 'CAI'
    subset_df_cai_ford = df_pick_rows[df_pick_rows['CODE'].isin([ 'CAI','FORD'])]

    # Reset the index of the subset DataFrame
    subset_df_cai_ford = subset_df_cai_ford.reset_index(drop=True)

    # Print the subset DataFrame
    subset_df_cai_ford
    print('MAKING CAI and FORD always be present -> df_ford_CAI_general is filtered ! len :' , len(subset_df_cai_ford))

    
    ########################################################
    # PICK THE LAST EXPERIENCE TO SHOWCASE a third experience that will be cohesive 
    # Filter the original DataFrame for rows other than 'FORD' and 'CAI'
    check_df =df_pick_rows[~df_pick_rows['CODE'].isin([    'CAI','FORD'])].copy()

    summary_df = check_df.groupby('CODE').agg({
        'CODE': 'count',
        'rate': 'max',
        'score': 'sum'
    })

    # Rename the columns for clarity
    summary_df.columns = ['Count', 'Highest Rate', 'Total Score']

    # Print the summary table
    print('CHECK the freq table of the positions to pick from ->  \n\n',summary_df)


    ########################################################
    # PICK THE LAST EXPERIENCE
    # WRITE SCORES in df
    code_scores = check_df.groupby('CODE')['score'].sum()

    code_scores_mapping = check_df['CODE'].map(code_scores)

    # Add a new column 'Total_Score' with the total scores for each code
    check_df['Total_Score'] = code_scores_mapping

    print("\nTotal scores calculated and added as 'Total_Score' column, total  counts : ", len(check_df))
    print("\nATTN ! NEXT WE PICK the * last experience *, maybe here we can pick in the future ENTER to cntd ...")
    
    ########################################################
    # FILTER LAST EXPERIENCE FROM HOW it SCORED -> if tied, it gives you two
    # PICK THE LAST EXPERIENCE
    other_df = check_df.copy()
    
    # Check if the DataFrame is empty
    if other_df.empty:
        result = "The DataFrame is empty"
    else:
        # Find the CODE(s) with the highest 'Total_Score'
        max_total_score = other_df['Total_Score'].max()
        selected_codes = other_df[other_df['Total_Score'] == max_total_score]['CODE'].tolist()
    
        # If there are multiple CODEs, select only one (e.g., the first one)
        if len(selected_codes) > 1:
            selected_code = [selected_codes[0]]  # Choose the first CODE if multiple have the same max 'Total_Score'
        else:
            selected_code = selected_codes
    
        # Create a filtered DataFrame 'filtered_df' with rows having the selected CODE(s)
        filtered_df = other_df[other_df['CODE'].isin(selected_code)]
    
        result = "\nFiltered DataFrame created with the CODE having the highest 'Total_Score.' ... printing its CODE\n"
    
    # Print or return the DataFrame 'filtered_df' and 'result'
    print(result)
    print(filtered_df['CODE'])


    # other_df = check_df.copy()

    # # Check if the DataFrame is empty
    # if other_df.empty:
    #     result = "The DataFrame is empty"
    # else:
    #     # Find the CODE(s) with the highest 'Total_Score'
    #     max_total_score = other_df['Total_Score'].max()
    #     selected_codes = other_df[other_df['Total_Score'] == max_total_score]['CODE'].tolist()

    #     # Create a filtered DataFrame 'filtered_df' with rows having the selected CODE(s)
    #     filtered_df = other_df[other_df['CODE'].isin(selected_codes)]

    #     result = "\nFiltered DataFrame created with the CODE(s) having the highest 'Total_Score.' ... printing its CODE\n"

    # # Print or return the DataFrame 'filtered_df' and 'result'
    # print(result)
    # print(filtered_df['CODE'])
    
    ########################################################
    
    df_ford_cai_gral = subset_df_cai_ford.copy()
    df_last_experience = filtered_df.copy()
    print('\nford_CAI_gral len :',len(df_ford_cai_gral),' THIRD picked EXPERIENCE len :',len(df_last_experience))
    ########################################################
    # CONCATENATE AND GET WANTED STATEMENT
    concatenated_df = pd.concat([df_ford_cai_gral, df_last_experience])
    print('JOB APPLICATION DESCRIPTION gathered in a total of : ',len(concatenated_df))
    ########################################################

    # NEED CV descriptions and a way to merge with the following 
    # once you created the print statement you will match a good description for CAI and FORD and the extra ones for CV
    # filtered_df_exp_descriptions now contains the rows from df_exp_descriptions that match 'Descriptions' in concatenated_df
    new_df = df_exp_descriptions[df_exp_descriptions['Description'].isin(concatenated_df['Description'])]
    print('\nMERGED DF with DS_JOBS and got a final table with DESC gathered for application with the following INFO as COLS ::\n')
    print('\n ##################################-#############################-#########################-######################')
    ########################################################
    cai_df = new_df[new_df['CODE'].str.contains('CAI', na=False)]
    ford_df = new_df[new_df['CODE'].str.contains('FORD', na=False)]
    added_df = new_df[~new_df['CODE'].str.contains('CAI|FORD', na=False)]

    ######################################################## CAI
    cai_desc = '\n* CAI ->  job description matching jd : \n'
    #Iterate through the DataFrame
    for index, row in cai_df.iterrows():
        code = row['CODE']
        description = row['Description']
        rate = row['rate']
        score = row['score']
        
        # Print the formatted information
        cai_desc += f'* {description}'
        
    cai_desc_this = cai_desc

    ######################################################## FORD

    ford_desc = '\n* FORD ->  job description matching jd :\n'
    #Iterate through the DataFrame
    for index, row in ford_df.iterrows():
        code = row['CODE']
        description = row['Description']
        
        # Print the formatted information
        ford_desc += f'* {description}'
        
    ford_desc_this =ford_desc

    ######################################################## ADDED
    
    # have CHAT do a mock interview from all the info (or have it ready ...)
    added_code = added_df['CODE'].unique()
    
    added_desc = f'* {added_code} ->  job description matching jd : \n\n'
    #Iterate through the DataFrame
    for index, row in added_df.iterrows():
        code = row['CODE']
        description = row['Description']
        
        # Print the formatted information
        added_desc += f'''* {description}
    
        '''
    added_desc_this =added_desc

    
    
    ########################################################
    ########################################################
    ########################################################
 
    # Group the DataFrame by 'CODE' column
    grouped = new_df.groupby('CODE')

    cai_desc = ''
    ford_desc = ''
    added_desc = ''

    
    complete_schema_1 = ""
    # Iterate through the groups ->46 tu crees en Magia ?
    for code, group in grouped:
        # Print the 'CODE' value
        print(f"\n*** *** *** < 0_company_CODE : {code} -> EXPERIENCES DESCRIPTION as follows :::")

        # Iterate through the rows in the group
        for index, row in group.iterrows():

            description = row['Description']
            rate = row['rate']
            score = row['score']

            code_here   = row['CODE'] # 0
            position    = row['Position'] # 1
            action_verb = row['Action Verb'] #2
            task        = row['Task'] #3
            results     = row['Results']#4
            method      = row['Method']#5

            fns         = row['functions'] #6
            fns_tools   = row['py_related']#7

            packages    = row['packages'] #8
            interface    = row['interface'] #9
            comp_prog    = row['comp_programs'] #10

            kw_realm    = row['A_kw_realm'] # 11
            kw_realm_2    = row['A_kw_realm_2'] # 11
            kw_subject    = row['B_kw_subject'] # 12
            kw_skill    = row['C_kw_skill'] # 13
            kw_skill_2    = row['C_kw_skill_2'] # 13
            kw_industry    = row['D_kw_industry'] # 14


            schema_1 = f'''
            < 0_at_COMPANY_code   :\t0  : \t\t\t\t *** *** *** {code_here} >
            < 1_position_TITTILE  :\t1  : {position} >
            < 2_task_ACTION_VERB  :\t2  : {action_verb} >
            < 3_task_DESCRIPTION  :\t3  : {task} >
            < 4_task_RESULTS      :\t4  : {results} >
            < 5_task_METHOD       :\t5  : {method} >     

            < 6_task_FUNCTION     :\t6  : {fns} >
            < 7_function_TOOLS    :\t7  : {fns_tools} >

            < 8_tools_PACKAGES    :\t8  : {packages} > 
            < 9_tools_INTERFACES  :\t9  : {interface} >
            < 10_tools_PROGRAMS   :\t10 : {comp_prog} >

            < 11_key-WORD_REALM   :\t11 : {kw_realm} | {kw_realm_2} > 
            < 12_key-WORD_SUBJECT :\t12 : {kw_subject} > 
            < 13_key-WORD_SKILL   :\t13 : {kw_skill} | {kw_skill_2} > 
            < 14_key-WORD_SKILL   :\t14 : {kw_industry} > 
           '''
            
            
            
            
            complete_schema_1 += f'\n{schema_1}'
            #print(f"* {description}")
            #print(f"Rate: {rate}, Score: {score}")

    complete_schema=complete_schema_1
      

    
    #print(added_desc_this)
    print('\n\n***************************---CONSIDER-FOR-RESUME---***************************')
    ########################################################
    return complete_schema,cai_desc_this,ford_desc_this,added_desc_this

#resume(job_desc)