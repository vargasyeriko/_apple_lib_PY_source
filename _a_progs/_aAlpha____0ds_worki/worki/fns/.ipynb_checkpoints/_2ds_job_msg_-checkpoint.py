# %load C:\Users\yerik\OneDrive\_Source\PY\MAIN\jmsg.py
# %load C:\Users\yerik\OneDrive\_Source\PY\MAIN\jmsg.py
#
# %%writefile C:\Users\yerik\OneDrive\_Source\PY\MAIN\jmsg.py
def worki_msg_rec(date):
    #General
    rec_name = input('\n \t\t\t\t  <<< RECRUITER name >>> ...  ')
    pos = input('\n \t\t\t\t  <<< JOB Position CODE ::: ds/ml/dl >>> ...  ')
    company_name= input('\n \t\t\t\t  <<< COMPANY name >>> ...  ')


    #################################### MESSAGES VARIABLES ####################################



    if pos == "ds":
        position = "Data Scientist"
        matched_role = position
    elif pos == "ml":
        position = "Machine Learning Specialist"
        matched_role = position
    elif pos == "dl":
        position = "Deep Learning Specialist"
        matched_role = position
    else:
        position = input('<<< Position name >>> ... ')
        matched_role = 'Lead Data Scientist'

        #print(position)

    #SIGN
    sign = f'''Best,
    Yeriko Vargas
    {matched_role} 
    (646)-771-6111
    ygvargas93@gmail.com | linkedin.com/in/yeriko-vargas/ | twitter.com/VargasYeriko 
    handle: @vargasyeriko
     '''
    #=================================================================edit
    yeriko_asks_rec_info_link = "https://docs.google.com/forms/d/e/1FAIpQLSeGaBJOzwphOI9Rde6yk4XMJKEHVBce4FnDPneWfkWGDN320g/viewform?usp=sf_link"
    link_1 ="https://docs.google.com/forms/d/e/1FAIpQLSf5uqEqNBswXN2ACDb7Y_fCkqiXYjEHdzImGXKU_BKffMfjeA/viewform?usp=sf_link"
    mail_sub_1 = f"Follow-Up {position} at {company_name}"

    #------------------------------#### Recruiter Reaches out it has been some time-----------------------------------------

    a_1 = f'''Hello {rec_name}, I appreciate you reaching out. I clearly see how this opportunity could 
    be a good fit for me. thanks again, and I would love to circle back with you in the near future for a call. 
    I am not going to lie I got pretty busy the last two months. I am sorry again, I wanted to 
    quickly send you my resume and if this position is open, I would love to see if I 
    can have an interview? Otherwise, let's stay in touch. '''

    a_2 =f'Let me know then, if I can still go for this opportunity, and/or if anything else aligns other than that.'




     #------------------------------#### Recruiter Reaches out within days-----------------------------------------


    b_1 = '''Hello {rec_name}, I appreciate you reaching out. I clearly see how this opportunity could 
    be a good fit for me. thanks again, and I would love to circle back with you in the near future and send you my availability 
    for a call. I am not going to lie I am pretty busy nowadays and I also have a few interviews coming up.
    In the meantime I hope that is okay to send you my resume, being that I am interested on this position.
    I would also like to hear if the position has been filled up within these days? Please.'''


     #---------------C---------------####### linked in - CAI - with link:------------------------C-----------------

    c_1 = f'''Hello {rec_name}, I appreciate you reaching out, I have read the job description. At the time, I am loaded with 
    freelance projects, and I would love to have us still in touch. I see you have strings attached to the Data Science 
    world, and I wanted to extend an invitation to stay in the loop with me and with what my freelance consulting company 
    is directed towards. CAI (Custom AI models), started as my own way to classify my freelance projects but as of now 
    websites like Upwork, Freelance, and Fiverr have become a great way for data scientists to find the right opportunities, 
    and CAI has the ideal goal to match and help grow the data scientist community for a better way to find the right people.'''

    c_2 = f'''My idea is to envision a platform where you, as a recruiter, could find the right data scientist for your needs. 
    These freelance websites do an excellent job saving the projects that dedicated people have done and are more reliable 
    I have been in the field for several years and now I can confidently match and help recruiters get the right candidate.
    I appreciate your proposal, and I will be more than happy to have you send opportunities my way. I am open to reading
    them and weight my availability or offering the contact info of a candidate. 
    I am trying to build a relationship with recruiters, and by perpetuity build a bigger platform.'''

    c_3 =  f''' These early stages have been blowing up fast, as more people (recruiters and data scientists) gravitate towards us,
    I will be able to build strong relationships that can bring better deals and more transparency for all parties.
    Let's connect by filling out this short form so I can have a better organization and idea of what are you looking for.
    CAI - info link: {link_1} '''

    #--------------D----------------#### Explaining my status  -----------------------D------------------

    d_1 = f'''Hello {rec_name}, I appreciate you reaching out, and ohh wow this is amazing, I am so interested in the position 
    of {position}, at {company_name}. I am very sorry I missed your call.'''

    d_2 = '''This is an incredible position, and I am sure I have what it takes to succeed on it, I just wanted to let you know 
    beforehand my work status here in the USA. I have a current EDA that is being extended through the end of next year. 
    But good news is that within that same year I will get my Green Card guaranteed, as I got married with a citizen 
    more than a year ago and started the paperwork for my change of status on May 2022.
    I really don't want us to waste our time, but this is necessary info I needed tell you first. I am sure there is a way 
    to move forward with this opportunity.I would love to see if you think things can align properly and I 
    can have an interview? Otherwise, lets stay in touch!'''

    d_3 =f''' p.s. I receive so many calls lately that I had to have a small 
    process to schedule them, do you mind just filling up my scheduling form? : {yeriko_asks_rec_info_link}'''

    #--------------E----------------#### Short and sweet  -----------------------E------------------
    e_1 = f'''Hello {rec_name}, I appreciate you reaching out, and oh wow this is amazing, I do like the 
    framework of this position.'''


    e_2= f'''I clearly see how this opportunity could 
    be a good fit for me, thanks again for sending it. Let's circle back for a call soon. 
    At the time I am pretty busy with freelance projects, and I also have a few interviews coming up.'''

    #--------------E----------------#### Part Time  -----------------------E------------------
    f_1 = f'''Hello {rec_name}, I appreciate you reaching out, and oh wow this is amazing, I do like the 
    framework of this position. thank you for sending it by.'''


    f_2= f'''I clearly see how this opportunity could 
    be a good fit for me, Although as of now I am looking for a part-time position. I have been doing a lot 
    of freelance projects, and as I am exploring and growing I can tell you that I can fill your needs through a part-time 
        position. I have been building apps with AI embedded models for small business owners that I have to monitor, but as my team is growing I would love to be of support for greater challenges!''' 

    f_3 ='''So if there is a possibility to interview for a part-time position, please contact me soon, I really appreciate you  reaching out.'''
    #-------------------------------------------------------------

    #ps
    ps_1 = f'''::: p.s. ::: 

    PLEASE fill up this sheet, this is extremely helpful for me to establish communication with you, schedule our first call, 
    and understand all of your needs. I do have more colleagues to send your way if that's helpful to you too! 
    thanks again, here is the link: {yeriko_asks_rec_info_link}'''

    ps_2 =f''' p.s. I receive so many calls lately that I had to have a small 
    process to schedule them, do you mind just filling up my scheduling form? link: {yeriko_asks_rec_info_link}'''

    #org
    org_1 =f'''Hi ____,

    Thank you so much for reaching out to me, I can see the position ___________ truly aligns 
    to my profile and I am so happy to move forward and have a chat. before going over a more
    detailed conversation I want to explain my status. I have an OPT that is expiring in january
    I know there has been some time since you sent this but I was transitioning jobs and 
    I just wanted to reach back to you, and send you my updated resume just in case.

    I appreciate the availability! I will cricle back and see if we can have a chat, I am 
    open to have a phone call Tuesday, Wednsday or Thursday around 1- 2 pm'''
    #Questions to ask
    #What is the interviewing process?


    #Recruiter Reaches out it has been some time
    a_1= a_1.replace('\n', '');a_2= a_2.replace('\n', '')

    # Recruiter Reaches out within days
    b_1=b_1.replace('\n', '')

    #  linked in - CAI - with link:
    c_1=c_1.replace('\n', '');c_2=c_2.replace('\n', '');c_3=c_3.replace('\n', '')

    # Explaining my status
    d_1=d_1.replace('\n', '');d_2=d_2.replace('\n', '');d_3=d_3.replace('\n', '')

    ## Short and sweet 
    e_1=e_1.replace('\n', '');e_2=e_2.replace('\n', '')

    ## Part Time 
    f_1=f_1.replace('\n', '');f_2=f_2.replace('\n', '');f_3=f_3.replace('\n', '')

    #ps
    ps_1 = ps_1.replace('\n', '');ps_2=ps_2.replace('\n', '')



    msg1 = f'''
    MAIL_SUBJECT::1: {mail_sub_1}

    {a_1}

    {a_2}

    {ps_1}

    {sign}
    '''
    #msg

    msg2 = f'''
    MAIL_SUBJECT::2: {mail_sub_1}

    {b_1}

    {a_2}

    {ps_1}

    {sign}
    '''
    #msg

    msg3 = f'''
    MAIL_SUBJECT::3: {mail_sub_1}

    {c_1}

    {c_2}

    {c_3}

    {ps_1}

    {sign}
    '''

    #msg
    msg4 = f'''
    MAIL_SUBJECT::4: {mail_sub_1}

    {d_1}

    {d_2}

    {d_3}

    {ps_1}

    {sign}
    '''
    #msg
    msg5 = f'''
    MAIL_SUBJECT::5: {mail_sub_1}

    {e_1}

    {e_2}

    {ps_1}

    {sign}
    '''
    #msg 6
    msg6 = f'''
    MAIL_SUBJECT::5: {mail_sub_1}

    {f_1}

    {f_2}

    {f_3}

    {ps_1}

    {sign}
    '''


    print('\n 1)  Recruiter Reaches out it has been MONTHS \n')
    print('\n 2)  Recruiter Reaches out within DAYS \n' )
    print('\n 3)   linked in - CAI - with link: \n' )
    print('\n 4)  Explaining my status \n')
    print('\n 5)  Short and sweet \n')

    print('\n 6)  Part-time \n' )

    msg_number = int(input("\t <<< # of message do you want to print ::: 1/2/3/4/5/6 >>> ... "))

    if msg_number == 1:
        print("\n\n---------------------------------------\n",msg1,"\n---------------------------------------")
    elif msg_number == 2:
        print("\n\n---------------------------------------\n",msg2,"\n---------------------------------------")
    elif msg_number == 3:
        print("\n\n---------------------------------------\n",msg3,"\n---------------------------------------")
    elif msg_number == 4:
        print("\n\n---------------------------------------\n",msg4,"\n---------------------------------------")
    elif msg_number == 5:
        print("\n\n---------------------------------------\n",msg5,"\n---------------------------------------")
    elif msg_number == 6:
        print("\n\n---------------------------------------\n",msg6,"\n---------------------------------------")
    else:
        print("\n\n---------------------------------------\n",msg5,"\n---------------------------------------")

    msg_number = input("\t <<< Continue without saving ::: enter/s (zARCHIVE) >>> ... ")

    if msg_number == "s": 

        lines00 = [f'{msg1}'f'{msg2}',f'{msg3}',f'{msg4}',f'{msg5}']
        with open(f"/Users/yerik/_apple_source/d_OUT/zARCHIVE/_0ds/messages/{date} - {rec_name} -{company_name}_msg.txt", 'w') as f:
            for line in lines00:
                f.write(line)
                f.write('\n')    
    else: 
        print( ' <jmsg>  not saved')

############################################################

