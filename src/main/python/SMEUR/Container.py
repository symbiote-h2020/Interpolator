'''
Created on 13.09.2017

@author: DuennebeilG

This module contains container classes.
'''

class ReducedStreetSegment(object):
    
    def __init__(self):
        self.centerLon=0.0
        self.centerLat=0.0
        self.comment=None
        
    def __repr__(self):
        result="ReducedStreetSegment: lon="+str(self.centerLon)+", lat="+str(self.centerLat)+", comment="+self.comment
        return result
    
    
    
class Location(object):
    def __init__(self):
        self.lat=0.0
        self.lon=0.0
    
    
        
class Property(object):
    def __init(self):
        self.label=None
        self.comment=None
        
        
class UnitOfMeasurement(object):
    def __init__(self):
        self.symbol=None
        self.label=None
        self.comment=None
        

class ObservationValue(object):
    def __init__(self):
        self.value=0.0
        self.obsProperty=None
        self.uom=None


class Observation(object):
    def __init__(self):
        self.resourceId=None
        self.location=None
        self.resultTime=None
        self.samplingTime=None
        self.obsValues=None
