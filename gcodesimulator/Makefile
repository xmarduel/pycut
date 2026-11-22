
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS =

PYTHON_SOURCES = \
	gcode_syntaxhighlighter.py \
	gcodefileviewer.py \
	gcodeminiparser.py \
	gcodesimulator_driver.py \
	glviewer.py

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc) 

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
