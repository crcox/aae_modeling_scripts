EX = ex/phase01_train.ex ex/phase01_test.ex
IN = AAE_PhonSem.in
PROC = AAE_PhonSem_train.tcl

all: network examples trainproc

stim:
	mkdir -p stimuli/AAE/json
	mkdir -p stimuli/AAE/pkl
	mkdir -p stimuli/SAE/json
	mkdir -p stimuli/SAE/pkl
	mkdir -p stimuli/AAE/dialect/json
	mkdir -p stimuli/AAE/dialect/pkl
	mkdir -p stimuli/SAE/dialect/json
	mkdir -p stimuli/SAE/dialect/pkl
	tree stimuli
	./aae_modeling_scripts/GenerateSAE_master.py
	./aae_modeling_scripts/GenerateAAE_master.py
	./aae_modeling_scripts/GenerateSAE_dialect_master.py
	./aae_modeling_scripts/SubsetStimuli.py

network: $(IN)

examples: $(EX)

trainproc: $(PROC)

$(IN): %.in: network.json
	./aae_modeling_scripts/buildNetworkFile.py $<

$(PROC): %.tcl: training.json
	./aae_modeling_scripts/buildProcScript.py $<

ex/phase%.ex: phase%.json
	./aae_modeling_scripts/buildExampleFile.py $<

clean:
	rm *.in
	rm *.tcl
	rm ex/*

cleanstim:
	rm -rf ./stimuli
