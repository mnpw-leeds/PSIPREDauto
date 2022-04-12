# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:03:23 2022

@author: mnpw

Psipred REST API script, automated submission and retrieval of result for 
individual and batch submission of .fasta files

The function submit() is based on the example script provided by the PSIPRED team, 
available at http://www.cs.ucl.ac.uk/fileadmin/bioinf/PSIPRED/send_fasta.py

TODO:
-Make sure all paths are defined using pathlib to make the code OS agnostic. At present it probably won't work on linux! Note that a lot of things here rely on the string of the path, pathlib tends to return a path object that you might need to use str() on to get things to work with minimal extra effort.
-Make a Sequence class to hold all information about a sequence (e.g. name, path, sequence, uuid, state) and modify the functions to work with it.
-Look into using asyncio to allow things to happend while waiting for results. Probably would only be printing things to console in this time however.
-Change how things are printed to console to make it easier to keep track of progress. Possibly look into format strings.
"""
import requests, os, logging, time
from pathlib import Path
import progressbar #The only external package required

log = logging.getLogger("PSIPREDauto")

"""Core functions"""

def submit(fasta_file, email, file_path=""):
    try: 
        url = 'http://bioinf.cs.ucl.ac.uk/psipred/api/submission.json'
        with open(f"{file_path}{fasta_file}", 'rb') as f:
            payload = {'input_data': (fasta_file, f)}
            if len(fasta_file)>64: # File names cannot be >64 chars, cut down to this if required
                fasta_file = fasta_file[:64]
            data = {'job': 'psipred',
                    'submission_name': fasta_file,
                    'email': email, }
            r = requests.post(url, data=data, files=payload)
            output = r.json()
            log.debug(f"{fasta_file} submitted, returned by server: {output}")
            uuid = output["UUID"]
            sub_name = output["submission_name"]
            return(uuid,sub_name)
    except KeyError:
        log.error(f"Error:{KeyError}\nReturned by server: {output}")
        return(False,False)

def check(UUID):
    output = requests.get(f"http://bioinf.cs.ucl.ac.uk/psipred/api/submission/{UUID}?format=json").json()
    state = output["state"]
    log.debug(f"State:{state}")
    if state == "Complete":
        data_paths = []
        for result in output["submissions"][0]["results"]:
            data_paths.append(result["data_path"])
        log.debug(f"Job for {UUID} is finished\nReturned by server: {output}")
        return(data_paths)
    else:#If the job is not finished
        log.debug(f"Job for {UUID} is not finished\nReturned by server: {output}")
        return(False)
    
def get_results(name,paths,output_path=""): #Name is only used for writing new file names
    for path in paths:
        file = requests.get(f"http://bioinf.cs.ucl.ac.uk/psipred/api{path}").text
        drop, ext = os.path.splitext(f"http://bioinf.cs.ucl.ac.uk/psipred/api{path}")
        name, drop = os.path.splitext(name)
        with open(f"{output_path}\\{name}{ext}","w") as f:
            f.write(file)
    log.debug(f"{name} results retrieved")
    
"""Single submission only"""
            
def single_schedule_check(interval,UUID): #How often to poll the server in mins, and a UUID to retrieve data for
    result = False
    while result == False: #check() returns False if the results are not ready
        time.sleep(interval*60)
        result = check(UUID)
        if result == False:
            print("Results not ready. Waiting {interval} minutes to poll again")
    return(result)

def single_submit(fasta_file, email, output, interval=1): #Provide a fasta file and how often to poll the server for results, in minutes
    print(f"Submitting {fasta_file}, please wait")
    uuid, sub_name = submit(fasta_file, email)
    print(f"Submitted successfully\nWaiting {interval} minute/s for results")
    paths = single_schedule_check(interval,uuid)
    output_dir = f"{fasta_file} output"
    if os.path.isdir(f"{output}\\{output_dir}") == False:
        Path(f"{output}\\{output_dir}").mkdir(parents=True, exist_ok=True)
    get_results(fasta_file,paths,output_path=f"{output}\\{output_dir}")
    print(f"Results retrieved, saved to {output}\\{output_dir}")
    
"""Batch submission only"""

def batch_submit(input_path, email, output, interval=4): #Provide input_path to directory of single sequence FASTA files, and a time to wait in minutes before polling the server for results
    max_job_number = 15 #number of concurrent submissions, max of 15 is set by the server
    #Identify .fasta files in the target directory
    fasta_files = []
    for file in os.listdir(input_path):
        if os.path.splitext(file)[1] == ".fasta":
            fasta_files.append(file)  
    fasta_files.sort()  
    number_of_jobs = len(fasta_files)
    to_run = fasta_files #Files that need to be run
    running = {} #Files that are just about to be submitted or have been submitted but the results are not ready
    to_get = {} #Files that are finished and are waiting to have their results downloaded
    completed = 0 #Keep track of the number of jobs that are finished to update the progress bar
    
    #Create a directory with time stamp to store the results
    time_tup = time.localtime()
    useful_time = time.strftime("%d-%m-%Y, %H.%M.%S",time_tup)
    output_dir = f"Output {useful_time}"
    Path(f"{output}\\{output_dir}").mkdir(parents=True, exist_ok=True)
    print(f"\nResults will be saved in: {output}\\{output_dir}")
    #Create a progress bar
    print("\nNote the progress bar only updates after each waiting interval"
          f" ({interval} mins). "
          "If you have recently submitted other sequences you may hit "
          "the maximum number of concurrent submissions (15) and will have "
          "to wait longer before any results are returned and the progress "
          "bar updates.")
    with progressbar.ProgressBar(max_value=number_of_jobs) as bar:
        bar.update(0)
        #Core logic
        while len(to_run) != 0: #As long as there are files that have not been submitted...
            left = len(to_run)
            log.info(f"Number of items left to submit: {left}")
            while len(running)<max_job_number and len(to_run) != 0 : #...ensure that as many as possible are running simultaneously, and stop trying to add more if none are left.
                running[to_run.pop(0)] = {"UUID":None}
            for file in list(running): #Loop to submit the files
                uuid, sub_name = submit(file, email, file_path=f"{input_path}/")
                if uuid != False: #Will be false if submit() failed, most likely due to previous jobs not being finished and the maximum number of concurrent jobs being hit
                    running[file]["UUID"] = uuid
                    running[file]["input_paths"] = None
              
            time.sleep(interval*60) #Wait for the server to calculate the results. PSIPRED team recommend 2-5 minute wait. This script defaults to 2 minutes.
            
            for file in list(running): #Check to see if the results are ready
                if running[file]["UUID"] is not None: #Will be None if the file was not correctly uploaded by submit(). Most often due to hitting the max number of jobs but could be due to an issue with the file itself (e.g. wrong format, empty, etc.)
                    running[file]["input_paths"] = check(running[file]["UUID"])
                    if running[file]["input_paths"] is not False: #Will be False if the results were found to be not ready by check()
                        to_get[file] = running.pop(file) #Move out of "running" and into "to_get", the contents of which will be downloaded
            for file in to_get: #Download the results
                log.debug(f"file = {file}\nto_get[file]['input_paths'] = {to_get[file]['input_paths']}")
                get_results(file,to_get[file]["input_paths"],output_path=f"{output}\\{output_dir}")
            completed += len(to_get) #Update the completed count with the sequences that have just been finished
            bar.update(completed)
            to_get = {} #Empty after the files have been downloaded to prevent repetition
    print(">>>COMPLETE<<<")
