target =  qtime
deps = ui/qtime.qrc ui/qtime.ui

all: $(target)

$(target): $(deps)
	pyuic4 ui/qtime.ui > ui/qtime.py
	pyrcc4 ui/qtime.qrc > ui/qtime.py


.PHONY: clean

clean:
	rm -f ui/qtime.py ui/*pyc
