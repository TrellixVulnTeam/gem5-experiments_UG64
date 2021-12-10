#ifndef __TUTORIAL_ASPLOS_TEST_HH__
#define __TURORIAL_ASPLOS_TEST_HH__

#include "params/Test.hh"
#include "sim/sim_object.hh"
#include <string>

//using namespace gem5;
namespace gem5
{
class Test : public SimObject
{
	public:
			Test(const TestParams &p);
};
} //namespace
#endif
