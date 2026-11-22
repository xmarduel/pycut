
TOP = ../..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS =

PYTHON_SOURCES = \
	gcodedrawer.py \
	origindrawer.py \
	selectiondrawer.py \
	shaderdrawable.py \
	tooldrawer.py

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
