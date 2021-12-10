#Simple config file for gem5 simulation

#Importing m5 library and all compiled SimObjects 

import m5

from m5.objects import*

#adds common scripts to our path
m5.util.addToPath('../')


from caches import*

#import the SimpleOpts module
from common import SimpleOpts

#get ISA for the default binary to run, for testing
isa = str(m5.defines.buildEnv['TARGET_ISA']).lower()
#isa = 'X86'

#default to running hello
#grap the specific path to the binary
#thispath = os.path.dirname(os.path.realpath(__file__))
thispath = '/home/vagrant/software/gem5/config/tutorial' 
#default_binary = os.path.join(thispath, '../../', 'tests/test-progs/hello/bin/', isa, 'linux/hello')
default_binary = '../../tests/tests-progs/hello/bin/x86/linux/hello'
#binary to execute
SimpleOpts.add_option("binary", nargs='?', default=default_binary)

#finalize the arguments and grab the args for our objects
args = SimpleOpts.parse_args()

#First SimObj is the system
#It is parent to all other Obj in the simulated system
#It contains a lot of functional infos like physical mem ranges, root clk domain, root voltage domain kernel, etc
#Instanciated like a simple python class
system = System()

#Clk domain
#First create it, then set the clock frequency on that domain
#Setting parameters on a sim object is the same as setting members of an object in python
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

#Memory system
#We will use as in most cases the timing mode for the mem sim
#We set up a single memory range of 512 MB
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

#CPU
#Most simple timing-based CPU in gem5 TimingSimpleCPU
#This model executes each instructions in a single clock cycle except mem req
system.cpu = TimingSimpleCPU()

#Creating the caches
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)

#Connect the caches to the cpu with the helper functions
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

#Creating a bus to connect the L2 to the L1 with the helper functions
system.l2bus = L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

#Now creating the L2 cache and connecting it to the L2 bus and the main memory bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2Bus)
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)

#We need to connect more ports
#We need and IO controller 
#Connecting PIO and interrupt ports to the memory bus is an x86 specific requirement other ISAs like ARM do not need the 3 extra lines
system.cpu.createInterruptController()
if m5.defines.buildEnv['TARGET_ISA'] == "X86":
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

#connects the system to the membus
system.system_port = system.membus.cpu_side_ports

#We need to create a memory controller and connect it to the membus
#DDR3 controller responsible for the entire memory range of our system
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports 

#We need to create the process another SimObj
#Then we can set the process command to the command we want to run
#We then set the CPU to use the process as it's workload
binary = 'tests/test-progs/hello/bin/x86/linux/hello'

#For gem5 v21 and beyond, uncomment the following line
system.workload = SEWorkload.init_compatible(args.binary)

process = Process()
process.cmd = [args.binary]
system.cpu.workload = process
system.cpu.createThreads()

#The final step is to instanciate the system and begin execution
#We create the root object then we instantiate the simulation
#The instantiation process goes through all SimObj and create the C++ equivalent
root = Root(full_system = False, system = system)
m5.instantiate()

#Finally we can run the simulation
print('Beggining simulation')
exit_event = m5.simulate()


#Inspecting the state of the system
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
