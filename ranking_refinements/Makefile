run:
	@echo "Running experiments...";
	./scripts/run_experiments.sh;
	@echo "Aggregating data size experiments..."
	python ./scripts/combine_data_size_stats.py;

plot: run
	@echo "Plotting results...";
	python plot.py;

clean:
	@echo "Cleaning environment:";
	find ./experiments -name "*.txt" -type f -delete;
	find ./experiments -name "*.csv" -type f -delete;