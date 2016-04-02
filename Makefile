MODEL_ARGS =  --signaling=.5 --moffset=.1

PDFS = $(patsubst %,%.pdf,$(MODELS))
PNGS = $(patsubst %,%.png,$(MODELS))

all: $(PDFS)

pngs: $(PNGS)

%.pic: %.json $(MODEL) 
	python $(MODEL) $(MODEL_ARGS) $<

%.pdf: %.pic
	pic < $< | groff -mpic | ps2pdf - > $@

%.png: %.pdf
	gs -sDEVICE=png256 -sOutputFile=$@ -r300 -dBATCH -dNOPAUSE $<

%.display: %.pdf
	open $<

clean:
	rm -f $(PDFS) $(PNGS)


