'''
Created on 6 Aug 2011

@author: geert
'''
import unittest
from meteorpy import common

class Test(unittest.TestCase):


    def testZenithAttraction(self):
        print common.zenith_attaction(53, 20)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testZenithAttraction']
    unittest.main()