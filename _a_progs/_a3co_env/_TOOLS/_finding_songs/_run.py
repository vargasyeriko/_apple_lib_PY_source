import song_lists

list_1 = song_lists.list_1
list_2 = song_lists.list_2
list_3 = song_lists.list_3
list_4 = song_lists.list_4
#list_5 = song_lists.list_5

exec(open("song_lists_fns_.py").read())

#!#!#!#!#! RUNNING STATEMENTS #!#!#!#!#!

# Just validate and clean (no overwrite)
validate_and_clean_songlists(overwrite=False)

# Clean and OVERWRITE _TOOLS/song_lists.py
# WARNING: This will overwrite the file!
validate_and_clean_songlists(overwrite=True)

df_search_songs = play_track_search_loop()
