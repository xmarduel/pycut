
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS = 

PYTHON_SOURCES = colorpicker.py
PYSIDE_UIS = viewers_settings.ui

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)
PYTHON_UIS = $(PYSIDE_UIS:%.ui=%_ui.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UIS)

include $(MKINC)/mk.rules
