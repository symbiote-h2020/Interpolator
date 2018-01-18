import unittest
import os

import json


import SMEUR.Utils as Utils

class TestUtils( unittest.TestCase ):
    def setUp( self ):
        pass
        
    def testDateParsing( self ):

        Utils.parseDT("2018-01-17T14:30:22")
        Utils.parseDT("2018-01-17T14:30:22.123Z")
#        dt.datetime.strptime(theDict['resultTime'], '%Y-%m-%dT%H:%M:%S')
        
        
if __name__ == "__main__":
    unittest.main()