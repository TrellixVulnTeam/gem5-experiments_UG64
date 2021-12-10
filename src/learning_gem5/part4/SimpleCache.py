# SimpleCache parameter declaration

from m5.params import *
from m5.proxy import *
from MemObject import MemObject

class SimpleCache(MemObject):
    type = 'SimpleCache'
    cxx_header = "learning_gem5/part4/simple_cache.hh"
    
    # Vector ports behave similarly to regular ports, they are resolved by
    # getMasterPort and getSlavePort.
    # They allow this object to connect to multiple peers.
    cpu_side = VectorSlavePort("CPU side port, receives requests")
    mem_side = MasterPort("Memory side port, sends requests")

    # Two new parameters, the latency for access/miss and the size of the cache.
    latency = Param.Cycles(1, "Cycles taken on a hit or to resolve a miss")
    size = Param.MemorySize('16kB', "The size of the cache")
    
    # This system parameter is a pointer to the main system this ache is 
    # connected to.
    # This is needed to get the cache block size from the system object.
    #
    # Parent.any is a proxy parameter
    system = Param.System(Parent.any, "The system this cache is part of")
