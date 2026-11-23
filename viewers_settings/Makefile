
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS = 

PYTHON_SOURCES = colorpicker.py
PYTHON_UIS = viewers_settings.ui

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)
PYTHON_UICFILES = $(PYTHON_UIS:%.ui=%_ui.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UICFILES)
uic:: $(PYTHON_UICFILES)

include $(MKINC)/mk.rules
