#Simple config file for gem5 simulation

#Importing m5 library and all compiled SimObjects 
import m5
from m5.objects import*
from caches import*

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

# lets add some caches
system.cpu.l1icache = L1ICache()
system.cpu.l1dcache = L1DCache()

# Connecting caches up to the cpu
system.cpu.l1icache.connectCPU(system.cpu)
system.cpu.l1dcache.connectCPU(system.cpu)

# Adding an L2 bus
system.l2bus = L2XBar()

# Connecting L1s to the L2 bus
system.cpu.l1icache.connectBus(system.l2bus)
system.cpu.l1dcache.connectBus(system.l2bus)

# Adding the L2 cache
system.l2cache = L2Cache()

system.l2cache.connectCPUSideBus(system.l2bus)

# System wide mem bus
system.membus = SystemXBar()

system.l2cache.connectMemSideBus(system.membus)

#We need to connect more ports
#We need and IO controller 
#Connecting PIO and interrupt ports to the memory bus is an x86 specific requirement other ISAs like ARM do not need the 3 extra lines
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

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
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
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
