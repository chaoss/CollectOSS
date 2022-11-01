import os
import os.path as path


#needed as a workaround since python executes imported files
#This presents a problem since importing the phase functions themselves needs information from the config
#while the config needs the phase names before population
#The solution is to either make the user define the phase names seperate or to do this
#Which is to import the .py as text and parse the function names.
def get_phase_names_without_import():
    raw_file = open("augur/tasks/start_tasks.py")
    lines = raw_file.readlines()
    raw_file.close()

    phase_names = []

    for line in lines:
        if "def " in line and "_phase(" in line:
            without_def = line.split()[1]
            phase_names.append(without_def.split('(')[0])
    

    return phase_names