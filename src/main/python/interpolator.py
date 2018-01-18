'''
Created on 13.09.2017

@author: DuennebeilG
'''

import sys
import os

import json

from pykrige.ok import OrdinaryKriging
import numpy as np
        

import SMEUR.Container
import SMEUR.Utils

def extractObsValuesByProperty(obs):
    '''
    We expect a list of Observations here were each Observation can potentially hold several ObservationValues.
    For the interpolation we can only use observationValues with identical Properties.
    Thus we reorganize the list here
    '''
    
    result=dict()   # The result will be a dict symbol --> [(Location, ObservationValue, uom.label)]
    
    for observation in obs:
        location=observation.location
        
        for obsValue in observation.obsValues:
            prop=obsValue.obsProperty.name
            if not prop in result:
                result[prop]=[]
            
            pair=(location, obsValue.value, obsValue.uom.symbol)
            result[prop].append(pair)
            
    return result



def prepareKriging(lon, lat, value):
    OK = OrdinaryKriging(lon, lat, value, variogram_model='linear',
                     verbose=True, enable_plotting=False, enable_statistics=False)

    return OK


def doKriging(OK, lon, lat):
    z, ss = OK.execute('points', lon, lat)
#    print(z)
#    print(ss)
    return z

def doInterpolationForOneProperty(observations, ssl):
    # Prepare data for the kriging, i.e. make it three separate lists lon, lat ,value
    
    lon=[]
    lat=[]
    value=[]
    uom=None
    
    for pair in observations:
        location=pair[0]
        v=float(pair[1])
        lon.append(location.lon)
        lat.append(location.lat)
        value.append(v)
        if uom is None:
            uom=pair[2]
        
    alon=np.array(lon)
    alat=np.array(lat)
    aval=np.array(value)
    
    krigingObject=prepareKriging(alon, alat, aval)

    idPoints=[]
    lonPoints=[]
    latPoints=[]
    
    for segmentID,ss in ssl.items():
        idPoints.append(segmentID)
        lonPoints.append(ss.centerLon)
        latPoints.append(ss.centerLat)


    interpolated=doKriging(krigingObject, lonPoints, latPoints)

    if len(interpolated)!=len(idPoints):
        raise ValueError("length of interpolated values differs from length of street segments")

    result=dict()
    for i in range(0, len(idPoints)):
        segmentID=idPoints[i]
        v=interpolated[i]
        result[segmentID]=(v, uom)
        
    return result
        
    

def doInterpolationForAllPoperties(valuesByProperty, ssl):
    allInterpolations=dict()
    for prop, observations in valuesByProperty.items():
        interpolated=doInterpolationForOneProperty(observations, ssl)
        allInterpolations[prop]=interpolated
        
    return allInterpolations

        
def orderBySegments(interpolatedByProperty):
    orderedBySegment=dict()
    
    for prop, segmentValues in interpolatedByProperty.items():
        for segID, value in segmentValues.items():
            if not segID in orderedBySegment:
                orderedBySegment[segID]=dict()
            
            segmentStore=orderedBySegment[segID]
            segmentStore[prop]=value
     
    return orderedBySegment   



if __name__ == '__main__':
    print("interpolator starting")
    
    print("Currently working in "+os.getcwd())
    
    sslFileName=sys.argv[1]
    obsFileName=sys.argv[2]
    outFileName=sys.argv[3]
    
    print("reading file "+ sslFileName+" as StreetSegmentList")
    fSSL = open(sslFileName, 'r')
    ssl=json.load(fSSL, cls=None, object_hook=SMEUR.Container.object_hook_segments, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
#    print(ssl)
    fSSL.close()

    
    print("reading file "+ obsFileName+" as Observation list")
    fOBS = open(obsFileName, 'r')
    obs=json.load(fOBS, cls=None, object_hook=SMEUR.Container.object_hook_obs, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
    print(obs)
    fOBS.close()


    print("Removing older values");
    obs=SMEUR.Utils.removeOldObservations(obs)

    print("Re-arranging the observations from sensor centric to property centric")
    obsByProperty=extractObsValuesByProperty(obs)
    print(obsByProperty)
    
    allInterpolations=doInterpolationForAllPoperties(obsByProperty, ssl)
    
    # Note, the above structure returned from the interpolation is still sorted by properties first and then by segments.
    # We still need to reorganize this to have segments as the primary ordering.  

    interpolOrderedBySegments=orderBySegments(allInterpolations)

    outputString=json.dumps(interpolOrderedBySegments, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=4, separators=None, default=None, sort_keys=False)

    fOut = open(outFileName, 'w')
    fOut.write(outputString)
    fOut.close()
    
    print("Done")