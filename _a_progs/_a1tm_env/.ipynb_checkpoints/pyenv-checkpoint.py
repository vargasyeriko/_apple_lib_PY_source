#import  CONDA_actions

exec(open(f"/Users/yerik/_apple_source/PY/GLOBAL/_9_CONDA_actions.py", encoding="utf-8").read())  # GLOBAL


import subprocess


# New Function: Choose Environment
def choose_environment():
    envs = {
        0: "/Users/yerik/_envs/_0ds_envs/ds_env", 
        1: "/Users/yerik/_envs/_1tm_envs/tm_env",
        2: "/Users/yerik/_envs/_2ms_envs/ms_env",
        3: "/Users/yerik/_envs/_3co_envs/co_env",
        4: "/Users/yerik/_envs/_4yy_envs/yy_env",
        5: "/Users/yerik/_envs/_5bh_envs/bh_env",
        
        6: "/Users/yerik/_envs/_GIT_envs/git_env0",
        7: "/Users/yerik/_envs/SRC_envs/src_env0",
        
        8: "/Users/yerik/_envs/_0ds_envs/rasa_env1",
        9: "/Users/yerik/_envs/_2ms_envs/demcus_env1",
    }


#import  CONDA_actions

# VAIRABLES
#
env_path = '/Users/yerik/_envs/_1tm_envs/tm_env'
my_env_path = env_path
#
my_dir_out       ='/Users/yerik/Desktop'
#
my_lib              = '/Users/yerik/_apple_source/PY/libs/_1tm'

####################
print('\n\n! HELLO YERIKO ::: @ 4yy ')
while True:
    key_pressed = input("\n\t\t\t\t\t\t(1) **CONDA ENV MANAGER = 'enter' <<<E/l>>> (2) **LIB= 'l'  \n").lower()

    if key_pressed == "":
        # Execute the first program
        exec(open(f"/Users/yerik/_apple_source/PY/GLOBAL/_9_CONDA_actions.py", encoding="utf-8").read())
        manage_packages_and_environment(env_path)
    elif key_pressed == "l":
        print("Exiting the program.")
        break
    else:
        print("INVALID")

print('\n*')
exec(open(f"/Users/yerik/_apple_source/PY/GLOBAL/_10_LIB_runner.py", encoding="utf-8").read())

####################

