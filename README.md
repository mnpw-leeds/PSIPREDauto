# PSIPREDauto Readme

PSIPREDauto is an unofficial python package to simplify and automate use of the PSIPRED REST API. PSIPRED is a program to predict the secondary
structure of proteins, available as an [interactive web app](http://bioinf.cs.ucl.ac.uk/psipred/), a [REST API](http://bioinfadmin.cs.ucl.ac.uk/UCL-CS_Bioinformatics_Web_Services.html) and [source code on GitHub](https://github.com/psipred/psipred). All versions of PSIPRED were developed and are maintained by the [UCL Department of Computer Science: Bioinformatics Group](http://bioinf.cs.ucl.ac.uk/).
This is an unnoffical package and is not affiliated with the PSIPRED team or UCL.

This package was developed as the documentation for both the PSIPRED REST API and source code is out of date and difficult to use, and only individual jobs can be submitted via the web app. Consequently using PSIPRED for any more than a handful of jobs is currently difficult. The aim of PSIPREDauto is to allow easy submission of large jobs to PSIPRED and to automatically retrieve the results. This is all done with minimal effort for the user via Python. 

PSIPREDauto can be used either as a python package in your IDE, or from the command line via the PSIPREDauto_commandline.py script. PSIPREDauto has only been tested on Windows 10, however only makes use of the Python standard library and the widely compatible `progressbar2` library so should work on any OS.

## Examples

Before use ensure that the file/s you wish to upload are appropriate! All files must be .fasta files containing a single protein sequence. Files containing multiple sequences are currently not supported,
although functionality to automatically split them is planned. Individual files or batch jobs can be submitted. 

### In python

To submit an individual file from python call the `single_submit` function. `single_submit` requires you to specify the full path to the input file, an email address and
an output directory where results will be saved. For example, to submit the file "TestSeq.fasta" in the directory "C:\Sequences" and save the results in "C:\Sequences\Results" you would use the following call:

`single_submit(r"C:\Sequences\TestSeq.fasta", "foo@bar.com", r"C:\Sequences\Results")`

For each submission PSIPRED returns 7 different results files in various formats which will be saved in the folder "C:\Sequences\Results\TestSeq.fasta output". 
There is also an optional parameter 'interval' to alter how often the server is polled for results. For example:

`single_submit(r"C:\Sequences\TestSeq.fasta", "foo@bar.com", r"C:\Sequences\Results", interval=1)`

would poll the server for results after 1 minute rather than the default 4 minutes. Note that the PSIPRED team recommend 2-5 minutes, however for individual files smaller values are generally ok.

To submit a batch of files use the `batch_submit` function. `batch_submit` requires you to specify the path of the folder containing the .fasta files (`batch_submit` will submit all .fasta files 
in the folder), an email address and an output directory where results will be saved. For example to submit all .fasta files in "C:\Sequences" and save the results in "C:\Sequences\Results" you would use the following call:

`batch_submit(r"C:\Sequences", "foo@bar.com", r"C:\Sequences\Results")`

The results will be saved in the folder "C:\Sequences\Results\Output (dd-mm-yy h-m-s)", where (dd-mm-yy h-m-s) is the date and time when the job was submitted in european date format. `batch_submit` also has
the 'interval' parameter which behaves in the same way as in `single_submit`. It is recommended to not alter this in most cases as setting lower values can lead to instability. For small batches of 
short sequences lower values may lead to faster completion, however for longer sequences and larger batches it may cause the program to crash before completion. This is because if too many requests are 
made before jobs are complete the server will start rejecting requests, causing an exception to be thrown. At present this will cause the program to crash.

### From the command line

`single_submit` and `batch_submit` can both be called from the command line through "PSIPREDauto_commandline.py". Parameters are largely the same as in python but you must specify if you are submitting a single or batch job with a keyword argument rather than by calling a different function.

## Logging

PSIPREDauto uses the python `logging` module. Enable `logging` to see more information about what is going on behind the scenes.

## Known issues

Very large batches (~>1000 sequences) are currently prone to failure due to the server eventually rejecting a request even if the time interval is not set to a small value. Possibly due to high load from other users? Working on a feature to catch this exception and prevent the crash here.
