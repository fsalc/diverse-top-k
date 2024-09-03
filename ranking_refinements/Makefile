run:
	@echo "Running experiments...";
	./scripts/run_experiments.sh;

plot: run
	@echo "Plotting results...";
	python plot.py;

clean:
	@echo "Cleaning environment:";
	find ./experiments -name "*.txt" -type f -delete;
	find ./experiments -name "*.csv" -type f -delete;