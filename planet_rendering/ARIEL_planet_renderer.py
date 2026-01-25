#!/usr/bin/env python3
"""
Generates RadVel planet .py files for ARIEL/KPF target stars. 
Uses Jinja2 to render files from "planet_template_py.j2" template file
"""

#imports
import numpy as np
import pandas as pd
from ariel_kpf.paths import get_latest_kpf_targets_file
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import time
import sys

#A couple of directory defintions (can run this file in whatever directory)
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates" #Helps Jinja2 find the templates
OUT_DIR = BASE_DIR/"build"
OUT_DIR.mkdir(parents=True, exist_ok=True)  #Creates folder to store rendered planet files

env = Environment(loader = FileSystemLoader(TEMPLATE_DIR), autoescape= False) # creating jinja2 rendering environment
# autoescape set to false since we don't want special characters to be escaped.

def main():
    """
    Renders planet.py files for ARIEL/KPF targets, using jinja2 templating.
    """
    startTime = time.time() #Starts the duration timer for this renderer.
    print("Loading Template....")
    template = env.get_template("planet_template.py.j2") # defining template
    print("Template Loaded ✅!")

    #Extracting latest KPF targets list
    print("Fetching KPF Target Data....")
    data = pd.read_csv(get_latest_kpf_targets_file())
    print(f"Loaded: {get_latest_kpf_targets_file()}")


    tot = len(data['ticid']) #how many targets are we rendering?
    print(f"Total Targets: {tot}")
    print("="*80)

    i = 1 #counter variable
    for _, row in data.iterrows():

        sys.stdout.write(f"\rRendering: tic{row['ticid']} -- ({i}/{tot}) ")
        i += 1 #increasing counter

        rendered = template.render(
            ticid = row['ticid'], #TIC ID
            per1 = row['period'], #Orbital period
            tc1 = row['epoch'], #Time of inferior conjunction
            k1 = 50 #Guess for RV semi-amplitude
        )
        file = f"tic{str(row['ticid'])}.py" #Saving file as "tic##########.py"
        (OUT_DIR / file).write_text(rendered)


    print("\n"+'='*80)
    print("Rendering Complete ✅!")
    print(f"RadVel planet files output to {OUT_DIR}")



if(__name__) == "__main__":
    main()



