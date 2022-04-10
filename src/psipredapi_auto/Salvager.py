# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 23:39:38 2022

@author: pnw2

Crashed psipredapi_auto run salvager. Checks to see which files have results, then moves files from the sequence folder
that already have results to a subdirectory called "Complete". You can then re-run 'psipredapi_auto_functions.batch_submit' 
on the sequence folder to continue from where the last run crashed without generating duplicate results. 

MAKE SURE TO BACK UP THE SEQUENCES FOLDER BEFORE RUNNING!
"""
import os

def salvager(sequence_folder, output_folder):
    # Create a list of names of all finished files
    finished_names = []
    for file in os.listdir(output_folder):
        name = os.path.splitext(file)[0]
        name = f"{name}.fasta"
        finished_names.append(name)
    finished_names = list(set(finished_names)) #Duplicate removal, as the above loop creates 7 identical entries
    finished_names.sort() #Alphabetical order
    if os.path.isdir(f"{sequence_folder}\\Complete") == False:
        os.mkdir(f"{sequence_folder}\\Complete")
    for file in os.listdir(sequence_folder):
        if file in finished_names:
            os.replace(f"{sequence_folder}\\{file}", f"{sequence_folder}\\Complete\\{file}") #Moves the sequence file to a subdirectory called "Complete"
    number_finished = len(finished_names)
    print(f"{number_finished} sequence files were found to have results and were moved to {sequence_folder}\\Complete")
    print(f"Re-run 'psipredapi_auto_functions.batch_submit' on {sequence_folder} to continue from where it previously crashed")