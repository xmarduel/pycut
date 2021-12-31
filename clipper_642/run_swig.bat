C:\Users\xavie\Downloads\swigwin-4.0.2\swig.exe -c++ -python clipper_642.i

g++ -O2 -fPIC -c clipper.cpp
g++ -O2 -fPIC -c clipper_642_wrap.cxx -IC:\\Users\\xavie\\AppData\\Local\\Programs\\Python\\Python39\\include
g++ -shared -fPIC clipper.o clipper_642_wrap.o -LC:\Users\xavie\AppData\Local\Programs\Python\Python39 -lpython39 -o _clipper_642.pyd


REM Python39: copy all *.dll of C:\msys64\mingw64\bin  in this folder!
