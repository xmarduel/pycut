
REM in RESOURCES

REM generate qt resources
pyside6-rcc.exe -o ..\resources_rc.py resources.qrc
pyside6-rcc.exe -o ..\resources_doc_rc.py resources-doc.qrc
