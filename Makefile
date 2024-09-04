experiments:
	@echo 'Running experiments and plotting results...'
	docker-compose up ranking-refinements
	@echo 'Done! Figures available in ./figures'

paper: experiments
	@echo 'Copying figures to appropriate paths...'

	cp "./figures/combined_useful_by_dataset/K/log_scale/Astr-CombUseful__duration[sec]_by_K__log_scaled__lines.pdf" ./paper/figures/astr_k.pdf
	cp "./figures/combined_useful_by_dataset/K/linear_scale/Law-CombUseful__duration[sec]_by_K__linear_scaled__lines.pdf" ./paper/figures/law_k.pdf
	cp "./figures/combined_useful_by_dataset/K/linear_scale/MEPS-CombUseful__duration[sec]_by_K__linear_scaled__lines.pdf" ./paper/figures/meps_k.pdf
	cp "./figures/combined_useful_by_dataset/K/linear_scale/TPC-H-CombUseful__duration[sec]_by_K__linear_scaled__lines.pdf" ./paper/figures/tpch_k.pdf

	cp "./figures/combined_useful_by_dataset/max_deviation/linear_scale/Astr-CombUseful__duration[sec]_by_max_deviation__linear_scaled__lines.pdf" ./paper/figures/astr_eps.pdf
	cp "./figures/combined_useful_by_dataset/max_deviation/linear_scale/Law-CombUseful__duration[sec]_by_max_deviation__linear_scaled__lines.pdf" ./paper/figures/law_eps.pdf
	cp "./figures/combined_useful_by_dataset/max_deviation/linear_scale/MEPS-CombUseful__duration[sec]_by_max_deviation__linear_scaled__lines.pdf" ./paper/figures/meps_eps.pdf
	cp "./figures/combined_useful_by_dataset/max_deviation/linear_scale/TPC-H-CombUseful__duration[sec]_by_max_deviation__linear_scaled__lines.pdf" ./paper/figures/tpch_eps.pdf

	cp "./figures/combined_useful_by_dataset/number_of_constraints/linear_scale/Astr-CombUseful__duration[sec]_by_number_of_constraints__linear_scaled__lines.pdf" ./paper/figures/astr_num.pdf
	cp "./figures/combined_useful_by_dataset/number_of_constraints/linear_scale/Law-CombUseful__duration[sec]_by_number_of_constraints__linear_scaled__lines.pdf" ./paper/figures/law_num.pdf
	cp "./figures/combined_useful_by_dataset/number_of_constraints/linear_scale/MEPS-CombUseful__duration[sec]_by_number_of_constraints__linear_scaled__lines.pdf" ./paper/figures/meps_num.pdf
	cp "./figures/combined_useful_by_dataset/number_of_constraints/linear_scale/TPC-H-CombUseful__duration[sec]_by_number_of_constraints__linear_scaled__lines.pdf" ./paper/figures/tpch_num.pdf

	cp "./figures/combined_useful_by_dataset/constraints_bounds/linear_scale/Astr-CombUseful__duration[sec]_by_constraints_bounds__linear_scaled__lines.pdf" ./paper/figures/astr_const_type.pdf
	cp "./figures/combined_useful_by_dataset/constraints_bounds/linear_scale/Law-CombUseful__duration[sec]_by_constraints_bounds__linear_scaled__lines.pdf" ./paper/figures/law_const_type.pdf
	cp "./figures/combined_useful_by_dataset/constraints_bounds/linear_scale/MEPS-CombUseful__duration[sec]_by_constraints_bounds__linear_scaled__lines.pdf" ./paper/figures/meps_const_type.pdf
	cp "./figures/combined_useful_by_dataset/constraints_bounds/linear_scale/TPC-H-CombUseful__duration[sec]_by_constraints_bounds__linear_scaled__lines.pdf" ./paper/figures/tpch_const_type.pdf

	cp "./figures/algorithms_comparison/Astr-CombUseful__duration[sec]_by_algorithm__linear_scaled__lines.pdf" ./paper/figures/astr_method.pdf
	cp "./figures/algorithms_comparison/Law-CombUseful__duration[sec]_by_algorithm__log_scaled__lines.pdf" ./paper/figures/law_method.pdf
	cp "./figures/algorithms_comparison/MEPS-CombUseful__duration[sec]_by_algorithm__linear_scaled__lines.pdf" ./paper/figures/meps_method.pdf
	cp "./figures/algorithms_comparison/TPC-H-CombUseful__duration[sec]_by_algorithm__linear_scaled__lines.pdf" ./paper/figures/tpch_method.pdf

	cp "./figures/data_size/Astronauts-CombUseful__duration[sec]_by_data_size__linear_scaled__lines.pdf" ./paper/figures/astr_size.pdf
	cp "./figures/data_size/Law-CombUseful__duration[sec]_by_data_size__linear_scaled__lines.pdf" ./paper/figures/law_size.pdf
	cp "./figures/data_size/MEPS-CombUseful__duration[sec]_by_data_size__linear_scaled__lines.pdf" ./paper/figures/meps_size.pdf
	cp "./figures/data_size/TPC-H-CombUseful__duration[sec]_by_data_size__linear_scaled__lines.pdf" ./paper/figures/tpch_size.pdf

	@echo 'Compiling paper with new figures...'
	docker-compose up latex
	mv ./paper/main.pdf .
	@echo 'Done! Recompiled paper is at ./main.pdf'

clean:
	rm -r ./figures/*
	rm ./paper/figures/astr_*.pdf ./paper/figures/law_*.pdf ./paper/figures/meps_*.pdf ./paper/figures/tpch_*.pdf
	rm -f ./main.pdf ./paper/main.blg ./paper/main.bbl ./paper/main.aux ./paper/main.log ./paper/main.out ./paper/comment.cut
	docker-compose rm -f
	docker rmi rodeo:latest
