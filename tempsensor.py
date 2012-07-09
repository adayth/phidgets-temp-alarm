from ctypes import *
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit
import logging

class TemperatureSensor:
    def __init__(self, input):            
        logging.info("Creating TemperatureSensor for sensor input %i" % (input))
        
        self.input = input
        
        #Functions to listen phidgets events
        def inferfaceKitAttached(e):
            logging.info("InterfaceKit attached")            
        
        def interfaceKitDetached(e):
            logging.info("InterfaceKit detached")
            
        def interfaceKitError(e):
            try:
                source = e.device
                logging.error("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
            except PhidgetException as e:
                logging.error("Phidget Exception %i: %s" % (e.code, e.details))                
        
        try:
            #Create a phidgets InterfaceKit object
            self.ik = InterfaceKit()
            #Attach handlers
            self.ik.setOnAttachHandler(inferfaceKitAttached)
            self.ik.setOnDetachHandler(interfaceKitDetached)
            self.ik.setOnErrorhandler(interfaceKitError)                        
            #Open phidgets
            self.ik.openPhidget()            
            logging.info("TemperatureSensor created")
        except PhidgetException as e:
            logging.error("Phidget Exception %i: %s" % (e.code, e.details))
    
    #Wait for attachment
    def open(self):        
        try:
            logging.info("Waiting for InterfaceKit attachment")
            self.ik.waitForAttach(5000)
        except PhidgetException as e:
            logging.error("Phidget Exception %i: %s" % (e.code, e.details))
    
    #Close phidget
    def close(self):        
        try:
            self.ik.closePhidget()
        except PhidgetException as e:
            logging.error("Phidget Exception %i: %s" % (e.code, e.details))
    
    #Obtains current sensor temperature
    def getTemperature(self):
        value = False            
        try:
            value = self.ik.getSensorValue(self.input)
        except PhidgetException as e:
            logging.error("Phidget Exception %i: %s" % (e.code, e.details))
        
        #So this returns temperature value or False   
        if value:
            value = (value * 0.2222) - 61.111
        return value
        
