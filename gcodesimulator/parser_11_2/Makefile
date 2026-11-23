
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
	parser.py \
	pointsegment.py \
	splineproperties.py

PYTHON_UIS =

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc) 
PYTHON_UIS = $(PYSIDE_UIS:%.ui=%_ui.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UIS)

include $(MKINC)/mk.rules
