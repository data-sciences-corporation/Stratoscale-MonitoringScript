#!/usr/bin/python3
########################################################################################################################
#                                           Stratoscale - Monitoring Script                                            #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# INTRODUCTION:                                                                                                        #
#   This script is part of a toolset which is being developed to help monitor and maintain a customer's                #
#   Stratoscale environment. It will monitor multiple components in the Stratoscale stack, which are otherwise         #
#   not monitored.                                                                                                     #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# MODULE DETAILS:                                                                                                      #
#   This module is for TODO                                                                                            #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v1.0 - 18 December 2018 (Richard Raymond)                                                                            #
#   - Test Template v0.2                                                                                               #
#   - First draft of log space monitoring script. Uses lazy create_bash-run_bash-delete_bash file method. TODO Optimise#
# v1.1 - 19 December 2018 (Richard Raymond)                                                                            #
#   - Test Template v0.3                                                                                               #
#                                                                                                                      #
########################################################################################################################
import os
import sys
import yaml
import subprocess

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# CONFIG VARIABLES
rootpath = sys.argv[2]
config = yaml.load(open(rootpath + '/config.yml', 'r'))                    # Pull in config information from YML file.
testdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"        # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"    # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"    # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 4                                                                  # Initialize OK/NOK marker
error_message = "*UPDATE ME*"                                               # Error message to provide overview
error_data = "*UPDATE ME*"                                                  # Full error contents
# ----------------------------------------------------------------------------------------------------------------------
# TEST SCRIPT DATA GOES HERE

# Make a bash script
bashscript = open("deleteme.sh", "w+")
bashscript.write("#!/bin/bash\nconsul exec df -h | grep log | awk {\'print $1 $6\'}")
bashscript.close()

# Allow execute access
os.chmod("deleteme.sh", 755)
process = subprocess.Popen('./deleteme.sh', stdout=subprocess.PIPE)
output, error = process.communicate()
# noinspection PyRedeclaration
error_data = output
# Clean dirty bash response
nodelist = output.split('%')
worstcase = 0
# Test node log space capacities for each node.
for i in range(len(nodelist)-1):
        nodelist[i] = nodelist[i].strip("\n")
        node, space = nodelist[i].split(":")
        if int(space) > 90:
                worstcase = 3
                error_message = error_message + "\n CRITICAL: " + node + " - " + space + "% full"
        elif int(space) > 75:
                worstcase = 2
                error_message = error_message + "\n ERROR: " + node + " - " + space + "% full"
        elif int(space) > 60:
                worstcase = 1
                error_message = error_message + "\n WARNING: " + node + " - " + space + "% full"
        if int(result) < int(worstcase):
                result = worstcase
        worstcase = 0
# Delete bash script file
os.remove("deleteme.sh")

# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
reportfile = open(reportdirectory + sys.argv[3] + '.txt', "a")              # Open the current report file
reportfile.write('TEST:         ' + sys.argv[1] + '\n')                     # Open test section in report file
reportfile.write('RESULT:       ' + config['errortypes'][result])           # Add test status to report
if result != 0:                                                             # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(reportdirectory + errorfilename + '.txt', "w+")        # Create error report file
    errorfile.write(error_data)                                             # Write error data to error file
    errorfile.close()                                                       # Close error file
    reportfile.write(" : " + error_message + '\n')                          # Add error message to report
    reportfile.write(" Please look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n' + config['formatting']['linebreak'] + '\n')           # Add line break to report file, after test
reportfile.close()                                                          # Close report file