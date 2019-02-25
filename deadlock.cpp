// lockGuardDeadlock.cpp

#include <iostream>
#include <chrono>
#include <mutex>
#include <thread>


int main() {
    std::mutex m1;
    std::mutex m2;
    std::thread t1([&m1, &m2] {
        std::cout<<"\n1. Acquiring m1.\n";
        m1.lock();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        std::cout<<"\n1. Acquiring m2\n";
        m2.lock(); 
    });
    std::thread t2([&m1, &m2] {
        std::cout<<"\n2. Acquiring m2\n";
        m2.lock();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        std::cout<<"\n2. Acquiring m1\n";
        m1.lock();
    });

    t1.join();
    t2.join();
	std::cout<<std::endl;
}