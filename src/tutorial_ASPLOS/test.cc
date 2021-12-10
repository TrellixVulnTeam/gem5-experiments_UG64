#include "tutorial_ASPLOS/test.hh"
#include "debug/TestFlag.hh"
#include "base/trace.hh"

namespace gem5
{
Test::Test(const TestParams &params) : SimObject(params)
{
	//std::cout << "Hello World! From a SimObject!" << std::endl;
	DPRINTF(TestFlag, "Created the Test SimObject\n");
}

/*
Test* 
TestParams::create() const
{
	return new Test(this);
	// allocating memory and instantiating new object
}*/

}
