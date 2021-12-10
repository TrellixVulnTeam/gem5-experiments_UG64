/*
 * Copyright (c) 2017 Jason Lowe-Power
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "learning_gem5/part2/simple_cache.hh"

#include "base/trace.hh"
#include "debug/SimpleCache.hh"

namespace gem5
{

/**
 * In this constructor declaration we use the cacheLineSize from the 
 * system parameter to set the blockSize, and then the blockSize to
 * set the total cache capacity.
 */
		
SimpleCache::SimpleCache(const SimpleCacheParams &params) :
    MemObject(params),
	latency(params->latency),
	blockSize(params->system->cacheLineSize()),
	capacity(params->size / blockSize),
    memPort(params->name + ".mem_side", this),
    blocked(false), outstandingPacket(nullptr), waitingPortId(-1)
{
	/**
	 * We need to create a number of CPUSidePorts based on the number
	 * of connections to this objects.
	 *
	 * Since the cpu_side port was declared as a VectorSlavePort in
	 * the SimObject.py, the parameter automatically has a variable
	 * port_cpu_side_connection_count.
	 */
	for (int i = 0; i < params->port_cpu_side_connection_count; i++)
	{
		cpuPorts.emplace_back(name() + csprintf(".cpu_side[%d]",i), i, this);
	}
}

/**
 *
 * Implementing getMasterPort and getSlavePort.
 * getMasterPort is exactly the same as the SimpleMemobj.
 * For getSlavePort we need to return the port based on the id requested.
 *
 */

Port &
SimpleCache::getMasterPort(const std::string &if_name, PortID idx)
{
    panic_if(idx != InvalidPortID, "This object doesn't support vector ports");

    // This is the name from the Python SimObject declaration (SimpleMemobj.py)
    if (if_name == "mem_side") 
	{
        return memPort;
    } 
	else if (if_name == "inst_port") 
	{
        return instPort;
    } 
	else if (if_name == "data_port") 
	{
        return dataPort;
    } 
	else 
	{
        // pass it along to our super class
        return SimObject::getPort(if_name, idx);
    }
}

BaseSlavePort& 
SimpleCache::getSlavePort(const std::string& if_name, PortID idx)
{
	if (if_name == "cpu_side" && idx < cpuPorts.size())
	{
		return cpuPorts[idx];
	}
	else 
	{
		return MemObject::getSlavePort(if_name, idx);
	}
}

void
SimpleMemobj::CPUSidePort::sendPacket(PacketPtr pkt)
{
    // Note: This flow control is very simple since the memobj is blocking.

    panic_if(blockedPacket != nullptr, "Should never try to send if blocked!");

    // If we can't send the packet across the port, store it for later.
    if (!sendTimingResp(pkt)) {
        blockedPacket = pkt;
    }
}

AddrRangeList
SimpleMemobj::CPUSidePort::getAddrRanges() const
{
    return owner->getAddrRanges();
}

void
SimpleMemobj::CPUSidePort::trySendRetry()
{
    if (needRetry && blockedPacket == nullptr) {
        // Only send a retry if the port is now completely free
        needRetry = false;
        DPRINTF(SimpleMemobj, "Sending retry req for %d\n", id);
        sendRetryReq();
    }
}

void
SimpleMemobj::CPUSidePort::recvFunctional(PacketPtr pkt)
{
    // Just forward to the memobj.
    return owner->handleFunctional(pkt);
}

bool
SimpleMemobj::CPUSidePort::recvTimingReq(PacketPtr pkt)
{
    // Just forward to the memobj.
    if (!owner->handleRequest(pkt)) {
        needRetry = true;
        return false;
    } else {
        return true;
    }
}

void
SimpleMemobj::CPUSidePort::recvRespRetry()
{
    // We should have a blocked packet if this function is called.
    assert(blockedPacket != nullptr);

    // Grab the blocked packet.
    PacketPtr pkt = blockedPacket;
    blockedPacket = nullptr;

    // Try to resend it. It's possible that it fails again.
    sendPacket(pkt);
}

void
SimpleMemobj::MemSidePort::sendPacket(PacketPtr pkt)
{
    // Note: This flow control is very simple since the memobj is blocking.

    panic_if(blockedPacket != nullptr, "Should never try to send if blocked!");

    // If we can't send the packet across the port, store it for later.
    if (!sendTimingReq(pkt)) {
        blockedPacket = pkt;
    }
}

bool
SimpleMemobj::MemSidePort::recvTimingResp(PacketPtr pkt)
{
    // Just forward to the memobj.
    return owner->handleResponse(pkt);
}

