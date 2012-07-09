import sys
import time
from Daemon.daemon import Daemon
import logging
import logging.handlers
from tempsensor import TemperatureSensor
from collections import deque
import mailutils

############################
# Load config file
############################
try:        
    # Import config module
    import config
    
    def checkConfigValue(name, default=False):
        value = getattr(config, name, default)
        if not value and not hasattr(config, name):
            print "Required value %s not found in config file" % (name)
            sys.exit(2)
        return value
            

    # Check required config values existence
    INPUT = checkConfigValue("INPUT")
    CHECK_FREQ = checkConfigValue("CHECK_FREQ")
    MAX_TEMP = checkConfigValue("MAX_TEMP")
    WARNING_FREQ = checkConfigValue("WARNING_FREQ")
    ADMINS = checkConfigValue("ADMINS")
    SENDER = checkConfigValue("SENDER")
    SUBJECT = checkConfigValue("SUBJECT")
    
    # Calculate MAXLEN: max temperatures to store
    MAXLEN = int(WARNING_FREQ / CHECK_FREQ)
    if MAXLEN <= 0:
        print "Cannot calculate MAXLEN value from WARNING_FREQ / CHECK_FREQ"
        sys.exit(2)

    # Check optional config values existence or load default values
    LOGFILE = checkConfigValue("LOGFILE", "/tmp/temp-daemon.log")

    # If loglevel is not defined, use as default level INFO
    LOGLEVEL = checkConfigValue("LOGLEVEL", logging.INFO)
    if LOGLEVEL != logging.INFO:
        try:
            # If is loglevel is defined, try to load in logging module
            LOGLEVEL = getattr(logging, LOGLEVEL)
        except AttributeError:
            print "Incorrect log level in config file. Try to use: DEBUG, INFO, WARNING, ERROR or CRITICAL"
            print "Using default value: INFO"
            LOGLEVEL = logging.INFO

    LOGFORMAT = checkConfigValue("LOGFORMAT", "%(asctime)-15s %(levelname)s: %(message)s")

    PIDFILE = checkConfigValue("PIDFILE", "/tmp/temp-daemon.pid")        
except ImportError, exp:
    print "Unable to load config.py file, please copy config_example.py and edit it"
    sys.exit(2)

############################
# Temperature Check Daemon
############################
class TempCheckDaemon(Daemon):
    tempsensor = None    
    # Stores last warning email timestamp
    lastwarning = 0
    # Stores latest MAXLEN read temperatures
    values = deque(maxlen=MAXLEN)
    
    # Initializes temperature sensor
    def getSensor(self):
        if not self.tempsensor:
            self.tempsensor = TemperatureSensor(INPUT)
        return self.tempsensor 
    
    # Main daemon loop
    def run(self):
        while True:            
            self.getSensor().open()
            
            while True:
                # Read temperature temp
                temp = self.getSensor().getTemperature()
                
                # Check if its a valid value
                if temp:
                    logging.debug("Temperature: %f degrees" % (temp))
                    self.values.append({'time': time.time(), 'value': temp})
                    self.checkWarning(temp)                                                            
                else:
                    logging.error("Error couldn't get temp from sensor")
                
                # Wait to read again the sensor
                time.sleep(CHECK_FREQ)

            tempsensor.close()
    
    # Check if warning mail must be send to ADMINS    
    def checkWarning(self, temp):                
        if (temp > MAX_TEMP) and (time.time() - self.lastwarning > WARNING_FREQ):
            logging.info("Sending warning mail to admins: %s" % (str(ADMINS)))
            
            # Build message contents
            content = ""            
            content += "Time                      Value\n"        
            for i in range(len(self.values)):
                content += "%s  %f degrees\n" % (time.ctime(self.values[i]['time']), self.values[i]['value'])
            
            # Try to send mails
            try:                
                mailutils.sendMail(SENDER, SUBJECT, ADMINS, content)                
            except Exception, ex:
                logging.error("Cannot send warning mail, reason: %s" % (str(ex)))
            
            self.lastwarning = time.time()                                       

############################
# Log config
############################

# Based in basicConfig function from logging
# Just changed FileHandler to RotateFileHandler and references to local logging module
def logConfig(**kwargs):    
    try:        
        filename = kwargs.get("filename")
        if filename:
            mode = kwargs.get("filemode", 'a')            
            hdlr = logging.handlers.RotatingFileHandler(filename, maxBytes=1 * 1024 * 1024, backupCount=3)
        else:
            stream = kwargs.get("stream")
            hdlr = logging.StreamHandler(stream)
        fs = kwargs.get("format", logging.BASIC_FORMAT)
        dfs = kwargs.get("datefmt", None)
        fmt = logging.Formatter(fs, dfs)
        hdlr.setFormatter(fmt)
        logging.root.addHandler(hdlr)
        level = kwargs.get("level")
        if level is not None:
            logging.root.setLevel(level)
    except Exception, ex:
        print("Error while configuring log")
        print ex        

############################
# Main function
############################
def main():    
    daemon = TempCheckDaemon(PIDFILE)
    if len(sys.argv) == 2:
        # First config logging
        if "run" == sys.argv[1]:
            logConfig(stream=sys.stdout, level=logging.DEBUG, format=LOGFORMAT)
        else:
            logConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
        
        # Command
        if "start" == sys.argv[1]:
            print "Starting daemon"
            daemon.start()
        elif "stop" == sys.argv[1]:
            print "Stopping daemon"
            daemon.stop()
        elif "restart" == sys.argv[1]:
            print "Restarting daemon"
            daemon.restart()
        elif "run" == sys.argv[1]:
            print "Running daemon in debug mode. Press CTRL + C to close."                       
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|run" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    main()