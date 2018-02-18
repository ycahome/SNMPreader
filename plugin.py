
#
#   SNMPreader Plugin
#
#   Ycahome, 2017
#   https://www.domoticz.com/forum
#
#
"""
<plugin key="SNMPreader" name="SNMP Value Reader" author="ycahome" version="1.0.0" wikilink="m" externallink="https://www.domoticz.com/forum/viewtopic.php?f=65">
    <params>
        <param field="Address" label="Server IP" width="200px" required="true" default="192.168.1.1"/>
        <param field="Mode1" label="OID" width="200px" required="true" default="1.3.6.1.2.1.25.3.2.1.1.2"/>
        <param field="Mode2" label="Community" width="200px" required="true" default="public"/>
        <param field="Mode3" label="Domoticz TypeName" width="200px">
            <options>
                <option label="Custom" value="Custom"/>
                <option label="Text" value="Text"/>
                <option label="Temperature" value="Temperature"  default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz

import sys
sys.path.append('/usr/lib/python3/dist-packages/')
from pysnmp.entity.rfc3413.oneliner import cmdgen


import json
import urllib.request
import urllib.error

from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta


#############################################################################
#                      Domoticz call back functions                         #
#############################################################################

def onStart():

    global gdeviceSuffix
    global gdeviceTypeName

    gdeviceSuffix = "(SNMP)"
    interval = 60

    createDevices()
    if Parameters["Mode6"] == "Debug":
        DumpConfigToDebug()
    

    ServerIP = str(Parameters["Address"])
    snmpOID = str(Parameters["Mode1"])
    snmpCommunity = Parameters["Mode2"]

    snmpDataValue = str(getSNMPvalue(ServerIP,snmpOID,snmpCommunity))


    Domoticz.Heartbeat(interval)
    return True

def onHeartbeat():

    ServerIP = str(Parameters["Address"])
    snmpOID = str(Parameters["Mode1"])
    snmpCommunity = Parameters["Mode2"]

    # Get new information and update the devices
    snmpDataValue = str(getSNMPvalue(ServerIP,snmpOID,snmpCommunity))

    UpdateDevice(1,0,snmpDataValue)
    Domoticz.Log("SNMP Value retrieved:"+snmpDataValue)


    return True

#############################################################################
#                         Domoticz helper functions                         #
#############################################################################

def DumpConfigToDebug():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Log("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Log("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Log("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Log("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Log("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Log("Device sValue:   '" + Devices[x].sValue + "'")


def UpdateDevice(Unit, nValue, sValue):

    # Make sure that the Domoticz device still exists before updating it.
    # It can be deleted or never created!

    if (Unit in Devices):
        Devices[Unit].Update(nValue, str(sValue))
        Domoticz.Debug("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")

#############################################################################
#                       Device specific functions                           #
#############################################################################

def createDevices():

    # Are there any devices?
    if len(Devices) != 0:
        # Could be the user deleted some devices, so do nothing
        Domoticz.Debug("Devices Already Exist.")
        return

    # Give the devices a unique unit number. This makes updating them more easy.
    # UpdateDevice() checks if the device exists before trying to update it.

    # Add Power and temperature device(s)
    Domoticz.Device(Name=gdeviceSuffix, Unit=1, TypeName=Parameters["Mode3"]).Create()

    Domoticz.Log("Devices created.")


def getSNMPvalue(ServerIP,snmpOID,snmpCommunity):

    cmdGen = cmdgen.CommandGenerator()

    #genData = cmdgen.CommunityData('public')
    genData = cmdgen.CommunityData(str(snmpCommunity))
    Domoticz.Debug("genData Loaded." + str(genData))

    TTData = cmdgen.UdpTransportTarget((str(ServerIP), 161), retries=2)
    Domoticz.Debug("TTData Loaded." + str(TTData))

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(genData,TTData,snmpOID)
    Domoticz.Debug("DATA Loaded." + str(varBinds))

    # Check for errors and print out results
    if errorIndication:
        Domoticz.Log(str(errorIndication))
    else:
        if errorStatus:
            Domoticz.Log('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1] or '?'))
        else:
            for name, val in varBinds:
                Domoticz.Debug('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

                return val.prettyPrint()

#
# Parse an int and return None if no int is given
#

def parseIntValue(s):

        try:
            return int(s)
        except:
            return None

#
# Parse a float and return None if no float is given
#

def parseFloatValue(s):

        try:
            return float(s)
        except:
            return None



