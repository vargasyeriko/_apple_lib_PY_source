
################ FUNCTIONS
##############
exec(open("_0_PreProcess_fns_.py",encoding="utf-8").read())

######################### cai_0 >>> smart RENAME 
df_rename = _rename_1307_kwtagging_GET_singlefile_interactive_v4(path_in)
df = df_rename.copy()

#print('\n\nRenamed:\n', df.head())
######################### cai_1 >>> to AIFF
df = _convert_1307_dfwav_GET_clean_aiff_with_tags(df)

######################### cai_2 >>> CHOP if needed 
input('ABOUT TO CHOP')
# modes :low medium high
#df_chunks = _aiff_1310_splitter_GET_smart_chunks_dfchunks(df, mode="high")
#df_chunks = _aiff_1310_lowvolsplit_GET_chunks_df(df)
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!
df_chunks = _aiff_1310_lowvolsplit_GET_chunks_df(df, rms_db_threshold=-35, max_chunks=20)

df = df_chunks.copy()
#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!


######################### cai_3 >>> CHOP BEAT GRID needed 
#
# get bpm and duration 
df = _bpm_1407_i2_GET_dominantbpm_durmin_smart(df)
# 
# BEAT CHOP 


input('')
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####

exec(open("run.py",encoding="utf-8").read())
#
#
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
# CAI 3 GET beat samples 
df_chunks = _slice_1110_bars_GET_clean_chunks(df)

df = df_chunks.copy()

print(len(df))
input('')
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
########
#######
####
exec(open("run.py",encoding="utf-8").read())

