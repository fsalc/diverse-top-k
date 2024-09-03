experiments:
	@echo 'Running experiments and plotting results...'
	docker-compose up ranking-refinements

paper: experiments
	@echo 'Compiling paper with new figures...'
	docker-compose up latex

clean:
	rm -r figures/*