# CPLEX
FROM python:3.9 AS cplex

COPY docker-utils/cplex_studio2211.linux_x86_64.bin /cplex/cplex_studio2211.linux_x86_64.bin
COPY docker-utils/response.properties /cplex/response.properties

RUN apt-get update && apt-get install -y default-jre

RUN chmod u+x /cplex/cplex_studio2211.linux_x86_64.bin
RUN /cplex/cplex_studio2211.linux_x86_64.bin -f /cplex/response.properties
RUN rm -rf /cplex

# Rodeo
FROM python:3.9 AS rodeo
COPY --from=cplex /opt/cplex /opt/cplex

# CPLEX bindings
WORKDIR /opt/cplex/cplex/python/3.9/x86-64_linux
RUN python3 setup.py install

# Verify CPLEX installed
RUN /opt/cplex/cplex/bin/x86-64_linux/cplex -h

WORKDIR /
COPY . /ranking_refinements
RUN pip install ranking_refinements/
RUN chmod u+x /ranking_refinements/ranking_refinements/scripts/run_experiments.sh

WORKDIR /ranking_refinements/ranking_refinements/
CMD make plot
