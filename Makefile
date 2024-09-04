experiments:
	@echo 'Running experiments and plotting results...'
	docker-compose up ranking-refinements
	@echo 'Done! Figures available in ./figures'

paper: experiments
	@echo 'Compiling paper with new figures...'
	docker-compose up latex
	@echo 'Done! Recompiled paper is at ./paper/main.pdf'

clean:
	rm -r figures/*
	docker-compose rm -f
	docker rmi rodeo:latest
