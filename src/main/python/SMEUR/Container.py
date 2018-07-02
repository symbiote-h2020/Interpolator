'''
Created on 13.09.2017

@author: DuennebeilG

This module contains container classes.
'''


import SMEUR.Utils as Utils
import math


class ReducedStreetSegment(object):
    
    def __init__(self):
        self.centerLon=0.0
        self.centerLat=0.0
        self.comment=None
        
    def __repr__(self):
        result="ReducedStreetSegment: lon="
        result=result+str(self.centerLon)
        result=result+", lat="
        result=result+str(self.centerLat)
        result=result+", comment="
        if self.comment is None:
            result=result+"None"
        else:
            result=result+self.comment.encode("UTF-8")
        return result
    
    
    
class Location(object):
    def __init__(self):
        self.lat=0.0
        self.lon=0.0

    def __repr__(self):
        result="Location(latitude="+str(self.lat)+", lon="+str(self.lon)+")"
        return result

    def __eq__(self, other):
        if self  is other:
            return True
        
        if other is None:
            return False
    
        if not isinstance(other, Location):
            return False
        
        if math.fabs(self.lat-other.lat)>0.000001:
            return False
        
        if math.fabs(self.lon-other.lon)>0.000001:
            return False
        
        return True
        

    def __hash__(self):
        return hash((self.lon, self.lat))


    
    
        
class Property(object):
    def __init(self):
        self.name=None
        self.iri=None
        self.description=None



    def __repr__(self):
        result="Property("
        result+="name="+self.name+","
        result+="iri="+self.iri+","
        result+="desc="+str(self.description)
        result+=")"
        return result

    def __eq__(self, other):
        if self  is other:
            return True
        
        if other is None:
            return False
    
        if not isinstance(other, Property):
            return False
        
        if self.label!=other.label:
            return False
        
        if self.comment!=other.comment:
            return False
        
        return True
        

    def __hash__(self):
        return hash((self.label, self.comment))
    


        
        
class UnitOfMeasurement(object):
    def __init__(self):
        self.symbol=None
        self.name=None
        self.description=None

    def __repr__(self):
        result="uom("
        result+="symbol="+self.symbol+","
        result+="name="+self.name if not self.name is None else "None" +","
        result+"description"+str(self.description)
        result+=")"
        return result


class ObservationValue(object):
    def __init__(self):
        self.value=0.0
        self.obsProperty=None
        self.uom=None

    def __repr__(self):
        result="ObsValue("

        result+="value="+str(self.value)+","
        result+="ObsProp="+str(self.obsProperty)+","
        result+="uom="+str(self.uom)

        result+=")"
        return result


class Observation(object):
    def __init__(self):
        self.resourceId=None
        self.location=None
        self.resultTime=None
        self.samplingTime=None
        self.obsValues=None

    def __repr__(self):
        result="Observation(location="+str(self.location)+" time="+str(self.resultTime)+" values="+str(self.obsValues)+")"
        return result



def object_hook_segments(theDict):
    if 'centerLon' in theDict:  # It's a ReducedStreetSegment
        result=ReducedStreetSegment()
        result.centerLon=theDict["centerLon"]
        result.centerLat=theDict["centerLat"]
        result.comment=theDict["comment"]
        return result

    return theDict


def object_hook_obs(theDict):
    if 'latitude' in theDict:  # It's a Location
        result=Location()
        result.lon=theDict["longitude"]
        result.lat=theDict["latitude"]
        return result

    if 'symbol' in theDict and 'name' in theDict and 'description' in theDict: # UoM
        result=UnitOfMeasurement()
        result.symbol=theDict["symbol"]
        result.name=theDict["name"]
        result.description=theDict["description"]
        return result


    if 'name' in theDict and 'description' in theDict: # Property
        result=Property()
        result.name=theDict["name"]
        result.iri=theDict["iri"]
        result.description=theDict["description"]
        return result

    if 'value' in theDict and 'obsProperty' in theDict and 'uom' in theDict: # Obervation
        result=ObservationValue()
        result.value=float(theDict["value"])
        result.obsProperty=theDict["obsProperty"]
        result.uom=theDict["uom"]
        return result

    if 'resourceId' in theDict and 'location' in theDict and 'resultTime' in theDict and 'samplingTime' in theDict and 'obsValues' in theDict:
        result=Observation()
        result.resourceId=theDict['resourceId']
        result.location=theDict['location']
        result.resultTime=Utils.parseDT(theDict['resultTime'])
        result.samplingTime=theDict['samplingTime']
        result.obsValues=theDict['obsValues']
        return result

    return theDict






