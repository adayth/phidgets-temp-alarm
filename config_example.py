#################################################
# Configure values to detect temperatures above
# limits and send a warning email to admins
#################################################

#################################################
# Required config values
#################################################

# INPUT: interface kit sensor input to read
INPUT = 0 

# CHECK_FREQ: check sensor temperature each CHECK_FREQ seconds
CHECK_FREQ = 60

# MAX_TEMP: above this temperature in degrees value, warning mails will be send 
MAX_TEMP = 30

# WARNING_FREQ: send a mail warning each WARNING_FREQ seconds
WARNING_FREQ = 1800

# ADMINS: mail addresses to send warnings
ADMINS = (
          'your_email1@domain.com',
          #'your_email2@domain.com',          
)

# SENDER: address to be the sender of warning mails
SENDER = 'noreply@cicei.com'

# SUBJECT: subject for the warning mails
SUBJECT = 'WARNING: Report mail temperatures'

#################################################
# Optional config values (default values should be ok)
#################################################

# Log config for a standard python logging
# http://docs.python.org/library/logging.html

# Path to log file
#LOGFILE = "/tmp/temp-daemon.log"

# Loglevel to execute. Levels: DEBUG, INFO, WARNING, ERROR or CRITICAL
# The recommended level is INFO
#LOGLEVEL = "INFO"

# Format of log entries
#LOGFORMAT = "%(asctime)-15s %(levelname)s: %(message)s"

# PID file for daemon
#PIDFILE = "/tmp/temp-daemon.pid"
