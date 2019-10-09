.PHONY: test watch dev requirements


test:
	watchexec -rce py  'sleep 2 && pytest -s'

dev: 
	watchexec -rce  py "./x.sh"
	
requirements:
	pipreqs --force . 


dist: requirements
