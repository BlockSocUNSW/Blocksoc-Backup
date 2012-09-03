import re
#This is the screen alias (from: screen -S [alias] [server init script]) 
#that the server runs under. Will be used to send commands to the 
#server.
SERVER_SCREEN_NAMES = [ "mc_fluid","mc_creative", "mc_tekkit_restricted", "mc_tekkit_creative", "mc_experiment"]
#The path that is to be backed up instide tar files.
BACKUP_TARGET_DIR = "/home/minecraft/"
#If there are any files/directories that you want to exclude from the 
#tar in this path, add them here.
BACKUP_TARGET_EXCLUDE = ["backups", ".git"]
#The directory were tar backups are placed
BACKUP_DIR = "/home/minecraft/backups/"
#If the earliest backup is older than this then a new back up will be 
#created (in seconds)
MIN_BACKUP_AGE = 604800 - 3600 #number of seconds in a week - hour of overhead
#Any backup older than this will be deleted.
MAX_BACKUP_AGE = 604800 * 4 + 3600 #number of seconds in 4 weeks + hour of over head
#regex form for tar files. Anything not matching exactly will be 
#ignored. Everything except the epoch time is just for human 
#readability. 
#[day][-][month][-][year][-][hour][-][minute][-][second]:[seconds since 
#epoch (gmtime)][\.tar]
TAR_FORM = re.compile('\d\d-\d\d-\d\d-\d\d-\d\d-\d\d:\d+.tar')
#Log format options.
LOG_FORMAT = '%(asctime)-15s\t%(levelname)s\t%(message)s'
LOG_NAME = "server_backup.log"


UP_SCRIPT="/home/minecraft/server/up.sh"
