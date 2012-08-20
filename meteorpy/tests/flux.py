'''
Created on 1 Aug 2011

@author: geert
'''
import unittest
from meteorpy import flux

class TestFlux(unittest.TestCase):

    def testData(self):
        fd = flux.FluxData("PER", "2011-07-20 00:00:00", "2011-07-20 00:10:00")
        data = fd.getData()
        assert( len(data) > 0 )
    
    def testGraph(self):
        graph = flux.FluxGraph("PER", "2011-07-20 00:00:00", "2011-07-22 00:00:00")
        graph.saveHTML()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.dataTest', 'Test.graphTest']
    unittest.main()