'''
Created on 1 Aug 2011

@author: geert
'''
import unittest
from meteorpy import flux

class TestFlux(unittest.TestCase):

    def testData(self):
        fd = flux.FluxData("2011-07-20 00:00:00", "2011-07-20 00:10:00", "PER")
        data = fd.getData()
        assert( len(data) > 0 )
    
    def testGraph(self):
        graph = flux.FluxGraph("2011-07-20 00:00:00", "2011-07-22 00:00:00", "PER")
        graph.saveHTML()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.dataTest', 'Test.graphTest']
    unittest.main()