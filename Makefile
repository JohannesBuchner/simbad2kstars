
all: planets.kstarcat GlC.kstarcat SB.kstarcat peculiar.kstarcat

# everybody loves planets
planets.kstarcat:
	python query.py "otype = 'Pl'" $@

# bright globular clusters, some of the oldest objects we know about
GlC.kstarcat:
	python query.py "Vmag<8.5&otype = 'GlC'" $@

# some bright objects which might have interesting spectra to look at
SB.kstarcat:
	python query.py "Vmag<5&otype = 'SB*'" $@
peculiar.kstarcat:
	python query.py "Vmag<7&otype = 'Pe*'" $@

.PHONY: all
