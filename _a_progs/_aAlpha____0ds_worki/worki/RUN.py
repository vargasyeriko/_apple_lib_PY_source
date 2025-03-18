#%%writefile RUN.py 
exec(open(f"/Users/yerik/_apple_source/PY/GLOBAL/_1_paths.py", encoding="utf-8").read())  # GLOBAL

import subprocess
import webbrowser
#...............................................................................VARIABLES ::: dates
from docx import Document
document = Document()



def welcome_job_app():
    options = ["Print > INFO STRATEGY for APPLYING \t  <input>:: <#> or \t1) < about - strategy - links >",
               "Print > MESG recruiters TEMPLATES \t  <input>:: <#> or \t2) < msgs >",
               "Print > [CV/RES_DS_entry_level] \t  <input>:: <#> or \t3) < cv/res >",
               "nan", #gonna be like version b of avobe or maybe other versions inside .... 
               "nan", # ds tutor here maybe
               "EDIT  > EDIT EDIT EDIT STRATEGY \t  <input>:: <#> or \t6) < edit >",
               "Copy  > COPY FIELDS - APPLY fast\t  <input>:: <#> or \t7) < gral & experience>",
              ]
    
    while True:
        print("\n*** JOB APPLICATION APP PACKAGE *** Please choose an option: by <#> or <code>\n*\n*\n*\n*\n*")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")

        user_input = input("*\nEnter your choice by <#> or <code> or <q/quit> ... \n")
            ############# ------------------------------------------ i ---
        if user_input.lower() == '1' or user_input.lower() == 'info':
            #
            # 1 --<<IMPOR_fns>>>
            exec(open(f"fns/_1ds_jobs_info_.py", encoding="utf-8").read()) 
            
            # 4 --<<EXPORTS>>
            #
            ############# ------------------------------------------ ii ---
        elif user_input.lower() == '2' or user_input.lower() == 'msgs':
            #
            # 1 --<<IMPOR_fns>>>
            from fns._2ds_job_msg_ import worki_msg_rec #
            #subprocess.run(["python", "fns/_2ds_job_msg_.py"])
            # 2 --<<TABLES>>
            #
            # 3 --<<RUN>>
            worki_msg_rec(date)
            # 4 --<<EXPORTS>>

            #############
            ############# ------------------------------------------ iii ---
        elif user_input.lower() == '3' or user_input.lower() == 'cv':
            #
            # 1 --<<IMPOR_fns>>>
            from fns._3ds_job_cv_ import ds_cv
            #subprocess.run(["python", "fns/_2ds_job_msg_.py"])
            # 2 --<<TABLES>>
            #
            # 3 --<<RUN>>
            doc_export = ds_cv()


        # elif user_input.lower() == '4' or user_input.lower() == 'res':
        #     #
        #     # 1 --<<IMPOR_fns>>>
        #     #subprocess.run(["python", "fns/_2ds_job_msg_.py"])
        #     # 2 --<<TABLES>>
        #     #
        #     # 3 --<<RUN>>
        #     exec(open(f"fns/_4ds_job_res_.py", encoding="utf-8").read())  # GLOBAL

            

     #   elif user_input.lower() == '5' or user_input.lower() == 'por':
            #
            # 1 --<<IMPOR_fns>>>
            #subprocess.run(["python", "fns/_2ds_job_msg_.py"])
            # 2 --<<TABLES>>
            
            # 3 --<<RUN>>
          
            

        elif user_input.lower() == '6' or user_input.lower() == 'edit':
            #
            # 1 --<<IMPOR_fns>>>
            from fns._6ds_edit_vars_ import edit_file
            #subprocess.run(["python", "fns/_2ds_job_msg_.py"])
            # 2 --<<TABLES>>
            #
            # 3 --<<RUN>>
            file_path = 'fns/_1ds_jobs_info_.py'

            edit_file(file_path) #    file_path = ... /PY/libs/_pyENVS/_Source/src_env0/_0ds_vars.py'
        ####################### COPY FIELDS Programs

        elif user_input.lower() == '7' or user_input.lower() == 'c_gral':
            #
            # 1 --<<IMPOR_fns>>>
            
            exec(open(f"fns/_7ds_COPY_GENERAL.py", encoding="utf-8").read())  







        
        
            # 4 --<<EXPORTS>>
#             direc_exp = '/Users/yerik/_apple_source/d_OUT/_0ds/apply_now/'
#             doc_export.save(f'{direc_exp}Yeriko Vargas - {date} {position} - Cover Letter.docx')#WORD
#             # EDIT then come back and 
#             input('Go modify and come back to (1) convert to pdf and (2) Archive')
            
#             # (1)2PDF
#             convert(f"{path_company_arch}/Yeriko Vargas - {date} {position} - Cover Letter.docx",
#                     f"{path_company_arch}/Yeriko Vargas - {date} {position} - Cover Letter.pdf" ) #pdf
#             # (2)zARCHIVE
#             direc_arch = '/Users/yerik/_apple_source/d_OUT/zARCHIVE/_0ds/apply_now/cvs/'
#             my_cv = docx.Document(f'{direc_exp}Yeriko Vargas - {date} {position} - Cover Letter.docx') # read modified
#             doc_export.save(f'{direc_arch}Yeriko Vargas - {date} {position} - Cover Letter.docx"')#WORD
            #############
            #enter to proceed
            
                  
                  
                  
            #############
            #############
            #############
            #############
            #############
            
            
        elif user_input.lower() == 'q':
            print("Quitting the application.")
            break
        else:
            print("Invalid input, try again.")

# Call the function
welcome_job_app()

