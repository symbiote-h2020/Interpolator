'''
Created on 13.09.2017

@author: DuennebeilG
'''

import sys
import os

import json

import math

from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
import numpy as np


import SMEUR.Container
import SMEUR.Utils



def dumpObs(obs):

    f=open("ReducedObservations.dat", "w")

    for obsProp in  obs:
        propData=obs[obsProp]
        for obsValue in propData:
            location=obsValue[0]
            lat=location.lat
            lon=location.lon
            value=obsValue[1]
            resultTime=obsValue[3]
            f.write(obsProp+","+str(lat)+","+str(lon)+","+str(value)+","+str(resultTime)+"\n")

    f.close()


def extractObsValuesByProperty(obs):
    '''
    We expect a list of Observations here were each Observation can potentially hold several ObservationValues.
    For the interpolation we can only use observationValues with identical Properties.
    Thus we reorganize the list here
    '''

    result=dict()   # The result will be a dict { Property --> [(Location, ObservationValue, uom.label)] }

    for observation in obs:
        location=observation.location
        resultTime=observation.resultTime

        for obsValue in observation.obsValues:
            prop=obsValue.obsProperty.iri
            if not prop in result:
                result[prop]=[]

            pair=(location, obsValue.value, obsValue.uom.symbol, resultTime)
            result[prop].append(pair)

    return result



def prepareKriging(lon, lat, value):

    print ("Kriging: Entry data:")
    print(lon)
    print(lat)
    print(value)

#    OK = OrdinaryKriging(lon, lat, value, 
    OK = UniversalKriging(lon, lat, value, 
                     variogram_model='linear',
#                     variogram_model='gaussian',
#                     variogram_model='spherical',
#                     drift_terms=('regional_linear'),
                     variogram_parameters=[1.0, 0.5],
                     verbose=True, 
                     enable_plotting=False)

    return OK


def doKriging(OK, lon, lat):
    print ("Kriging: interpolation points:")
    print(lon[:20])
    print(lat[:20])

    z, ss = OK.execute('points', lon, lat)
#    print(ss[::100])
    return z


def check_infs_nans(a):
    print("Checking an array for infs and nans")
    print("Length is "+str(len(a)))
    for i in range(0, len(a)):
        f =a[i]
        if math.isnan(f):
            print(i, f)
        if math.isinf(f):
            print(i, f)



def dumpInterpolated(property, latPoints, lonPoints, values):
    f=open("interpolated.dat", "a")
    for i in range(len(latPoints)):
        lat=latPoints[i]
        lon=lonPoints[i]
        v=values[i]
        f.write(property+","+str(lat)+","+str(lon)+","+str(v)+"\n")
    f.close()




def doInterpolationForOneProperty(property, observations, ssl):
    print("Interpolating on property "+property)
    # Prepare data for the kriging, i.e. make it three separate lists lon, lat ,value
    
    lon=[]
    lat=[]
    value=[]
    uom=None
    
    for pair in observations:
        location=pair[0]
        if location is None:
            raise ValueError("Location is None in "+str(pair))
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

    print("Doing an interpolation on "+str(len(idPoints))+" street segments")

#    try:
    interpolated=doKriging(krigingObject, lonPoints, latPoints)
#    except ValueError as ve:
#        check_infs_nans(lonPoints)
#        check_infs_nans(latPoints)
#        print(lonPoints)
#        print(latPoints)
#        raise ve

    print("A sample from the interpolated values:"+str(interpolated[::1000]))

    if len(interpolated)!=len(idPoints):
        raise ValueError("length of interpolated values differs from length of street segments")

    dumpInterpolated(property, latPoints, lonPoints, interpolated)

    result=dict()
    for i in range(0, len(idPoints)):
        segmentID=idPoints[i]
        v=interpolated[i]
        result[segmentID]=(v, uom)
        
    return result
        
    

def doInterpolationForAllPoperties(valuesByProperty, ssl):
    allInterpolations=dict()
    for prop, observations in valuesByProperty.items():
        interpolated=doInterpolationForOneProperty(prop, observations, ssl)
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



def removeOlderObservations(observations):
    locations=set()
    
    # Step 1, gather all locations
    for obs in observations:
        location=obs[0]
        locations.add(location)
    
    
    result=list()
    
    for location in locations:
        obsForLocation=[ o for o in observations if o[0]==location]
        sortedObs=sorted(obsForLocation, key=lambda obs: obs[3])
        bestObs=sortedObs[-1]
        result.append(bestObs)
    
    return result




if __name__ == '__main__':
    print("interpolator starting")

    print("Currently working in "+os.getcwd())

    sslFileName=sys.argv[1]
    obsFileName=sys.argv[2]
    outFileName=sys.argv[3]

    print("reading file "+ sslFileName+" as StreetSegmentList")
    fSSL = open(sslFileName, 'r', encoding='utf-8')
    ssl=json.load(fSSL, cls=None, object_hook=SMEUR.Container.object_hook_segments, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
#    print(ssl)
    fSSL.close()


    print("reading file "+ obsFileName+" as Observation list")
    fOBS = open(obsFileName, 'r', encoding='utf-8')
    obs=json.load(fOBS, cls=None, object_hook=SMEUR.Container.object_hook_obs, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
    fOBS.close()


#    print("Removing older values");
#    print("length of obs before is "+str(len(obs)))
#    obs=SMEUR.Utils.removeOldObservations(obs)
#    print("length of obs after is "+str(len(obs)))

    print("Re-arranging the observations from sensor centric to property centric")
    obsByProperty=extractObsValuesByProperty(obs)

    obsByPropertyReduced=dict()
    for prop in obsByProperty:
        allObs=obsByProperty[prop]
        reducedObs=removeOlderObservations(allObs)
        obsByPropertyReduced[prop]=reducedObs
        
    obsByProperty=obsByPropertyReduced


    dumpObs(obsByProperty)
#    print(obsByProperty)

    allInterpolations=doInterpolationForAllPoperties(obsByProperty, ssl)

    # Note, the above structure returned from the interpolation is still sorted by properties first and then by segments.
    # We still need to reorganize this to have segments as the primary ordering.  

    interpolOrderedBySegments=orderBySegments(allInterpolations)

    outputString=json.dumps(interpolOrderedBySegments, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=4, separators=None, default=None, sort_keys=False)

    fOut = open(outFileName, 'w')
    fOut.write(outputString)
    fOut.close()
    
    print("Done")

