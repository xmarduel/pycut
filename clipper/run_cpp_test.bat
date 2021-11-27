
g++ -O2 -fPIC -c clipper.cpp
g++ -O2 -fPIC -c clipper_test.cpp

g++  clipper.o clipper_test.o  -o clipper_test.exe

