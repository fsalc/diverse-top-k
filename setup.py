from setuptools import setup

setup(
   name='ranking_refinements',
   version='1.0',
   description='Ranking refinements',
   packages=['ranking_refinements'],
   install_requires=['sqlglot', 'seaborn', 'matplotlib', 'numpy', 'duckdb==0.8.0', 'PuLP==2.7.0'],
)
