from m5.params import *
from m5.SimObject import SimObject

class Test(SimObject):

    type = 'Test'
    cxx_header = "tutorial_ASPLOS/test.hh"
    cxx_class = 'gem5::Test'    
