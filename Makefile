.PHONY: test watch dev requirements dev2


test:
	watchexec -rce py  'sleep 3 && pytest -srpP'

dev: 
	watchexec -rce py "./x.sh --debug" 
	
wun: 
	watchexec -rce py "./x.sh" 

run: 
	"./x.sh" 

requirements:
	pipreqs --force . 


dist: requirements
