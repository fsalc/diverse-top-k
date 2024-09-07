from setuptools import setup

setup(
   name='ranking_refinements',
   version='1.0',
   description='Ranking refinements',
   packages=['ranking_refinements'],
   install_requires=['sqlglot==15.2.0', 'seaborn==0.13.2', 'matplotlib==3.7.1', 'numpy==1.24.3', 'pandas==2.0.2', 'duckdb==0.8.0', 'PuLP==2.7.0'],
)
