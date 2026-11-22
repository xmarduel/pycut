
TOP = ../..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS =

PYTHON_SOURCES = \
	arcproperties.py \
	gcodeparser.py \
	gcodepreprocessorutils.py \
	gcodeviewparse.py \
	linesegment.py \
	pointsegment.py

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
