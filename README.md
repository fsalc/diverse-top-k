# Query Refinement for Diverse Top-k Selection

This repository contains the ① reproducibility package for running our experiments and ② the implementation of our algorithm, which may be imported and used as a Python library.

If there are any issues evaluating the reproducibility package or otherwise using the implementation, please feel free to create an issue on GitHub or send an email.

## ① Reproducibility Package

```
          ❶                           ❷                           ❸                       
  Install dependencies         Download datasets         Run experiments suite
```

### ❶ Install dependencies

* We containerized our experiments suite in order to ensure the correct dependencies are installed and the proper setup is performed.
    - The host machine should have 16 GB memory, and at least 256 GB of available disk space to ensure enough room to build the containers, hold the datasets, etc.
    - Please ensure Docker, docker-compose, and GNU make are all installed on your system, e.g. on Debian

    ```apt-get install docker docker-compose build-essential```

> [!IMPORTANT]
> In general, a license for **IBM CPLEX is required** for our implementation. Please ensure to place the `.bin` file of your licensed installer **(for Linux x86-64)** in the [docker-utils](docker-utils) folder, and the scripts will take care of the rest.

> [!NOTE]
>  For compatability, we recommend IBM ILOG CPLEX Optimization Studio V22.1.1 (part no. `G0798ML`). From it, download IBM ILOG CPLEX Optimization Studio V22.1.1 for Linux x86-64.

* Otherwise, no special configuration is required for the system -- anything special is handled by our containers.

### ❷ Datasets

* Some of the datasets are too large to store in this repository. A link will be provided here shortly, or please contact us.

### ❸ Running experiments, generating figures, & recompiling the paper

* In order to run the experiments, generate plots, and recompile the paper, simply run
```shell
make paper
```
* We expect that the full suite of experiments will take between 24-48 hours depending on hardware setup.
* The script runs *all* experiments from which *all data presented in each graph shown in the paper* was collected. 
* The script will also automatically *generate new plots* from the collected data, and *recompile the paper* with the new figures included. If the script terminates successfully, the paper `main.pdf` should be placed into this directory.
* If something goes wrong, please try `make clean && make paper` or feel free to contact us.

### Appendix

#### Modifying experiments

* All experiments are stored as configuration files in [ranking_refinements/experiments_conf](ranking_refinements/experiments_conf).
* The queries, constraints, maximum average deviations $\varepsilon$, methods/algorithms, $k^*$, and other parameters may be controlled by these configuration files.
* Adding a new experiment configuration file requires modifying [ranking_refinements/scripts/run_experiments.sh](ranking_refinements/scripts/run_experiments.sh) in order for it to be run with the suite.

#### Clean-up

* In the case you would like to clean everything up (e.g. starting a fresh run), simply run
```shell
make clean
```

---

## ② Algorithm Implementation

### Structure

* The technical details behind our algorithm may be found in our technical report, available at http://arxiv.org/abs/2403.17786
* All of the source code for implementation is in `ranking_refinements` folder
    * `fair.py` contains the key components of the implementation, and some example scenarios that may be run by evaluating the file

### Getting everything set up

* We assume in this section that you'd like to use the library *outside* of the provided Docker containers for the evaluation of our experiments suite.
* Please ensure CPLEX is installed, as well as its included Python bindings.
    - See [here](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-installing) for instructions on installing CPLEX, and [here](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-setting-up-python-api) for instructions on setting up the Python bindings
* From this directory, run
```pip install ./ranking_refinements```
    - This should install all the necessary dependencies and allow you to use the library.

### Running the algorithm

* At the end of `fair.py`, there are a few example cases with various datasets
* Let's look at one example scenario in order to illustrate the usage of our library:

```python
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
        + `useful_method`: One of `UsefulMethod.QUERY_DISTANCE, UsefulMethod.MAX_ORIGINAL, UsefulMethod.KENDALL_DISTANCE`
        + `method`: One of `RefinementMethod.MILP_OPT, RefinementMethod.MILP, RefinementMethod.BRUTE_PROV, RefinementMethod.BRUTE`
