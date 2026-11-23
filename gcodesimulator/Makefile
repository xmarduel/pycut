
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS = parser parser_11_2 util

PYTHON_SOURCES = \
	gcode_syntaxhighlighter.py \
	gcodefileviewer.py \
	gcodeminiparser.py \
	gcodesimulator_driver.py \
	glviewer.py

PYTHON_UIS = simcontrols.ui

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc) 
PYTHON_UICFILES = $(PYTHON_UIS:%.ui=%_ui.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UICFILES)

include $(MKINC)/mk.rules
