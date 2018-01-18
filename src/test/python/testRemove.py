import unittest
import os

import json


import SMEUR.Container
import SMEUR.Utils

class TestOBS( unittest.TestCase ):
    def setUp( self ):
        pass
        
    def testRemoveOld( self ):
        
        print(os.getcwd())
        
        obsFileName="../../../OBS.json"
        print("reading file "+ obsFileName+" as Observation list")
        
        fOBS = open(obsFileName, 'r')
        obs=json.load(fOBS, cls=None, object_hook=SMEUR.Container.object_hook_obs, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
        print(obs)
        fOBS.close()

        print("Removing older values");
        obs=SMEUR.Utils.removeOldObservations(obs)


        
if __name__ == "__main__":
    unittest.main()