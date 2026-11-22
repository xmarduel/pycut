
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS = drawers parser tables util widgets

PYTHON_SOURCES = 

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
