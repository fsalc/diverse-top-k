FROM openjdk:8-jre
COPY --from=python:3.6 / /

COPY docker-utils/cplex_studio2211.linux_x86_64.bin /cplex/cplex_studio2211.linux_x86_64.bin
COPY docker-utils/response.properties /cplex/response.properties

RUN chmod u+x /cplex/cplex_studio2211.linux_x86_64.bin
RUN /cplex/cplex_studio2211.linux_x86_64.bin -f /cplex/response.properties
RUN rm -rf /cplex

COPY . /ranking_refinements
RUN pip install ranking_refinements/
CMD /ranking_refinements/run_all.sh
