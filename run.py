import sys
import time
from Daemon.daemon import Daemon
import logging
from tempsensor import TemperatureSensor
import subprocess

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
    def run(self):
        while True:
            tempsensor = TemperatureSensor(INPUT)
            tempsensor.open()
            
            while True:
                # Read temperature value
                value = tempsensor.getTemperature()
                
                # Send warning if needed
                if value:
                    logging.debug("Temperature: %f degrees" % (value))
                    if value > MAX_TEMP:
                        logging.INFO("Sending warning mail")                     
                else:
                    logging.error("Error couldn't get value from sensor")
                
                # Wait to read again the sensor
                time.sleep(CHECK_FREQ)

            tempsensor.close()

############################
# Main function
############################
def main():    
    daemon = TempCheckDaemon(PIDFILE)
    if len(sys.argv) == 2:
        # First config logging
        if "run" == sys.argv[1]:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOGFORMAT)
        else:
            logging.basicConfig(filename=LOGFILE, level=LOGLEVEL, format=LOGFORMAT)
        
        # Command
        if "start" == sys.argv[1]:
            print "Starting daemon"
            daemon.start()
        elif "stop" == sys.argv[1]:
            print "Stoping daemon"
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