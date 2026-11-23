
TOP = ../..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS = 

PYTHON_SOURCES = \
	glcontrolswidget.py \
	glwidget_container.py \
	glwidget.py

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
