target =  qtracker
deps = ui/qtracker.qrc ui/qtracker.ui

all: $(target)

$(target): $(deps)
	pyuic4 ui/qtracker.ui > ui/qtracker.py
	pyuic4 ui/project.ui > ui/project.py
	pyrcc4 ui/qtracker.qrc > ui/qtracker_rc.py


.PHONY: clean

clean:
	rm -f ui/qtracker.py ui/qtracker_rc.py ui/project.py ui/*pyc *pyc
