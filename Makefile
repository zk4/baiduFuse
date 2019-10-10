.PHONY: test watch dev requirements dev2


test:
	watchexec -rce py  'sleep 2 && pytest -s'

dev: 
	watchexec -rce py "./x.sh --debug" 
	
y: 
	watchexec -rce py "./y.sh"
run: 
	./x.sh

requirements:
	pipreqs --force . 


dist: requirements
