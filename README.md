# Query Refinement for Diverse Top-k Selection

## Reproducibility Package

* We containerized our experiments suite in order to ensure the correct dependencies are installed and the proper setup is performed.
    - Please ensure Docker, docker-compose, and GNU make are all installed on your system
* In general, a license for IBM CPLEX is required for our implementation. Please ensure to place the `.bin` file of your licensed installer in the `docker-utils` folder, and the scripts will take care of the rest.
* Some of the datasets are too large to store in this repository. A link will be provided here shortly, or please contact us.
* In order to run the experiments, generate plots, and recompile the paper, simply run
```
make paper
```
* We expect that the full suite of experiments will take on 24-48 hours depending on hardware setup.
* If something goes wrong, please try `make clean && make paper` or feel free to contact us.

## Structure

* Technical report is available at http://arxiv.org/abs/2403.17786
* Source code for implementation is in `ranking_refinements` folder
    * `fair.py` contains the key components of the implementation, and some example scenarios that may be run by evaluating the file

## Running the algorithm

* At the end of `fair.py`, there are a few example cases with various datasets
* Constraint sets are built by `Constraints(Constraint(Group(Attribute, Value), (K, Cardinality), sense='L' or 'U'), ...)` where `Attribute` and `Value` are both strings, and `K` and `Cardinality` are integers
* Queries are defined by `Ranking(SQL Query)` where `SQL Query` is a string and has a 
    (1) WHERE clause
    (2) ORDER BY clause
* Rankings may be refined subject to a set of constraints by `ranking.refine(constraints)`
    * `refine` has a few options, such as `max_deviation`, `method`, `opt`, etc...