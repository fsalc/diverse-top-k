from typing import Optional, List, Union
import duckdb as d
import numpy as np


class Condition:

    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value

    @staticmethod
    def _get_value_str(value):
        if isinstance(value, float) or isinstance(value, int) or isinstance(value, np.int64):
            return str(value)
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, list):
            return "(" + ", ".join([Condition._get_value_str(v) for v in value]) + ")"
        raise ValueError(f"Type of value isn't valid {value}: {type(value)}")

    def __repr__(self):
        if len(self.field.split('.')) == 1:
            return f'''{f'"{self.field}"' if '.' not in self.field else self.field} {self.operator} {self._get_value_str(self.value)}'''
        return f'{self.field} {self.operator} {self._get_value_str(self.value)}'


class Conditions:

    def __init__(self, *conditions: Condition):
        self.conditions: List[conditions] = list(conditions)

    def add(self, condition):
        self.conditions.append(condition)

    def __iter__(self):
        for c in self.conditions:
            yield c

    def __len__(self):
        return len(self.conditions)

    def __repr__(self):
        return ' AND '.join([str(cond) for cond in self.conditions])


class OrderByClause:

    def __init__(self, field: str, is_desc: bool = True):
        self.field: str = field
        self.is_desc: bool = is_desc

    def __repr__(self):
        return f'''ORDER BY {f'"{self.field}"' if '.' not in self.field else self.field} {"DESC" if self.is_desc else "ASC"}'''


class Query:

    def __init__(self, dataset: Union[str, List[str]],
                 conditions: Optional[Conditions] = None,
                 order_by_clause: Optional[OrderByClause] = None,
                 select: str = '*',
                 limit: Optional[int] = None,
                 base_dir: str = 'data/',
                 label: str = None,
                 verbatim: str = None):
        self._datasets: List[str] = [f'"{base_dir}{dataset}"'] if isinstance(dataset, str) else \
            [f'"{base_dir}{data}" as {data.split("/")[-1][0]}' for data in dataset]
        self._conditions: Conditions = Conditions()
        if conditions:
            self._conditions = conditions
        self._select = select
        self._order_by_clause: Optional[OrderByClause] = order_by_clause
        self._limit: Optional[int] = limit
        self.base_dir = base_dir
        self._joins = []
        self.label = label # For experiments
        self.verbatim = verbatim

    def set_label(self, label: str) -> 'Query':
        self.label = label
        return self

    def condition(self, condition: Condition) -> 'Query':
        self._conditions.add(condition)
        return self

    def join(self, dataset, on) -> 'Query':
        self._joins += [f'JOIN "{self.base_dir}{dataset}" AS {dataset.split("/")[-1][0]} ON {on}\n']
        return self

    def clean_conditions(self) -> 'Query':
        self._conditions = Conditions()
        return self

    def where(self, *conditions: Condition) -> 'Query':
        for cond in conditions:
            self.condition(cond)
        return self

    def order_by(self, field: str, is_desc: bool = True) -> 'Query':
        self._order_by_clause = OrderByClause(field, is_desc)
        return self

    def limit(self, lim) -> 'Query':
        self._limit = lim
        return self

    def count(self) -> 'Query':
        self._select = 'COUNT(*)'
        return self

    @property
    def _limit_clause(self) -> str:
        if self._limit:
            return f'LIMIT {self._limit}'
        return ''

    def run(self):
        return d.sql(self.build()).fetchnumpy()

    def build(self) -> str:
        if self.verbatim: return self.verbatim
        return f'SELECT {self._select} ' \
               f'FROM {",".join(self._datasets)} ' \
               f'{"".join(self._joins)}' \
               f'WHERE {self._conditions} ' \
               f'{self._order_by_clause} ' \
               f'{self._limit_clause} '


