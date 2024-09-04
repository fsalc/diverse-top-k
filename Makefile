experiments:
	@echo 'Running experiments and plotting results...'
	docker-compose up ranking-refinements
	@echo 'Done! Figures available in ./figures'

paper: experiments
	@echo 'Compiling paper with new figures...'
	docker-compose up latex
	mv ./paper/main.pdf .
	@echo 'Done! Recompiled paper is at ./main.pdf'

clean:
	rm -r ./figures/*
	rm -f ./main.pdf ./paper/main.blg ./paper/main.bbl ./paper/main.aux ./paper/main.log ./paper/main.out ./paper/comment.cut
	docker-compose rm -f
	docker rmi rodeo:latest
