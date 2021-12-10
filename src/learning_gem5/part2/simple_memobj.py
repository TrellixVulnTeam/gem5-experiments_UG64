# This file creates a basic system and executes the simple
# hello world application. 
#
# It uses the SimpleMemobj between the CPU and membus. 

# import gem5 library and all the SimObjects
import m5
from m5.objects import*

# create the simulated system
system = System()

# set clock frequency for the system and its childrens
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# system setup
system.mem_mode = 'timing'                  # memory timing accesses
system.mem_ranges = [AddrRange('512MB')]    # create an address range

# create a simple CPU
system.cpu = TimingSimpleCPU()

# create the simple memory object 
system.memobj = SimpleCache()
system.memobj.size = '16kB'

# routing CPU ports to cache
system.cpu.icache_port = system.memobj.cpu_side[0]
system.cpu.dcache_port = system.memobj.cpu_side[1]

# create a mem bus (coherent Xbar)
system.membus = SystemXBar()

# connect the memObj 
system.memobj.mem_side = system.membus.slave

# create interrupt controller for the CPU and the membus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_master = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_slave = system.membus.mem_side_ports

# create controller for DDR3 and membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# system and membus routing
system.system_port = system.membus.cpu_side_ports

# create the simple hello world process
process = Process()

# sets the command and path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
binpath = os.path.join(thispath, '../../..', '/home/vagrant/software/gem5/benchmarks/STREAM-master/stream_f.exe')

# cmd is a list beggining with the executable
process.cmd = [binpath]

# sets the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(binpath)

# set up the SimObject, start the simulation and instantiate all of the objects
# created above

root = Root(full_system = False, system = system)
m5.instantiate()

print('Beggining simulation...')
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))


