import datetime as dt


def removeOldObservations(obs):
    bestvalues=dict()   # (Location) -> date

    # Pass 1, find largest date
    for observation in obs:
#        print("Dealing with an obs of "+str(observation))
        location=observation.location
        print("location for that is "+str(location))
        
        if location in bestvalues:
            largestDate=bestvalues[location]
            print("location is already known")
        else:
            largestDate=observation.resultTime
            print("location is new")
            
        if largestDate<observation.resultTime:
            largestDate=observation.resultTime
        
        bestvalues[location]=largestDate

    print("Best values are "+str(bestvalues))
    
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
    
    if result is not None:
        return result

    try:
       result=dt.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        pass

    if result is not None:
        return result
    

    result=dt.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%fZ')

    return result

