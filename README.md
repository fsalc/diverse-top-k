# Query Refinement for Diverse Top-k Selection

This repository contains the ① reproducibility package for running our experiments and ② the implementation of our algorithm, which may be imported and used as a Python library.

If there are any issues evaluating the reproducibility package or otherwise using the implementation, please feel free to create an issue on GitHub or send an email.

## ① Reproducibility Package

* We containerized our experiments suite in order to ensure the correct dependencies are installed and the proper setup is performed.
    - The host machine should have 16 GB memory, and at least 256 GB of available disk space
    - Please ensure Docker, docker-compose, and GNU make are all installed on your system
* In general, a license for **IBM CPLEX is required** for our implementation. Please ensure to place the `.bin` file of your licensed installer in the `docker-utils` folder, and the scripts will take care of the rest.
* Some of the datasets are too large to store in this repository. A link will be provided here shortly, or please contact us.
* In order to run the experiments, generate plots, and recompile the paper, simply run
```
make paper
```
* We expect that the full suite of experiments will take between 24-48 hours depending on hardware setup.
* If something goes wrong, please try `make clean && make paper` or feel free to contact us.


## ② Algorithm Implementation

### Structure

* The technical details behind our algorithm may be found in our technical report, available at http://arxiv.org/abs/2403.17786
* All of the source code for implementation is in `ranking_refinements` folder
    * `fair.py` contains the key components of the implementation, and some example scenarios that may be run by evaluating the file

### Getting everything set up

* Please ensure CPLEX is installed, as well as its included Python bindings.
    - See [here](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-installing) for instructions on installing CPLEX, and [here](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-setting-up-python-api) for instructions on setting up the Python bindings
* From this directory, run
```pip install ./ranking_refinements```
    - This should install all the necessary dependencies and allow you to use the library.

### Running the algorithm

* At the end of `fair.py`, there are a few example cases with various datasets
* Let's look at one example scenario in order to illustrate the usage of our library:

``` 
from ranking_refinements.fair import Ranking, Constraints, Constraint, Group, UsefulMethod, RefinementMethod

constraints = Constraints(
    Constraint(Group("Gender", "F"), (4, 2)),
    Constraint(Group("Gender", "M"), (4, 2)),
)

ranking = Ranking('SELECT * FROM "data/candidates.csv" WHERE ("Major" = \'CS\' OR Major = \'EE\') AND "Hours" >= 90 AND "Hours" <= 100 ORDER BY "Gpa" DESC')
```

#### Constraints

* `Constraints` holds many instances of `Constraint`
    - An instance of `Constraint` is initialized with a `Group` and a tuple `(k, cardinality)`
    - A `Group` is initialized with an attribute from the database, and a value in its domain
    - For example, `Constraint(Group("Gender", "F"), (4, 2))` encodes the constraint:
    > At least 2 of the top-4 candidates should belong to the group `Gender=F`
    - When initializing `Constraint`, the optional `sense` keyword argument can be `L` or `U` for at-least and at-most respectively.

#### Rankings

* `Ranking` holds an SPJ query with (1) a WHERE clause and (2) an ORDER BY clause.
    - An instance of `Ranking` is initialized with a SQL query (as a string)

#### Refinements

* With a `Ranking` and a set of `Constraints`, we may refine the query by calling the `refine` method on the `Ranking` object
    - For our example, we would call `ranking.refine(constraints)`
    - `refine` can be configured with many parameters, such as
        + `max_deviation`: Maximum average deviation allowed from the constraint set
        + `method`: 