#!/usr/bin/python
# -*- coding: utf-8 -*-
# ====================================================================
# @authors: Joe Del Rocco
# @since: 7/12/2021
# @summary: Script to generate sun and sky irradiance with libRadtran.
# ====================================================================
# site.YYYYMMDDhhmm.csv
# edir, edn, eglo -> direct beam, diffuse down, global
# Spectral energy is in W/m2
# ====================================================================
# Key,Azimuth,Altitude,Sum,350,351,352,...
# edir,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# edn,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,5...
# eglo,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky0,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky1,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky2,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky3,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky4,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky5,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky6,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# sky7,214.532,63.3295,8.13E+02,4.60E-01,5.34E-01,5.90E-01,...
# ====================================================================
import argparse
import sys
import os
import re
from datetime import datetime, timezone
import dateutil
import shutil
import subprocess
import shlex
import logging
from threading import Timer
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd


'''
Log to file and standard out with one call.
'''
def log(args, msg):
    if not args.log: return
    msg = str(msg)
    print(msg)
    with open(args.logpath, "a") as f:
        f.write(msg + '\n')


'''
Helper function to kill a process.
'''
def killProcess(process, timeout):
    timeout["value"] = True
    process.kill()


'''
Helper function to run a shell command with timeout support.
'''
def runCMD(cmd, timeout_sec):
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = {"value": False}
    timer = Timer(timeout_sec, killProcess, [process, timeout])
    timer.start()
    stdout, stderr = process.communicate()
    timer.cancel()
    return process.returncode, stdout, stderr, timeout["value"]


'''
Helper function to copy a single file or filetree from one location to another.
'''
def copy(src, dest):
    try:
        if os.path.isfile(src):
            shutil.copy(src, dest)
        else:
            for filename in os.listdir(src):
                srcfile = os.path.join(src, filename)
                destfile = os.path.join(dest, filename)
                if os.path.isfile(srcfile):
                    shutil.copy(srcfile, destfile)
                else:
                    shutil.copytree(srcfile, destfile)
    except Exception as ex:
        logging.error(ex.message)


'''
Verify that a string is a valid date or datetime
:param datestr: String that is to be verified.
:param datefmtstr: Format datetime string (e.g. "%Y-%m-%d")
'''
def verifyDateTime(datestr, datefmtstr):
    try:
        datetime.strptime(datestr, datefmtstr)
        return True
    except ValueError:
        return False


def loadTemplate(args):
    args.template = "in/template.inp"

    #contents = ""
    with open(args.template) as file:
        contents = file.read()

    if not contents:
        log(args, "Error reading template file: '" + args.template + "'")
        return False

    args.templatedata = contents
    return True


def loadSiteFile(args):
    #contents = ""
    with open(args.sitefile) as file:
        contents = file.read()

    if not contents:
        log(args, "Error reading site file: '" + args.sitefile + "'")
        return False

    args.sitedata = contents
    return True


def simulateDay(args):
    # create and config libRadtran inp file
    fname = "in/" + args.stub + ".inp"
    with open(fname, "w+") as file:
        # config: template defaults
        file.write(args.templatedata)

        # config: site parameters
        file.write("#------------------------------------------\n")
        file.write("# SITE PARAMETERS\n")
        file.write("#------------------------------------------\n")
        file.write("\n")
        file.write(args.sitedata)

        # config: more parameters
        file.write("#------------------------------------------\n")
        file.write("# CUSTOM PARAMETERS\n")
        file.write("#------------------------------------------\n")
        file.write("\n")

        # config: timestamp
        dt = dateutil.parser.parse(args.datetime)
        dt = dt.replace(second=0, microsecond=0)  # ignore beyond minutes
        dtutc = dt.astimezone(timezone.utc)       # libRadtran needs UTC
        file.write("# simulation datetime\n")
        file.write("time " + dtutc.strftime("%Y %m %d %H %M %S") + "\n")
        file.write("\n")

        # config: output level
        if args.verbose:
            file.write("verbose\n")
        else:
            file.write("quiet\n")
        file.write("\n")

# # time: 2013/07/26 13:15 (quarter: 3, month: 7, week: 30, day: 207, hour: 13)
# # sun: (214.5320, 63.3295, 26.6705) (azm, alt, sza)
#
# # log
# verbose
#
# # date, time, site, sun
# time YYYY MM DD hh mm ss
# day_of_year 207           # Correct for Earth-Sun distance
# sza 26.6705               # Solar zenith angle
#
# # spectral range
# spline 350 1780 1         # Interpolate from first to last in step
# wavelength 350 1780       # Wavelength range [nm]


def simulateSky(args):
    pass

# # radiance
# phi0 214.5320             # Solar azimuth angle
# phi 214.5320              # Sensor azimuth angle
# umu -0.033                # Sensor zenith angle (cos of angles 26.6705)
# output_user lambda uu


def output(args):
    pass


'''
Program entry point.
'''
def main():
    # handle command line args
    parser = argparse.ArgumentParser(description='Script to generate sun and sky irradiance with libRadtran. All output is saved to a .csv file.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_help = True
    # required parameters
    parser.add_argument('sitefile', type=str, help='filepath to site config')
    parser.add_argument('datetime', type=str, help='datetime to simulate (00/00/0000 00:00 TZN)')
    # parser.add_argument('-p', '--photo', dest='photo', type=str, help='path to fisheye sky photo')
    # parser.add_argument('-c', '--cover', dest='cover', type=int, help='sky cover (1=UNK, 2=CLR, 3=SCT, 4=OVC)')
    # # optional parameters
    parser.add_argument('-r', '--range', dest='range', type=int, nargs=2, default=(350, 2500), help='spectral range (def 350 2500)')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log progress to stdout and file')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output')
    # parser.add_argument('-cs', '--circumsolar', dest='circumsolar', type=float, default=0, help='consider circumsolar region (radius)')
    args = parser.parse_args()

    # error checking
    if not verifyDateTime(args.datetime, "%m/%d/%Y %H:%M %Z"):
        print("Error: invalid datetime: '" + args.datetime + "'")
        sys.exit(2)
    if not os.path.exists(args.sitefile):
        print("Error: no site file found: '" + args.sitefile + "'")
        sys.exit(2)

    # this instance run stub name will be: site + . + datetime
    args.stub = os.path.splitext(os.path.basename(args.sitefile))[0] + "." + re.sub('[/: ]', '', args.datetime)
    #print(args.stub)

    # start logging
    args.logpath = "./out/" + args.stub + ".txt"
    log(args, "-" * 80)
    log(args, ' '.join(sys.argv))

    # configure matplotlib
    params = {'legend.fontsize': 'x-large',
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'xx-large',
              'xtick.labelsize': 'large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # load input files
    if not loadTemplate(args):
        sys.exit(2)
    if not loadSiteFile(args):
        sys.exit(2)

    # simulate w/ libRadtran for the datetime to get sun and sky irradiance
    simulateDay(args)
    sys.exit(0)

    # simulate w/ libRadtran for sky patch radiances
    simulateSky(args)

    # log metrics

    # output final sky data file
    output(args)


if __name__ == "__main__":
    main()
