# PSIPREDauto Readme

PSIPREDauto simplifies and automates the prediction of protein secondary structure from sequence files using the PSIPRED REST API. PSIPRED is a program to predict protein secondary structure and is available as an [interactive web app](http://bioinf.cs.ucl.ac.uk/psipred/), a [REST API](http://bioinfadmin.cs.ucl.ac.uk/UCL-CS_Bioinformatics_Web_Services.html) and [source code on GitHub](https://github.com/psipred/psipred). All versions of PSIPRED were developed and are maintained by the [UCL Department of Computer Science: Bioinformatics Group](http://bioinf.cs.ucl.ac.uk/).
This is an unnoffical package and is not affiliated with the PSIPRED team or UCL. If you use PSIPREDauto in any published work, please cite PSIPRED [(see guidance from the PSIPRED team on how they like to be cited)](http://bioinfadmin.cs.ucl.ac.uk/UCL-CS_Bioinformatics_PSIPRED_citation.html) and not this package, the PSIPRED team deserve the credit! Any acknowledgement of PSIPREDauto would of course be greatly appreciated, but this package would be impossible without the hard work of the PSIPRED team.

This package was developed as the documentation for both the PSIPRED REST API and source code is out of date and difficult to use, and only individual jobs can be submitted via the web app. Consequently using PSIPRED for any more than a handful of jobs is currently difficult. The aim of PSIPREDauto is to allow easy submission of large jobs to PSIPRED and to automatically retrieve the results. This is all done with minimal effort for the user via Python. 

After installation PSIPREDauto can be used either as a python package in your IDE, or from the command line via the commandline.py script. PSIPREDauto has only been tested on Windows 10, however only makes use of the Python standard library and the widely compatible `progressbar2` library so should work on any OS.

## Installation

PSIPREDauto is available from PyPI using pip: 

`pip install PSIPREDauto`

Alternatively, the source code is [available on github](https://github.com/mnpw-leeds/PSIPREDauto) to do with what you will.

## Examples

Before use ensure that the file/s you wish to upload are appropriate! All files must be .fasta files containing a single protein sequence. Files containing multiple sequences are currently not supported,
although functionality to automatically split them is planned. Individual files or batch jobs can be submitted. 

### In python

To submit an individual file from python call the `single_submit` function. `single_submit` requires you to specify the full path to the input file, an email address and
an output directory where results will be saved. For example, to submit the file "TestSeq.fasta" in the directory "C:\Sequences" with the email address foo@bar.com, and save the results in "C:\Sequences\Results" you would use the following call:
```
from PSIPREDauto.functions import single_submit

single_submit(r"C:\Sequences\TestSeq.fasta", "foo@bar.com", r"C:\Sequences\Results")
```
Note that the file paths are passed as strings! Currently no other types of submission are supported.

For each submission PSIPRED returns 7 different results files in various formats which will be saved in the folder "C:\Sequences\Results\TestSeq.fasta output". Note the PSIPRED server will also send a copy of the results to the specified email address.
There is also an optional parameter 'interval' to alter how often the server is polled for results. For example:

`single_submit(r"C:\Sequences\TestSeq.fasta", "foo@bar.com", r"C:\Sequences\Results", interval=1)`

would poll the server for results after 1 minute rather than the default 4 minutes. Note that the PSIPRED team recommend 2-5 minutes, however for individual files smaller values are generally ok.

To submit a batch of files use the `batch_submit` function. `batch_submit` requires you to specify the path of the folder containing the .fasta files (`batch_submit` will submit all .fasta files 
in the folder), an email address and an output directory where results will be saved. For example to submit all .fasta files in "C:\Sequences" and save the results in "C:\Sequences\Results" you would use the following call:
```
from PSIPREDauto.functions import batch_submit

batch_submit(r"C:\Sequences", "foo@bar.com", r"C:\Sequences\Results")
```
The results will be saved in the folder "C:\Sequences\Results\Output <timestamp>", where the timestamp is in dd-mm-yy h-m-s format. Remember that you will also receive a seperate email copy of the results for each file submitted, if you are submitting a large batch it is advisable to set up an email filter to prevent your inbox being flooded by PSIPRED (emails will be from "psipred@cs.ucl.ac.uk", without quotes) . `batch_submit` also has
the 'interval' parameter which behaves in the same way as in `single_submit`. It is recommended to not alter this in most cases as setting lower values can lead to instability. For small batches of 
short sequences lower values may lead to faster completion, however for longer sequences and larger batches it may cause the program to crash before completion. This is because if too many requests are 
made before jobs are complete the server will start rejecting requests, causing an exception to be thrown. At present this will cause a crash.

### From the command line

Single and batch submissions can be made from the command line through "commandline.py". Parameters are largely the same as in python but you must specify if you are submitting a single or batch job with the `--single` or `--batch` keywords rather than by calling a different function. Use the following example to display the command line help information.

`python -m PSIPREDauto.commandline --help`

To submit "TestSeq.fasta" in the directory "C:\Sequences" and save the results in "C:\Sequences\Results" you would use the following:

`python -m PSIPREDauto.commandline --single --input "C:\Sequences\TestSeq.fasta" --email "foo@bar.com" --output "C:\Sequences\Results"`

Submitting a batch job is similar, but the `--batch` keyword must be used instead of `--single`. For example to submit all .fasta files in "C:\Sequences" and save the results in "C:\Sequences\Results\Output <timestamp>" you would use the following:

`python -m PSIPREDauto.commandline --batch --input "C:\Sequences" --email "foo@bar.com" --output "C:\Sequences\Results"`

There is also an `--interval` keyword argument that works in the same way as above, however only takes integer values. As when used in a Python script the default interval is 4 minutes.

## Other things to note
  
* Remember that all file paths must be provided as a string! Alternatives such as the path without quotes or pathlib.Path objects will result in an exception.
* The progress bar will only update after it successfully receives results from the server (default every 4 minutes), lack of movement on the progress bar does not mean nothing is happening. Additionally the progress bar isn't particlarly accurate for small batches as it doesn't take into account the waiting interval. 
  
## Logging

PSIPREDauto uses the python `logging` module. Enable `logging` to see more information about what is going on behind the scenes.

## Known issues

* Very large batches (~>1000 sequences) are currently prone to failure due to the server eventually rejecting a request even if the time interval is long. Possibly due to high load from other users? Working on a feature to catch this exception and prevent the crash here.
* Very large batches also seem to sometimes experience a problem where progress stops without an exception being thrown. Currently unsure what is causing this issue but it is suspected to be due to the modules internal job queue filling up with jobs that cannot have their results retrieved.
* Losing internet connection during a job will result in a crash.
