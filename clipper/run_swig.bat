C:\Users\xavie\Downloads\swigwin-4.0.2\swig.exe -c++ -python clipper.i

g++ -O2 -fPIC -c clipper.cpp
g++ -O2 -fPIC -c clipper_wrap.cxx -IC:\\Users\\xavie\\AppData\\Local\\Programs\\Python\\Python39\\include
g++ -shared -fPIC clipper.o clipper_wrap.o -LC:\Users\xavie\AppData\Local\Programs\Python\Python39 -lpython39 -o _clipper.pyd


REM Python39: copy all *.dll of C:\msys64\mingw64\bin  in this folder!

REM >>> import os
REM >>> import clipper