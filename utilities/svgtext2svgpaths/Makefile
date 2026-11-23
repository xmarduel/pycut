
TOP = ../..
MKINC = $(TOP)/make

export WITH_FLAKES=YES
export WITH_MYPY=YES
export WITH_RUFF=YES

include $(MKINC)/mk.defaults

SUBDIRS =

PYTHON_SOURCES = svgtext2svgpath.py \
	svgtext2svgpaths_fonts_specs.py
PYTHON_UIS = 
PYTHON_RCCS = 

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc) 
PYTHON_UICFILES = $(PYTHON_UIS:%.ui=%_ui.py)
PYTHON_RCCFILES = $(PYTHON_RCCS:%.qrc=%_rc.py)


all:: $(PYTHON_LIBFILES) $(PYTHON_UICFILES) $(PYTHON_RCCFILES)
uic:: $(PYTHON_UICFILES)
rcc:: $(PYTHON_RCCFILES)

include $(MKINC)/mk.rules
