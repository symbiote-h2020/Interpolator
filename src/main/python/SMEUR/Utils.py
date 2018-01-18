import datetime as dt


def removeOldObservations(obs):
    bestvalues=dict()   # (Location) -> date

    # Pass 1, find largest date
    for observation in obs:
        location=observation.location
        
        if location in bestvalues:
            largestDate=bestvalues[location]
        else:
            largestDate=observation.resultTime
            
        if largestDate<observation.resultTime:
            largestDate=observation.resultTime
        
        bestvalues[location]=largestDate

    
    retVal=list()
    
    # Pass 2, remove everything but the largest
    for i in range(0, len(obs)):
        
        observation=obs[i]        
        location=observation.location
        
        largestDate=bestvalues[location]
        if largestDate==observation.resultTime:
            retVal.append(observation)
            
    return retVal
    

def parseDT(datestr):
    result=None
    try:
       result=dt.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        pass
    
    if result is None:
       result=dt.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    return result
