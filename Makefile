EX = ex/phase01_train.ex ex/phase01_test.ex
IN = AAE_PhonSem.in
PROC = AAE_PhonSem_train.tcl

all: network examples trainproc

network: $(IN)

examples: $(EX)

trainproc: $(PROC)

$(IN): %.in: network.json
	aae_modeling_scripts/buildNetworkFile.py $<

$(PROC): %.tcl: training.json
	aae_modeling_scripts/buildProcScript.py $<

ex/phase%.ex: phase%.json
	aae_modeling_scripts/buildExampleFile.py $<

clean:
	rm *.in
	rm *.tcl
	rm ex/*
