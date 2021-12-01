C:\Users\xavie\Downloads\swigwin-4.0.2\swig.exe -c++ -python cam.i

g++ -O2 -fPIC -c cam_wrap.cxx -IC:\\Users\\xavie\\AppData\\Local\\Programs\\Python\\Python39\\include
g++ -O2 -fPIC -c cam.cpp
g++ -O2 -fPIC -c hspocket.cpp 
g++ -O2 -fPIC -c vEngrave.cpp 
g++ -O2 -fPIC -c separateTabs.cpp  
g++ -shared -fPIC cam_wrap.o cam.o hspocket.o vEngrave.o separateTabs.o -LC:\Users\xavie\AppData\Local\Programs\Python\Python39 -lpython39 -o _cam.pyd


REM Python39: copy all *.dll of C:\msys64\mingw64\bin  in this folder!

REM >>> import os
REM >>> import cam