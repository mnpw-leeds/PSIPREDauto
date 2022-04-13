# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 22:27:47 2022

@author: pnw2
"""

import argparse, sys
from PSIPREDauto_functions import single_submit, batch_submit

parser = argparse.ArgumentParser(description="psipredapi_auto command line implementation. "\
                                 "Required commands: Either --single or --batch, --input ,"\
                                 " --email  and --output. "\
                                 "Optional commands: --interval. Arguments can be provided in any order")

parser.add_argument("--single", "-s", action="store_true", help="Specify a single submission")
parser.add_argument("--batch", "-b", action="store_true", help="Specify a batch submission")
parser.add_argument("--input", "-i", help="Specify the input file path. For --single give the full path for "\
                    "the file to be submitted, for --batch specify the directory containing the files", required=True)
parser.add_argument("--output", "-o", help="Output directory where results will be saved.", required=True)
parser.add_argument("--email", "-e", help="Your email address. Required by the PSIPRED API to keep track of how many jobs you are running.", required=True)
parser.add_argument("--interval", "-t", type=int, default=4, help="How often to poll the server for results in minutes. "\
                    "Requires whole integer values and defaults to 4. The PSIPRED team reccommend 2-5 minutes for most jobs. "\
                    "For longer sequences and large batches higher values are reccommended. Setting a lower value is often "\
                    "ok for individual files or small batches but may lead to instability for large jobs as the server will "\
                    "refuse requests if too many are submitted too quickly.")
    
args = parser.parse_args()
dic_args = vars(args)
print("\nInput parameters:")
for arg in dic_args:
    print(f"{arg} = {dic_args[arg]}")

if args.single == True and args.batch == True:
    print("Error: --single and --batch cannot both be specified")
    sys.exit()

if args.single == False and args.batch == False:
    print("Error: Please specify either --single or --batch")
    sys.exit()
    
if args.interval < 1:
    args.interval = 1
    print("Warning: Interval too low, changed to 1")
    
if args.single == True:
    single_submit(args.input, args.email, args.output, interval=args.interval)

if args.batch == True:
    batch_submit(args.input, args.email, args.output, interval=args.interval)