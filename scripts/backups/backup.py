#!/usr/bin/python2.7
#A script that maintains backups of the server if called regularly (say every 6 hours as a cron job). Calls a git update for short term updates and creates tar archives weekly. These archives are maintained for up to 4 weeks before deletion. And archive older than 4 weeks will be deleted. Archives set in the 'future' will be ignored

#!/bin/bash
#pushes exerything here to the git repo
#git@github.com:BlockSocUNSW/Server-Backups.git


import sys
import os
import time
import re
import logging
import datetime

# import options.
from backup_options import *

NOW = datetime.datetime.now()

# setup logger.
logger = logging.getLogger('Server Backup')
handle = logging.FileHandler(LOG_NAME)
formatter = logging.Formatter(LOG_FORMAT)
handle.setFormatter(formatter)
logger.addHandler(handle) 
logger.setLevel(logging.INFO)

# Os command wrapper.
def osCmd(command, critical=False):
	status = os.system(command)
	if status != 0:
		logger.critical("Failed to send command: [" + command + "]")
		if critical:
			raise Error("Failed to send command: [" + command + "]")
	return status

# Sends a message to a screen via -X stuff.
def serverCmd(command,critical=False):
    for screen in SERVER_SCREEN_NAMES:
        send = "screen -S " + screen + " -p 0 -X stuff \"\n" + command + "\n\""
        status = os.system(send)
    
        if status != 0:
            logger.critical("Command failed: [" + screen + "] " + command)
            if critical:
			raise Error("Command failed: [" + screen + "] " + command)
    return

# Script to push the server data to a git repo.
def gitPush():
    cwd = os.getcwd()
    os.chir(BACKUP_TARGET_DIR)
    osCmd("git add server scripts")
    osCmd("git commit  -m " + NOW.strftime("%Y-%m-%d %H:%M"))
    osCmd("git push -u origin master")
    osCmd("git gc")
    os.chir(cwd)
    return
    
# creates a tar backup of the target directory.
def createTar():
    #get the name
    name = NOW.strftime("%d-%m-%y-%H-%M-%S:") + str(int(time.time())) + ".tar"
    #make the full path to the tar.
    name = os.path.join(BACKUP_DIR, name)
    #move into the target directory.
    cwd = os.getcwd()
    os.chdir(BACKUP_TARGET_DIR)
    target = "*"
    exclude = " "
    #and any excludes
    if len(BACKUP_TARGET_EXCLUDE) != 0:
        exclude = ""
        for i in BACKUP_TARGET_EXCLUDE:
            exclude = exclude + "--exclude " + i + " "
    #compile and execute command
    command = "tar -cf " + name + " " + target + " " + exclude
    osCmd(command, critical=True)
    #return to the original dir.
    os.chdir(cwd)
    return

#removes a file/directory.
def removeBackup(path):
    logger.info("Removing path: " + path)
    osCmd("rm -r " + path)
    return

if __name__=='__main__':
    logger.info("Starting backup process for: " + NOW.strftime("%d-%m-%y-%H-%M-%S"))
    serverCmd("say Starting backup")
    serverCmd("save-all")
    serverCmd("save-off")
    serverCmd("stop")
    time.sleep(3)
    try:
        #get the backups
        os.chdir(BACKUP_DIR)
        backups = []
        for f in os.listdir("."):
            if len(TAR_FORM.findall(f)) == 1:
                #get the epoch time and save it and the file name
                t = int(f[0:len(f)-4].split(":")[1])
                if t > time.time():
                    logging.info("Tar [" + f + "] set in future. Ignoring.")
                else:
                    backups.append([t,f])
                    
        #sort the backups by epoch.
        backups.sort()
        logger.info("Current Backups: ")
        for b in backups:
           logger.info("    " + b[1]) 
           
        # if there are no backups, make one.
        if len(backups) == 0:
            logging.info("No backups. Creating one.")
            createTar()
        else:
            #otherwise, if the newest backup is outside of the minimum bound, make a new backup
            if time.time() - backups[len(backups)-1][0] > MIN_BACKUP_AGE:
                logging.info("New backup required.")
                createBackup()
            #prune off any backups that are older than the max bound.
            while len(backups) != 0 and  time.time() - backups[0][0] > MAX_BACKUP_AGE:
                logging.info("Removing old backup: " + backups[0][1])
                path = os.path.join(BACKUP_DIR, backups[0][1])
                removeBackup(path)
                del backups[0]
                
        logger.info("Tar check done.")
        
        logger.info("Pushing to git.")
        #gitPush()
        logger.info("Git push done.")
        #send alert that backup complete and enable saves.
        os.chdir(os.path.dirname(UP_SCRIPT))
        osCmd(UP_SCRIPT + "&", True)
        time.sleep(5)
        serverCmd("save-on")
        serverCmd("save-all")
        serverCmd("say Backup complete")
        logger.info("Backup done.")
        logger.info("")
    except:
        os.chdir(os.path.dirname(UP_SCRIPT))
        osCmd(UP_SCRIPT + "&")
        time.sleep(5)
        logger.critical( "Error:"+ str(sys.exc_info()))
        serverCmd("save-on")
        serverCmd("save-all")
        serverCmd("say Backup complete")
        serverCmd("WARNING: Exception occurred in backup. Contact admin immediately.")
        logger.critical("An exception occured. Backup aborted.")
        logger.info("")