void
SimpleMemobj::MemSidePort::recvReqRetry()
{
    // We should have a blocked packet if this function is called.
    assert(blockedPacket != nullptr);

    // Grab the blocked packet.
    PacketPtr pkt = blockedPacket;
    blockedPacket = nullptr;

    // Try to resend it. It's possible that it fails again.
    sendPacket(pkt);
}

void
SimpleMemobj::MemSidePort::recvRangeChange()
{
    owner->sendRangeChange();
}

/**
 * It takes time to access the cache, therefore the latency to access
 * the cache tags needs to be taken into acount.
 * An extra parameter has been added for this, and in handlerequest
 * an event to stall the request for the needed amount of time is 
 * now used.
 */


bool
SimpleCache::handleRequest(PacketPtr pkt, int port_id)
{
    if (blocked) {
        // There is currently an outstanding request. Stall.
        return false;
    }

    DPRINTF(SimpleMemobj, "Got request for addr %#x\n", pkt->getAddr());

    // This memobj is now blocked waiting for the response to this packet.
    blocked = true;

	waitingPortId = port_id;

	schedule(new AccessEvent(this, pkt), clockEdge(latency));

    return true;
}

bool
SimpleMemobj::handleResponse(PacketPtr pkt)
{
    assert(blocked);
    DPRINTF(SimpleMemobj, "Got response for addr %#x\n", pkt->getAddr());

    // The packet is now done. We're about to put it in the port, no need for
    // this object to continue to stall.
    // We need to free the resource before sending the packet in case the CPU
    // tries to send another request immediately (e.g., in the same callchain).
    blocked = false;

    // Simply forward to the memory port
    if (pkt->req->isInstFetch()) {
        instPort.sendPacket(pkt);
    } else {
        dataPort.sendPacket(pkt);
    }

    // For each of the cpu ports, if it needs to send a retry, it should do it
    // now since this memory object may be unblocked now.
    instPort.trySendRetry();
    dataPort.trySendRetry();

    return true;
}

void
SimpleMemobj::handleFunctional(PacketPtr pkt)
{
    // Just pass this on to the memory side to handle for now.
    memPort.sendFunctional(pkt);
}

AddrRangeList
SimpleMemobj::getAddrRanges() const
{
    DPRINTF(SimpleMemobj, "Sending new ranges\n");
    // Just use the same ranges as whatever is on the memory side.
    return memPort.getAddrRanges();
}

void
SimpleMemobj::sendRangeChange()
{
    instPort.sendRangeChange();
    dataPort.sendRangeChange();
}

void SimpleCache::accessTiming(PacketPtr pkt)
{	
	/**
	 * accessFunctional performs the functonal access of the cache
	 * and either reads of writes the cache on a hit or returns 
	 * that the access was a miss.
	 */
	bool hit = accessFunctional(pkt);

	// The access is a hit, we need to respond to the packet.
	if (hit)
	{
		pkt->makeResponse();
		sendResponse(pkt);
	}
	else
	{
		Addr addr = pkt->getAddr();
        Addr block_addr = pkt->getBlockAddr(blockSize);
        unsigned size = pkt->getSize();
        
		if (addr == block_addr && size == blockSize) 
		{
            DPRINTF(SimpleCache, "forwarding packet\n");
            memPort.sendPacket(pkt);
        } 
		else 
		{
            DPRINTF(SimpleCache, "Upgrading packet to block size\n");
            panic_if(addr - block_addr + size > blockSize,
                     "Cannot handle accesses that span multiple cache lines");

            assert(pkt->needsResponse());
            MemCmd cmd;

            if (pkt->isWrite() || pkt->isRead()) 
			{
                cmd = MemCmd::ReadReq;
            } 
			else 
			{
                panic("Unknown packet type in upgrade size");
            }

            PacketPtr new_pkt = new Packet(pkt->req, cmd, blockSize);
            new_pkt->allocate();

            outstandingPacket = pkt;

            memPort.sendPacket(new_pkt);
		}
	}
}

void SimpleCache::sendResponse(PacketPtr pkt)
{
	int port = waitingPortId;

	blocked = false;
	waitingPortId = -1;

	cpuPorts[port].sendPacket(pkt);
	for(auto& port : cpuPorts)
	{
		port.trySendRetry();
	}
}

class AccessEvent : public Event
{
	private:
		SimpleCache *cache;
		PacketPtr pkt;
	public:
		AccessEvent(SimpleCache *cache, PacketPtr pkt) :
			Event(Default_Pri, AutoDelete), cache(cache), pkt(pkt)
		{
		}

		void process() override 
		{
			cache->accessTiming(pkt)
		}
};

} // namespace gem5
























