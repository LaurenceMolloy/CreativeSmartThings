################################################################
#           Copyright (c) Creative Smart Things 2020           #
#                                                              #
# Blog Post ID: 287                                            #
# Script Name:  test_gutenberg_file_index.py                   #
# Version:      1.0                                            #
# Date:         25 February 2020                               #
# Author:       Laurence Molloy                                #
# Purpose:      Tests existence and validity of all zip files  #
#               listed in a Project Gutenberg file index       #
# Requirements: an index file manually generated from a        #
#               Project Gutenberg zip file repository using    #
#               find aleph.gutenberg.org/ -type f > index.txt  #
################################################################

import re
import zipfile
import os.path

# file index should be
# 1. called index.txt
# 2. placed in the current working directory
file_index = "index.txt"

# lists for counting files of different types
file_list = []
file_good = []
file_bad = []
file_missing = []
file_not_zip = []

with open(file_index) as idx:
    file_list = idx.readlines()

# process all files in the file index
processed_files = 0
for f in file_list:
    processed_files += 1
    fname = f.rstrip()
    # existence test
    if (not os.path.isfile(fname)):
        file_missing.append(fname)
    # file type test
    elif (not zipfile.is_zipfile(fname)):
        file_not_zip.append(fname)
    else:
        file = zipfile.ZipFile(f.rstrip(), mode='r')
        # file corruption test
        if file.testzip() is not None:
            file_bad.append(fname)
        # all good zip files will reach here
        else:
            file_good.append(fname)
    if (processed_files % 100 == 0):
        print("Tested" , processed_files , "files")

# report statistics
print("FILE COUNT:", len(file_list))
print("GOOD:", len(file_good))
print("BAD:", len(file_bad))
print("MISSING:", len(file_missing))
print("NOT ZIP:", len(file_not_zip))

# identify bad (possibly corrupt) zip files
if len(file_bad):
    print("[BAD FILES]")
    print("\t", end = '')
    print(*file_bad, sep = "\n\t")

# identify missing files
if len(file_missing):
    print("[MISSING FILES]")
    print("\t", end = '')
    print(*file_missing, sep = "\n\t")

# identify non-zip files
if len(file_not_zip):
    print("[NOT ZIP FILES]")
    print("\t", end = '')
    print(*file_not_zip, sep = "\n\t")

# flag if no errors are found - gold star!
if len(file_list) == len(file_good):
    print("*** ALL GOOD ***")
