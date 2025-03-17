#########################################################
##
# Folder fn is inside functions/pyENVS/_Source/srs_env0, find RUN.py in father folder.
import os
import subprocess
# & FOLDER_RUNPY_SRC to be  **delegated**
#
# & >>>>>>>>>>>>>>  =  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#
FOLDER_RUNPY_SRC = 'worki'
#
# & >>>>>>>>>>>>>>  =  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#
# XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x
#
valid= 'functions/_pyENVS/_Source/src_env0'  

direc = f'/Users/yerik/_apple_source/PY/{valid}/{FOLDER_RUNPY_SRC}'
subprocess.run(['python',f"{direc}/run.py"], cwd=f'{direc}')
#
#XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x XX x
#
# END
##
#