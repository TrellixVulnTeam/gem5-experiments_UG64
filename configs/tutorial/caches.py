#Caches configuration file

#We first import the simObj we are going to extend in this file
import m5
from m5.objects import Cache

#adding common scipts to our path
#m5.util.addToPath('../../')
#from common import SimpleOpts

#We can treat the BaseCache object like any python class and extend it
#We start by making the L1 cache
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    
    def connectCPU(self, cpu):
    	#This must be defined in a subclass
    	raise NotImplementedError
    def connectBus(self, bus):
    	self.mem_side = bus.cpu_side_ports

#Here we set values of DefaultCache that don't have default values
#All the possible parameters are in the source code of SimObj

#Sub classes of L1Cache; the L1DCache and L1ICache
class L1ICache(L1Cache):
    #sets default size
    size = '16kB'
    #SimpleOpts.add_option('--l1i_size', help="L1 instruction cache size. Default: %s" %size)
    
    def connectCPU(self, cpu):
        #connect this cache s port to a CPU icache port
        self.cpu_side = cpu.icache_port
class L1DCache(L1Cache):
    #sets default size
    size = '64kB'
    #SimpleOpts.add_option('--l1d_size', help="L1 data cache size. Default: %s" %size)
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port

#We also create and L2 with reasonable parameters
class L2Cache(Cache):
    size = '256kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    
    #SimpleOpts.add_option('--l2_size', help="L2 cache size. Default: %s" %size)

    def connectCPUSideBus(self, bus):
    	self.cpu_side = bus.mem_side_ports
    def connectMemSideBus(self, bus):
    	self.mem_side = bus.cpu_side_ports

        
#We add helper functions to connect the CPU to the cache and caches to a bus
