from copy import deepcopy
from enum import Enum

from pulp import LpVariable, LpProblem, LpAffineExpression, LpMinimize, LpStatus, LpInteger, lpSum, CPLEX_PY, CPLEX_CMD
import duckdb as d
import numpy as n
from timeit import default_timer as timer

import sqlglot
from collections import defaultdict
from ranking_refinements.query import Condition, Conditions
from itertools import chain, combinations, product
import heapq

class UsefulMethod(Enum):
    QUERY_DISTANCE = 0
    KENDALL_DISTANCE = 1
    JACCARD_DISTANCE = 2
    MAX_ORIGINAL = 3

class RefinementMethod(Enum):
    MILP = 0
    MILP_OPT = 1
    BRUTE = 2
    BRUTE_PROV = 3

NUMERIC_OPS = {sqlglot.expressions.LT: '<',
                sqlglot.expressions.LTE: '<=',
                sqlglot.expressions.GT: '>', 
                sqlglot.expressions.GTE: '>='}
CATEGORICAL_OPS = [sqlglot.expressions.EQ, sqlglot.expressions.NEQ]

class Group(object):
    def __init__(self, attr, val):
        self.attr, self.val = attr, val

    def __str__(self):
        return f'{self.attr} = {self.val}'


class Constraint(object):
    """
    Cardinalities are passed as tuples (k, v) where k is the prefix size and v is the target cardinality
    """

    def __init__(self, group, *cardinalities, sense='L'):
        self.group, self.cardinalities, self.sense = group, cardinalities, sense

    def __str__(self):
        return f'{self.group} (TOP {self.cardinalities[0][0]}) > {self.cardinalities[0][1]} '


class Constraints(object):
    def __init__(self, *constraints: Constraint, label=None):
        self.constraints = constraints
        self.p_star = max([k[0] for c in constraints for k in c.cardinalities])
        self.label = label # For experiments

    def __iter__(self):
        for c in self.constraints:
            yield c

    def __len__(self):
        return len(self.constraints)

    def __getitem__(self, item):
        return self.constraints[item]
    
    def __str__(self):
        return ", ".join(map(str, self.constraints))

    def attrs(self):
        return {c.group.attr for c in self.constraints}

    def on(self, attr):
        return list(filter(lambda c: c.group.attr == attr, self.constraints))

# Small utility
def string_is_float(x):
    try:
        float(x)
        return True
    except:
        return False

class Refinement(object):
    def __init__(self, prov):
        self.prov = prov
        cs = []
        for k, v in self.prov.items():
            if type(v) == dict:
                for k2, v2 in v.items():
                    # TODO: Deal with rounding
                    cs.append(Condition(k, k2, round(v2, 5)))
            elif type(v) == list:
                cs.append(Condition(k, 'IN', v))
            else:
                return Exception('unknown type in refinement')
        self.conditions = Conditions(*cs)

    def __str__(self):
        return(str(self.prov))
        # TODO: Pretty print
        # b = ""
        # for k, v in self.prov.items():
        #     b += f'{k}: {" | ".join(v)}'
        #     b += '\n'
        # return b

class Lineage(object):
    # TODO: make permutation-invariant on attrs
    def __init__(self, lineage, attrs):
        self.hash = hash(tuple(lineage[attr] for attr in attrs))
        self.lineage = lineage

    def __getitem__(self, item):
        return self.lineage[item]

    def __hash__(self):
        return self.hash
    
    def __eq__(self, item):
        return self.lineage == item.lineage 

class Ranking(object):
    """
    Pass a SQL query into the constructor and call refine with a Constraints object
    """

    def __init__(self, query):
        self.query = sqlglot.parse_one(query)
        self.cached = None
        # print(self.query)
        if self.query.args.get('from'):
            self.from_ = self.query.args['from']
        else:
            raise Exception('Ranking query must have FROM clause')

        if self.query.args.get('order'):
            self.utility = self.query.args['order']
        else:
            raise Exception('Ranking query must have ORDER BY clause')

        if self.query.args.get('where'):
            self.where = self.query.args['where']
        else:
            raise Exception('Ranking query must have WHERE clause (otherwise set of refinements is empty)')
        
        if self.query.args.get('joins'):
            self.joins = self.query.args['joins']
        else:
            self.joins = []

    def attrs(self):
        return list(set(d.sql(
            sqlglot.select('*').from_(self.from_).limit(1).sql()
        ).fetchnumpy().keys()))

    def conds(self):
        return self.query.args['where'].find_all(sqlglot.expressions.Predicate)
    
    def numerical(self):
        return [cond for cond in self.conds() if type(cond) in NUMERIC_OPS.keys()]

    def categorical(self):
        return [cond for cond in self.conds() if type(cond) in CATEGORICAL_OPS]

    def conds_attrs(self, conds):
            # This assumes that predicates only contain constants
            # which are the only predicates supported for refinement at the moment
            return {cond.this.sql().strip('"') for cond in conds}

    def conds_constants(self, conds):
            # This assumes that predicates only contain constants
            # which are the only predicates supported for refinement at the moment
            return list({constant.this for cond in conds for constant in cond.find_all(sqlglot.expressions.Literal)})

    def domain(self, attr):
        if self.cached:
            return {self.cached[attr][i] for i in range(len(self.cached[attr]))}
        else:
            q = sqlglot.select(f'"{attr}"' if '.' not in attr else f'{attr} as "{attr}"').distinct().from_(self.from_)
            for join in self.joins:
                q = q.join(join)

            return set(d.sql(
                q.sql()
            ).fetchnumpy()[attr].filled())
    
    def top_k_of_groups_query(self, select=['*'], attrs=None, top=None):
        return f'''
            SELECT *, ROW_NUMBER() OVER () - 1 AS r FROM 
                (SELECT *, ROW_NUMBER() OVER (PARTITION BY {', '.join(f'"{attr}"' for attr in attrs)} ORDER BY __rank)
                AS __group_rank 
                FROM (SELECT {', '.join(f'"{s}"' if '.' not in s else f'{s} AS "{s}"' for s in select)}{',' if select else ''} ROW_NUMBER() OVER ({self.utility.sql()}) 
                    AS __rank {self.from_.sql()} {" ".join([join.sql() for join in self.joins])})
                    ORDER BY __rank) 
            WHERE __group_rank <= {top}'''

    # TODO: Use sqlglot builder for this
    def orig_ranked(self, attrs=None, top=None, opt=True):
        # for tpch
        # TODO: refactor
        quotedRenamed = " ".join([f'"{attr}"' if '.' in attr and ('"' not in attr and "'" not in attr) else attr for attr in self.where.args['this'].sql().split(' ')])

        if opt:
            return list(d.sql(f'''
                    SELECT * FROM ({self.top_k_of_groups_query(select=attrs, attrs=attrs, top=top)}) 
                    WHERE {quotedRenamed} ORDER BY __rank LIMIT {top}'''
            ).fetchnumpy()['r'])

        q = sqlglot.select('*').from_(self.from_).order_by(self.utility)
        for join in self.joins:
            q = q.join(join)
        return list(d.sql(
            sqlglot.subquery(
                sqlglot.subquery(q).select(
                    'row_number() over () - 1 as r').select("*")
            ).select('r').where(quotedRenamed).order_by('r').limit(top).sql()
        ).fetchnumpy()['r'])

    # TODO: Use sqlglot builder for this
    def all_ranked(self, select=['*'], attrs=None, top=None, opt=True):
        if opt:
            self.cached = {k: v.filled() for k, v in d.sql(
                self.top_k_of_groups_query(select=select, attrs=attrs, top=top)
            ).fetchnumpy().items()}
            return self.cached
        
        sq = sqlglot.select('*').from_(self.from_)
        for join in self.joins:
            sq = sq.join(join)
        q = sqlglot.subquery(sq).select('*').select('ROW_NUMBER() OVER () - 1 AS r')


        self.cached = {k: v.filled() for k, v in d.sql(
            q.order_by(self.utility).sql()
        ).fetchnumpy().items()}
        return self.cached

    # TODO: Use sqlglot builder for this
    def group(self, g, attrs=None, top=None, opt=True):
        if self.cached:
            t = []
            for i in range(len(self.cached[g.attr])):
                # backwards compatability
                try:
                    g.val = float(g.val)
                except ValueError:
                    pass
                if self.cached[g.attr][i] == g.val: t.append(self.cached['r'][i])
            return t
        else:
            if opt:
                return list(d.sql(f'''
                        SELECT * FROM ({self.top_k_of_groups_query(select=attrs.union({g.attr}), attrs=attrs, top=top)}) WHERE "{g.attr}" == \'{g.val}\''''       
                ).fetchnumpy()['r'])

            q = sqlglot.select('*').from_(self.from_).order_by(self.utility)
            for join in self.joins:
                q.join(join)

            return list(d.sql(
                sqlglot.subquery(
                    sqlglot.subquery(q).select(
                        'row_number() over () - 1 as r').select(f"{g.attr}")
                ).select('r').where(f'"{g.attr}" == \'{g.val}\'').sql()
            ).fetchnumpy()['r'])


    def refine(self, constraints, max_deviation=0, useful_method=UsefulMethod.QUERY_DISTANCE, debug=False, method=RefinementMethod.MILP_OPT, opt=True, only_lower_bound_card_constraints=False):
        start_time = timer()

        if method == RefinementMethod.MILP or method == RefinementMethod.MILP_OPT:
            opt = (method == RefinementMethod.MILP_OPT)
            if debug: print(f'starting MILP refinement algorithm with {useful_method}, optimizations {"on" if opt else "off"}')
            ### Grab Necessary Data ###

            p_star = constraints.p_star

            protected = {attr for attr in constraints.attrs()}
            attrs = self.conds_attrs(self.conds())
            relevant_attrs = list(protected.union(attrs))

            all_ranked = self.all_ranked(select=relevant_attrs, attrs=attrs, top=p_star, opt=opt)
            orig_ranked = self.orig_ranked(attrs=attrs, top=p_star, opt=opt)
            domains = {attr: self.domain(attr) for attr in set(attrs).difference(protected)}
            cardinality = len(all_ranked[list(all_ranked.keys())[0]])
            print('card', cardinality)

            tuples_with_constraints = set()
            for c in constraints:
                group = self.group(c.group, attrs=attrs, top=p_star)
                for t in group:
                    tuples_with_constraints.add(t)
                if c.sense == 'U': only_lower_bound_card_constraints = False

            ### LP Variables ###

            if debug: print('initializing milp problem')
            problem = LpProblem("BAR", LpMinimize)

            # Position of each tuple in the refined ranking
            if debug: print('initializing rank variables')
            s = [LpVariable(f's_{i}', lowBound=0, upBound=2*cardinality+1) for i in range(cardinality)]

            # LP variables determined by whether tuple t is in top-k
            if debug: print('initializing tuple in top k variables')
            l = {k: {t: LpVariable(f'l_{k}_{t}', lowBound=0, upBound=1, cat=LpInteger) for t in range(cardinality)} 
                for k in list({i[0] for a in protected for c in constraints.on(a) for i in c.cardinalities})}
            
            # Variable to hold the max between constraint difference and zero
            if debug: print('initializing aux variables to score abs difference of mospe')
            m = {a: {
                c.group.val: {k[0]: LpVariable(f'max_{a}_{c.group.val}_{k[0]}', lowBound=0) for k in
                            c.cardinalities} for c in constraints.on(a)} for a in protected}
            
            # LP variables for provenance annotations
            # NOTE: Set of enabled provenance attributes for categorical attributes is equivalent to the set of constants
            # included by categorical predicates in a refinement. This is not the case for numerical predicates, so even
            # though we create their annotations here, we create additional variables that actually reflect the numerical
            # predicate constant for the refinement.
            if debug: print('initializing annotation variables')
            R = {attr: {val: LpVariable(f'R_{str(attr).replace(" ", "_")}_{str(val).replace(" ", "_")}', lowBound=0, upBound=1, 
                                                cat=LpInteger) for val in domains[attr]} for attr in attrs}
            # Additional variables needed to model some distance measures
            if debug: print('initializing distance variables')
            if useful_method == UsefulMethod.QUERY_DISTANCE:
                # Rescaling variables q for Charnes-Cooper transform
                q = {attr: LpVariable(f'q_{attr}', lowBound=0, upBound=1) for attr in self.conds_attrs(self.categorical())}
                # Rescaled categorical selectors
                Rc = {attr: {val: LpVariable(f'Rc_{str(attr).replace(" ", "_")}_{str(val).replace(" ", "_")}',
                                            lowBound=0, upBound=1) for val in domains[attr]} for attr in self.conds_attrs(self.categorical())}
                # Absolute values of difference between original numeric predicate's constant and the refined constant
                Nd = {attr: {} for attr in self.conds_attrs(self.numerical())}
                for predicate in self.numerical():
                    attr = self.conds_attrs([predicate]).pop()
                    Nd[attr][type(predicate)] = LpVariable(f'Nd_{str(attr).replace(" ", "_")}_{NUMERIC_OPS[type(predicate)]}')
            if useful_method == UsefulMethod.JACCARD_DISTANCE:
                # Rescaling variable q for Charnes-Cooper transform
                q = LpVariable('q', lowBound=0, upBound=1) 
                # Rescaled binaries for tuple t in top-k
                lc = {k: {t: LpVariable(f'lc_{k}_{t}', lowBound=0, upBound=1) for t in range(cardinality)} 
                    for k in list({i[0] for a in protected for c in constraints.on(a) for i in c.cardinalities})}
            if useful_method == UsefulMethod.KENDALL_DISTANCE:
                # See case descriptions below
                case_2 = [LpVariable(f'case_two_{t}', lowBound=0, upBound=cardinality) for t in orig_ranked]

                new_tuples = LpVariable('new_tuples', lowBound=0, upBound=cardinality)
                case_3 = [LpVariable(f'case_three_{t}', lowBound=0, upBound=cardinality) for t in orig_ranked]

            if debug: print('initializing value contained by numerical predicate variables')
            I = {attr: {val: {} for val in domains[attr]} for attr in attrs}

            # LP variables for numerical predicate refinements
            for predicate in self.numerical():
                attr = self.conds_attrs([predicate]).pop()
                R[attr][type(predicate)] = LpVariable(f'R_{str(attr).replace(" ", "_")}_{NUMERIC_OPS[type(predicate)]}', lowBound=min(domains[attr]), upBound=max(domains[attr]))
                for val in domains[attr]:
                    I[attr][val][type(predicate)] = LpVariable(f'I_{str(attr).replace(" ", "_")}_{str(val).replace(" ", "_")}_{NUMERIC_OPS[type(predicate)]}', lowBound=0, upBound=1, 
                                                cat=LpInteger)

            # Here we have to assign ordinal weights to categorical variables
            # We also store the number of values included by the original predicate
            if debug: print('assigning counts for categoricl predicates for jaccard difference')
            R_weight = defaultdict(lambda: defaultdict(lambda: 0))
            C_orig = defaultdict(lambda: 0)
            for cond in self.categorical():
                attr = [ident for ident in cond.find_all(sqlglot.expressions.Identifier)][0] # There should only be one
                val = list(filter(lambda x: x.is_string, [v for v in cond.find_all(sqlglot.expressions.Literal)]))
                if val:
                    R_weight[attr.this][val[0].this] = 1
                    C_orig[attr.this] += 1

            if opt:
                # LP variables for whether lineage is selected by current refinement
                if debug: print('initializing lineage in ranking variables')
                lineages, tuples_lineage = set(), {}
                for t in range(cardinality):
                    lineage = Lineage({attr: all_ranked[attr][t] for attr in attrs}, attrs)
                    lineages.add(lineage)
                    tuples_lineage[t] = lineage
                cl, r = 0, {}
                for lineage in lineages:
                    r[lineage] = LpVariable(f'r_{cl}', lowBound=0, upBound=1, cat=LpInteger)
                    cl += 1
            else:
                # LP variables for whether tuple t is selected by current refinement
                if debug: print('initializing tuple in ranking variables')
                r = {t: LpVariable(f'r_{t}', lowBound=0, upBound=1, cat=LpInteger) for t in range(cardinality)}


            ### LP Constraints ###

            # Constraint for modeling the position of tuple
            if debug: print('adding constraints on scores')
            if opt:
                # Some bookkeeping to go from lineage to term in terms array
                lineage_map = {lineage: i for (lineage, i) in zip(lineages, range(len(lineages)))}
                # Better to keep this array and increment it (unfortunately we need to use immutable tuples as values)
                terms = [(r[lineage], 0) for lineage in lineages]
                for t in range(cardinality):
                    if not opt or (opt and (t in tuples_with_constraints or not useful_method == UsefulMethod.QUERY_DISTANCE)):
                        # This tuple belongs to a lineage, so we need to change its coefficeint to -cardinality - 1 +
                        # the number of the tuples of this lineage that occur before this one
                        o = terms[lineage_map[tuples_lineage[t]]][1]
                        terms[lineage_map[tuples_lineage[t]]] = (r[tuples_lineage[t]], -cardinality - 1 + terms[lineage_map[tuples_lineage[t]]][1])
                        # PuLP copies the array so we can continue to modify it
                        if opt and only_lower_bound_card_constraints:
                            problem += s[t] >= LpAffineExpression(terms, constant=cardinality+1)
                        else:
                            problem += s[t] == LpAffineExpression(terms, constant=cardinality+1)
                        # Restore the value since we are done copying here
                        terms[lineage_map[tuples_lineage[t]]] = (r[tuples_lineage[t]], o)
                    # We saw another tuple of this lineage and processed it, so increase the count for this lineage
                    terms[lineage_map[tuples_lineage[t]]] = (r[tuples_lineage[t]], terms[lineage_map[tuples_lineage[t]]][1] + 1)
            # else:
            #     for t in range(cardinality):
            #         terms = [(r[i], 1) for i in range(0, t)] + [(r[t], -cardinality - 1)]
            #         if opt and only_lower_bound_card_constraints:
            #             problem += s[t] >= LpAffineExpression(terms, constant=cardinality+1)
            #         else:
            #             problem += s[t] == LpAffineExpression(terms, constant=cardinality+1)
            else:
                terms = []
                for t in range(cardinality):
                    if opt and only_lower_bound_card_constraints:
                        problem += s[t] >= LpAffineExpression(terms + [(r[t], -cardinality - 1)], constant=cardinality+1)
                    else:
                        problem += s[t] == LpAffineExpression(terms + [(r[t], -cardinality - 1)], constant=cardinality+1)
                    terms.append((r[t], 1))
                    print(t)

            # Evaluate provenance annotation for numerical variables to 1 if refined predicate includes it
            # TODO: Double check these, make sure they admit only and all values that they should
            for predicate in self.numerical():
                if debug: print('adding constraints for numerical predicate', predicate)
                attr = self.conds_attrs([predicate]).pop()
                M = max(abs(min(domains[attr])), max(domains[attr])) + 100
                for val in domains[attr]:
                    if type(predicate) == sqlglot.expressions.LT:
                        problem += R[attr][sqlglot.expressions.LT] + M * (1 - I[attr][val][sqlglot.expressions.LT]) >= (val - 0.0001)
                        problem += R[attr][sqlglot.expressions.LT] - M * I[attr][val][sqlglot.expressions.LT] <= (val - 0.0001) 
                    elif type(predicate) == sqlglot.expressions.LTE:
                        problem += R[attr][sqlglot.expressions.LTE] + M * (1 - I[attr][val][sqlglot.expressions.LTE]) >= val
                        problem += R[attr][sqlglot.expressions.LTE] - M * I[attr][val][sqlglot.expressions.LTE] <= (val - 0.0001)
                    elif type(predicate) == sqlglot.expressions.GT:
                        problem += R[attr][sqlglot.expressions.GT] + M * I[attr][val][sqlglot.expressions.GT] >= (val + 0.0001)
                        problem += R[attr][sqlglot.expressions.GT] - M * (1 - I[attr][val][sqlglot.expressions.GT]) <= (val + 0.0001)
                    elif type(predicate) == sqlglot.expressions.GTE:
                        problem += R[attr][sqlglot.expressions.GTE] + M * I[attr][val][sqlglot.expressions.GTE] >= (val + 0.0001)
                        problem += R[attr][sqlglot.expressions.GTE] - M * (1 - I[attr][val][sqlglot.expressions.GTE]) <= val
            
            # for attr in self.conds_attrs(self.numerical()):
            #     for val in domains[attr]:
            #         # assumes interval of 2 predicates
            #         problem += lpSum(I[attr][val][op] for op in I[attr][val].keys()) - 2 * R[attr][val] >= 0
            #         problem += lpSum(I[attr][val][op] for op in I[attr][val].keys()) - 2 * R[attr][val] <= 1
                
            # Require tuple to be selected if in current refinement
            conds_count = len(self.numerical()) + len(self.conds_attrs(self.categorical()))
            if opt:
                if debug: print('adding constraints for lineage in ranking')
                for lineage in lineages:
                    categorical = lpSum(R[attr][lineage[attr]] for attr in self.conds_attrs(self.categorical()))
                    numerical = lpSum(I[attr][lineage[attr]][op] for attr in self.conds_attrs(self.numerical()) for op in I[attr][lineage[attr]].keys())
                    problem += categorical + numerical - conds_count * r[lineage] >= 0
                    problem += categorical + numerical - conds_count * r[lineage] <= conds_count - 1
            else:
                if debug: print('adding constraints for tuple in ranking')
                for t in range(cardinality):
                    categorical = lpSum(R[attr][all_ranked[attr][t]] for attr in self.conds_attrs(self.categorical()))
                    numerical = lpSum(I[attr][all_ranked[attr][t]][op] for attr in self.conds_attrs(self.numerical()) for op in I[attr][all_ranked[attr][t]].keys())
                    problem += categorical + numerical - conds_count * r[t] >= 0
                    problem += categorical + numerical - conds_count * r[t] <= conds_count - 1

            # Enforce l_k_t for the prefixes
            if debug: print('adding constraints for tuple in top-k')
            for c in constraints:
                for k in c.cardinalities:
                        for t in range(cardinality):
                            problem += s[t] + (2 * cardinality + 1) * l[k[0]][t] >= k[0] - 1
                            problem += s[t] - (2 * cardinality + 1) * (1 - l[k[0]][t]) <= k[0] - 1

            # Max zero (don't penalize for exceeding lower bound or staying under upper bound)
            if debug: print('adding constraints for difference from card. constraint')
            for c in constraints:
                for k in c.cardinalities:
                    if c.sense == 'L':
                        problem += m[c.group.attr][c.group.val][k[0]] >= k[1] - lpSum(l[k[0]][t] for t in self.group(c.group, attrs=attrs, top=p_star, opt=opt))
                    elif c.sense == 'U':
                        problem += m[c.group.attr][c.group.val][k[0]] >= lpSum(l[k[0]][t] for t in self.group(c.group, attrs=attrs, top=p_star, opt=opt)) - k[1]
                    else:
                        raise Exception('unsupported cardinality constraint sense ', c.sense)
                    problem += m[c.group.attr][c.group.val][k[0]] >= 0

            ### LP Objective ###

            if debug: print('generating deviation expression')
            fairness = lpSum(
                (1 / (len(constraints) * k[1])) * (m[c.group.attr][c.group.val][k[0]]) for c in constraints for k in
                c.cardinalities)

            if debug: print('adding constraints for distance calculation')
            # Note, Jaccard distance introduces non-linearity, but in this case we are 
            # are able to linearize it using the Charnes-Cooper transformation.
            if useful_method == UsefulMethod.QUERY_DISTANCE:
                # Rc_a_v is q_a iff R_a_v is 1, 0 otherwise
                for a in self.conds_attrs(self.categorical()):
                    for v in Rc[a].keys():
                        problem += Rc[a][v] <= R[a][v]
                        problem += Rc[a][v] <= (1 - R[a][v]) + q[a]
                        problem += Rc[a][v] >= q[a] - (1 - R[a][v])
                    # Find rescaling q such that q times size of union is 1
                    problem += lpSum((1 - R_weight[a][v]) * Rc[a][v] for a in self.conds_attrs(self.categorical()) for v in Rc[a].keys()) + q[a] * C_orig[a] == 1
                for predicate in self.numerical():
                    attr = self.conds_attrs([predicate]).pop()
                    constant = float(self.conds_constants([predicate])[0])
                    problem += Nd[attr][type(predicate)] >= (1/constant) * (R[attr][type(predicate)] - constant)
                    problem += Nd[attr][type(predicate)] >= (1/constant) * (constant - R[attr][type(predicate)])
            if useful_method == UsefulMethod.JACCARD_DISTANCE:
                for t in range(cardinality):
                        problem += lc[p_star][t] <= l[p_star][t]
                        problem += lc[p_star][t] <= (1 - l[p_star][t]) + q
                        problem += lc[p_star][t] >= q - (1 - l[p_star][t])
                problem += lpSum((0 if t in orig_ranked else 1) * lc[p_star][t] for t in range(cardinality)) + q * len(orig_ranked) == 1
            if useful_method == UsefulMethod.KENDALL_DISTANCE:
                new_ranked = list(set(range(cardinality)) - set(orig_ranked))
                problem += new_tuples == lpSum(l[p_star][t] for t in new_ranked)
                # See cases from Fagin paper
                # Case 1 never occurs: tuples always in same relative order
                # Case 2: both tuples in original, but only later tuple appears in new list
                for i in range(len(orig_ranked)-1):
                    problem += case_2[i] <= (cardinality + 1) * (1 - l[p_star][orig_ranked[i]])
                    problem += case_2[i] <= (cardinality + 1) * l[p_star][orig_ranked[i]] + lpSum(l[p_star][orig_ranked[j]] for j in range(i+1, len(orig_ranked)))
                    problem += case_2[i] >= lpSum(l[p_star][orig_ranked[j]] for j in range(i+1, len(orig_ranked))) - (cardinality + 1) * l[p_star][orig_ranked[i]]
                # Case 3: old tuple missing from new list while new tuple in new list 
                for i in range(len(orig_ranked)):
                    problem += case_3[i] <= (cardinality + 1) * (1 - l[p_star][orig_ranked[i]])
                    problem += case_3[i] <= (cardinality + 1) * l[p_star][orig_ranked[i]] + new_tuples
                    problem += case_3[i] >= new_tuples - (cardinality + 1) * l[p_star][orig_ranked[i]]
                # Case 4: always 0 assuming optimistic (minimal) distance

            # These are lambdas so we don't try to use LP variables we only add for certain distances
            useful_methods = {
                UsefulMethod.QUERY_DISTANCE: lambda: lpSum(1 - lpSum(R_weight[a][v] * Rc[a][v] for v in R[a].keys()) for a in self.conds_attrs(self.categorical())) + lpSum(Nd[self.conds_attrs([predicate]).pop()][type(predicate)] for predicate in self.numerical()),
                UsefulMethod.KENDALL_DISTANCE: lambda: lpSum(i for i in case_2) + lpSum(i for i in case_3),
                UsefulMethod.JACCARD_DISTANCE: lambda: 1 - lpSum((1 if t in orig_ranked else 0) * lc[p_star][t] for t in range(cardinality)),
                UsefulMethod.MAX_ORIGINAL: lambda: -1 * lpSum(l[p_star][t] for t in orig_ranked)
            }

            # Require at least k* tuples in the output
            if opt:
                problem += LpAffineExpression(terms, constant=0) >= p_star
            else:
                problem += LpAffineExpression((l[p_star][t], 1) for t in range(cardinality)) >= p_star

            # Minimize distance, constrain deviation to max
            if debug: print('adding deviation constraint and distance objective')
            problem += fairness >= 0
            problem += fairness <= max_deviation
            problem += useful_methods[useful_method]()

            ### Solve LP & Results ###

            if debug:
                print('writing problem...')
                problem.writeMPS("debug.mps")
            solver = CPLEX_PY()

            print('sending problem to solver...')
            solver_time = timer()

            solution = problem.solve(solver)

            end_time = timer()
            times = (start_time, solver_time, end_time)

            if debug:
                print('LP Status:', LpStatus[solution])

                for i in [i for i in range(cardinality) if s[i].varValue <= cardinality]:
                    print(s[i], s[i].varValue)

            # 1 is feasible, optimal solution
            if solution != 1: return None, times

            prov = {}
            for i in R.keys():
                for j in R[i].keys():
                    if j in NUMERIC_OPS.keys():
                        if prov.get(i):
                            prov[i][NUMERIC_OPS[j]] = R[i][j].varValue
                        else:
                            prov[i] = {NUMERIC_OPS[j]: R[i][j].varValue}
                    elif isinstance(j, str) and R[i][j].varValue > 0:
                        j_ = j.replace("_", " ")
                        if prov.get(i):
                            prov[i].append(j_)
                        else:
                            prov[i] = [j]

            return Refinement(prov), times
        elif method == RefinementMethod.BRUTE:
            print('starting brute')
            start_time = timer()

            p_star = constraints.p_star
            protected = {attr for attr in constraints.attrs()}
            attrs = self.conds_attrs(self.conds())
            relevant_attrs = list(protected.union(attrs))

            # From Python 3 documentation:
            def powerset(iterable):
                s = list(iterable)
                return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

            # Distance setups
            C = defaultdict(list)
            N = defaultdict(int)
            if useful_method == UsefulMethod.QUERY_DISTANCE:
                for cond in self.categorical():
                    attr = [ident for ident in cond.find_all(sqlglot.expressions.Identifier)][0] # There should only be one
                    val = list(filter(lambda x: x.is_string, [v for v in cond.find_all(sqlglot.expressions.Literal)]))
                    C[attr].append(val)
                for predicate in self.numerical():
                    attr = self.conds_attrs([predicate]).pop()
                    constant = float(self.conds_constants([predicate])[0])
                    N[f'{attr} {NUMERIC_OPS[type(predicate)]}'] = constant
            elif useful_method == UsefulMethod.KENDALL_DISTANCE or useful_method == UsefulMethod.MAX_ORIGINAL:
                q = sqlglot.select(*[f'"{s}"' if '.' not in s else f'{s} AS "{s}"' for s in attrs]).from_(self.from_).order_by(self.utility)
                for join in self.joins:
                    q = q.join(join)
                quotedRenamed = " ".join([f'"{attr}"' if '.' in attr and ('"' not in attr and "'" not in attr) and not string_is_float(attr) else attr for attr in self.where.args['this'].sql().split(' ')])
                print(quotedRenamed)
                original = d.sql(
                    sqlglot.subquery(
                        sqlglot.subquery(q).select(
                            'row_number() over () - 1 as r').select("*")
                    ).select('*').where(quotedRenamed).order_by('r').limit(p_star).sql()).fetchnumpy()

            # Get possible values of predicate constants
            R = defaultdict(lambda: defaultdict(lambda: 0))
            for attr in self.conds_attrs(self.categorical()):
                R[f'{attr} IN'] = powerset(self.domain(attr))
            for predicate in self.numerical():
                attr = self.conds_attrs([predicate]).pop()
                R[f'{attr} {NUMERIC_OPS[type(predicate)]}'] = self.domain(attr)

            p = 0
            min_dist = float('inf')
            min_conds = None
            solver_time = timer()
            # Pick possible refinement, check if pruned, then evaluate refinement and check distance & satisfaction
            for i in (dict(zip(R.keys(), a)) for a in product(*R.values())):
                conds = " AND ".join([f'''{k} ({", ".join(f"'{v_}'" for v_ in v)})''' if type(v) == tuple else f'{k} {v}' for k, v in i.items()])

                guaranteedEmpty = False
                for attr in self.conds_attrs(self.numerical()):
                    lb = i.get(f'{attr} >', None) or i.get(f'{attr} >=', None)
                    ub = i.get(f'{attr} <', None) or i.get(f'{attr} <=', None)
                    if lb and ub and lb > ub:
                        guaranteedEmpty = True
                if guaranteedEmpty: continue

                counts = []
                if useful_method == UsefulMethod.KENDALL_DISTANCE or useful_method == UsefulMethod.MAX_ORIGINAL:
                    q = sqlglot.select(*[f'"{s}"' if '.' not in s else f'{s} AS "{s}"' for s in relevant_attrs]).from_(self.from_).order_by(self.utility)
                    for join in self.joins:
                        q = q.join(join)
                    quotedRenamed = " ".join([f'"{attr}"' if '.' in attr and ('"' not in attr and "'" not in attr) and not string_is_float(attr) else attr for attr in conds.split(' ')])
                    result = d.sql(
                        sqlglot.subquery(
                            sqlglot.subquery(q).select(
                                'row_number() over () - 1 as r').select('*')
                        ).select('*').where(quotedRenamed).order_by('r').limit(p_star).sql())
                else:
                    result = d.sql(self.query.where(conds, append=False).limit(p_star).sql())
                tuples = result.fetchnumpy()
                for constraint in constraints:
                    counts.append(len([t for t in tuples[constraint.group.attr if '.' not in constraint.group.attr or useful_method == UsefulMethod.KENDALL_DISTANCE or useful_method == UsefulMethod.MAX_ORIGINAL else constraint.group.attr.split('.')[-1]] if t == constraint.group.val]))

                deviation = 0
                constraint_weight = 1 / len(counts)
                for j in range(len(counts)):
                    deviation += max(constraints[j].cardinalities[0][1] - counts[j], 0) / constraints[j].cardinalities[0][1] * constraint_weight
                
                # Distance calculation
                dist = 0
                if useful_method == UsefulMethod.QUERY_DISTANCE:
                    for attr in self.conds_attrs(self.categorical()):
                        intersection = set(i[f'{attr} IN']).intersection(set(C[attr]))
                        union = set(i[f'{attr} IN']).union(set(C[attr]))
                        dist += 1 - (len(intersection) / len(union))
                    for predicate in self.numerical():
                        attr = self.conds_attrs([predicate]).pop()
                        dist += abs(N[f'{attr} {NUMERIC_OPS[type(predicate)]}'] - i[f'{attr} {NUMERIC_OPS[type(predicate)]}']) / N[f'{attr} {NUMERIC_OPS[type(predicate)]}']
                elif useful_method == UsefulMethod.MAX_ORIGINAL:
                    intersection = len(set(original['r']).intersection(set(tuples['r'])))
                    union = len(tuples['r']) + len(original['r']) - intersection
                    dist = 1 - (intersection/union)
                elif useful_method == UsefulMethod.KENDALL_DISTANCE:
                    union = set(original['r']).union(set(tuples['r']))
                    for (t, t_) in combinations(union, 2):
                        # Case 2
                        if t in original['r'] and t_ in original['r'] and t in tuples['r'] and t_ not in tuples['r'] and t_ < t:
                            dist += 1
                        if t in original['r'] and t_ in original['r'] and t not in tuples['r'] and t_ in tuples['r'] and t < t_:
                            dist += 1
                        # Case 3
                        if t in original['r'] and t_ not in original['r'] and t not in tuples['r'] and t_ in tuples['r']:
                            dist += 1
                        if t not in original['r'] and t_ in original['r'] and t in tuples['r'] and t_ not in tuples['r']:
                            dist += 1

                if dist < min_dist and deviation <= max_deviation:
                    min_dist, min_conds = dist, i
                    print('*\t', conds, counts, '\tdev:', deviation, '\tdist:', dist)

            end_time = timer()
            times = (start_time, solver_time, end_time)

            if not min_conds:
                raise Exception('no refinement found')

            prov = {}
            for attr in self.conds_attrs(self.categorical()):
                prov[attr] = list(min_conds[f'{attr} IN'])
            for predicate in self.numerical():
                attr = self.conds_attrs([predicate]).pop()
                if prov.get(attr):
                    prov[attr][NUMERIC_OPS[type(predicate)]] = min_conds[f'{attr} {NUMERIC_OPS[type(predicate)]}']
                else:
                    prov[attr] = {NUMERIC_OPS[type(predicate)]: min_conds[f'{attr} {NUMERIC_OPS[type(predicate)]}']}

            return Refinement(prov), times
        elif method == RefinementMethod.BRUTE_PROV:
            # TODO: Refactor and combine with above method
            print('starting brute w/ prov')
            start_time = timer()

            p_star = constraints.p_star
            protected = {attr for attr in constraints.attrs()}
            attrs = self.conds_attrs(self.conds())
            relevant_attrs = list(protected.union(attrs))

            # From Python 3 documentation:
            def powerset(iterable):
                s = list(iterable)
                return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

            # Distance setups
            C = defaultdict(list)
            N = defaultdict(int)
            if useful_method == UsefulMethod.QUERY_DISTANCE:
                for predicate in self.categorical():
                    attr = self.conds_attrs([predicate]).pop()
                    val = list(map(lambda x: x.this, list(filter(lambda x: x.is_string, [v for v in predicate.find_all(sqlglot.expressions.Literal)]))))
                    C[attr].append(val[0])
                for predicate in self.numerical():
                    attr = self.conds_attrs([predicate]).pop()
                    constant = float(self.conds_constants([predicate])[0])
                    N[f'{attr} {NUMERIC_OPS[type(predicate)]}'] = constant
            elif useful_method == UsefulMethod.MAX_ORIGINAL or useful_method == UsefulMethod.KENDALL_DISTANCE:
                q = sqlglot.select(*[f'"{s}"' if '.' not in s else f'{s} AS "{s}"' for s in attrs]).from_(self.from_).order_by(self.utility)
                for join in self.joins:
                    q = q.join(join)
                quotedRenamed = " ".join([f'"{attr}"' if '.' in attr and ('"' not in attr and "'" not in attr) and not string_is_float(attr) else attr for attr in self.where.args['this'].sql().split(' ')])
                print(quotedRenamed)
                original = d.sql(
                    sqlglot.subquery(
                        sqlglot.subquery(q).select(
                            'row_number() over () - 1 as r').select("*")
                    ).select('*').where(quotedRenamed).order_by('r').limit(p_star).sql()).fetchnumpy()

            # Capture lineages and add relevant tuples
            # all_ranked = self.all_ranked(opt=False)
            q = sqlglot.select(*[f'"{s}"' if '.' not in s else f'{s} AS "{s}"' for s in relevant_attrs]).from_(self.from_).order_by(self.utility)
            for join in self.joins:
                q = q.join(join)
            all_ranked = {k: v.filled() for k, v in d.sql(
                    sqlglot.subquery(
                        sqlglot.subquery(q).select(
                            'row_number() over () - 1 as r').select('*')
                        ).select('*').sql()
                ).fetchnumpy().items()}
            print('all ranked')
            cardinality = len(all_ranked[list(all_ranked.keys())[0]])

            # all_ranked_tuples = {attr: all_ranked[attr][t] for attr in relevant_attrs + ['r'] for t in range(cardinality)}

            lineages, lineage_tuples = set(), defaultdict(list)
            for t in range(cardinality):
                lineage = Lineage({attr: all_ranked[attr][t] for attr in attrs}, attrs)
                lineages.add(lineage)
                lineage_tuples[lineage].append(all_ranked['r'][t])

            # Get possible values of predicate constants
            R = defaultdict(lambda: defaultdict(lambda: 0))
            for attr in self.conds_attrs(self.categorical()):
                R[f'{attr} IN'] = powerset(self.domain(attr))
            for predicate in self.numerical():
                attr = self.conds_attrs([predicate]).pop()
                R[f'{attr} {NUMERIC_OPS[type(predicate)]}'] = self.domain(attr)

            p = 0
            min_dist = float('inf')
            min_conds = None
            solver_time = timer()
            # Pick possible refinement, check if pruned, then evaluate refinement and check distance & satisfaction
            for i in (dict(zip(R.keys(), a)) for a in product(*R.values())):
                conds = " AND ".join([f'''{k} ({", ".join(f"'{v_}'" for v_ in v)})''' if type(v) == tuple else f'{k} {v}' for k, v in i.items()])

                guaranteedEmpty = False
                for attr in self.conds_attrs(self.numerical()):
                    lb = i.get(f'{attr} >', None) or i.get(f'{attr} >=', None)
                    ub = i.get(f'{attr} <', None) or i.get(f'{attr} <=', None)
                    if lb and ub and lb > ub:
                        guaranteedEmpty = True
                if guaranteedEmpty: continue

                result = []
                for lineage in lineages:
                    #check if match
                    match = True
                    for attr in attrs:
                        if i.get(f'{attr} IN', None) and lineage[attr] not in i.get(f'{attr} IN', None):
                            match = False
                        if i.get(f'{attr} >', None) and lineage[attr] <= i.get(f'{attr} >', None):
                            match = False
                        if i.get(f'{attr} >=', None) and lineage[attr] < i.get(f'{attr} >=', None):
                            match = False
                        if i.get(f'{attr} <', None) and lineage[attr] >= i.get(f'{attr} <', None):
                            match = False
                        if i.get(f'{attr} <=', None) and lineage[attr] > i.get(f'{attr} <=', None):
                            match = False
                    #if match, add to priority queue
                    if match:
                        result.extend(lineage_tuples[lineage])
                        # for t in lineage_tuples[lineage]:
                        #     heapq.heappush(result, (t['r'], t))
                heapq.heapify(result)
                tuples = []
                while len(tuples) < p_star and result:
                    tuples.append(heapq.heappop(result))

                counts = []
                for constraint in constraints:
                    counts.append(len([t for t in tuples if all_ranked[constraint.group.attr][t] == constraint.group.val]))
                deviation = 0
                constraint_weight = 1 / len(counts)
                for j in range(len(counts)):
                    deviation += max(constraints[j].cardinalities[0][1] - counts[j], 0) / constraints[j].cardinalities[0][1] * constraint_weight

                # Distance calculation
                dist = 0
                if useful_method == UsefulMethod.QUERY_DISTANCE:
                    for attr in self.conds_attrs(self.categorical()):
                        intersection = set(i[f'{attr} IN']).intersection(C[attr])
                        union = set(i[f'{attr} IN']).union(C[attr])
                        dist += 1 - (len(intersection) / len(union))
                    for predicate in self.numerical():
                        attr = self.conds_attrs([predicate]).pop()
                        dist += abs(N[f'{attr} {NUMERIC_OPS[type(predicate)]}'] - i[f'{attr} {NUMERIC_OPS[type(predicate)]}']) / N[f'{attr} {NUMERIC_OPS[type(predicate)]}']
                elif useful_method == UsefulMethod.MAX_ORIGINAL:
                    intersection = len(set(tuples).intersection(set(original['r'])))
                    union = len(tuples) + len(original) - intersection
                    dist = 1 - (intersection/union)
                elif useful_method == UsefulMethod.KENDALL_DISTANCE:
                    union = set(original['r']).union(set(tuples))
                    for (t, t_) in combinations(union, 2):
                        # Case 2
                        if t in original['r'] and t_ in original['r'] and t in tuples and t_ not in tuples and t_ < t:
                            dist += 1
                        if t in original['r'] and t_ in original['r'] and t not in tuples and t_ in tuples and t < t_:
                            dist += 1
                        # Case 3
                        if t in original['r'] and t_ not in original['r'] and t not in tuples and t_ in tuples:
                            dist += 1
                        if t not in original['r'] and t_ in original['r'] and t in tuples and t_ not in tuples:
                            dist += 1

                if dist < min_dist and deviation <= max_deviation:
                    min_dist, min_conds = dist, i
                    print('*\t', conds, counts, '\tdev:', deviation, '\tdist:', dist)

            end_time = timer()
            times = (start_time, solver_time, end_time)

            if not min_conds:
                raise Exception('no refinement found')

            prov = {}
            for attr in self.conds_attrs(self.categorical()):
                prov[attr] = list(min_conds[f'{attr} IN'])
            for predicate in self.numerical():
                attr = self.conds_attrs([predicate]).pop()
                if prov.get(attr):
                    prov[attr][NUMERIC_OPS[type(predicate)]] = min_conds[f'{attr} {NUMERIC_OPS[type(predicate)]}']
                else:
                    prov[attr] = {NUMERIC_OPS[type(predicate)]: min_conds[f'{attr} {NUMERIC_OPS[type(predicate)]}']}

            return Refinement(prov), times
if __name__ == '__main__':
    # Astronauts

    # constraints = Constraints(
    #     Constraint(Group("Gender", "Female"), (10, 5)),
    #     # Constraint(Group("Gender", "Male"), (10, 5), sense='U'),
    # )

    # ranking = Ranking(
    #     'SELECT * FROM "data/astronauts.csv" WHERE "Graduate Major" = \'Physics\' AND "Space Walks" >= 1 AND "Space Walks" <= 3 ORDER BY "Space Flight (hr)" DESC')

    # Vertex Cover

    # constraints = Constraints(
    #     Constraint(Group("Edge", "1"), (14, 1)),
    #     Constraint(Group("Edge", "2"), (14, 1)),
    #     Constraint(Group("Edge", "3"), (14, 1)),
    #     Constraint(Group("Edge", "4"), (14, 1)),
    #     Constraint(Group("Edge", "5"), (14, 1)),
    #     Constraint(Group("Edge", "6"), (14, 1)),
    #     Constraint(Group("Edge", "7"), (14, 1)),
    # )

    # ranking = Ranking(
    #     'SELECT * FROM "data/graph.csv" WHERE "Vertex" = \'x\' ORDER BY Edge ASC')

    # Candidates (running example)

    constraints = Constraints(
        Constraint(Group("Gender", "F"), (4, 2)),
        Constraint(Group("Gender", "M"), (4, 2)),
    )

    ranking = Ranking(
        'SELECT * FROM "data/candidates.csv" WHERE ("Major" = \'CS\' OR Major = \'EE\') AND "Hours" >= 90 AND "Hours" <= 100 ORDER BY "Gpa" DESC')

    # Law Students
    
    # constraints = Constraints(
    #     # Constraint(Group("race", "Black"), (20, 3)),
    #     Constraint(Group("sex", 1), (10, 5)),
    # )

    # ranking = Ranking(
    #     'SELECT * FROM "data/law_students.csv" WHERE (region_first = \'GL\' OR region_first = \'NW\') AND "UGPA" <= 4.0 AND "UGPA" >= 3.5 ORDER BY "LSAT" DESC')

    # MEPS

    # constraints = Constraints(
    #     Constraint(Group("SEX", "1"), (50, 25)),
    # )

    # ranking = Ranking(
    #     'SELECT * FROM "data/meps.csv" WHERE AGE16X >= 25 AND FAMS1231 >= 4 ORDER BY rank')

    # TPC-H
    
    # constraints = Constraints(
    #         Constraint(Group("o.ORDERPRIORITY", "5-LOW"), (10, 5)),
    #     )
    
    # ranking = Ranking('''SELECT c.*, o.*, l.*, s.*, n.*, re.* FROM "data/TPCH/SCALE-1/10/customer.csv" AS c JOIN "data/TPCH/SCALE-1/10/orders.csv" AS o ON o.CUSTKEY = c.CUSTKEY JOIN "data/TPCH/SCALE-1/10/lineitem.csv" AS l ON l.ORDERKEY = o.ORDERKEY JOIN "data/TPCH/SCALE-1/10/supplier.csv" AS s ON s.SUPPKEY = l.SUPPKEY JOIN "data/TPCH/SCALE-1/10/nation.csv" AS n ON n.NATIONKEY = s.NATIONKEY JOIN "data/TPCH/SCALE-1/10/region.csv" AS re ON re.REGIONKEY = n.REGIONKEY WHERE re.NAME = 'ASIA' ORDER BY l.REVENUE1 DESC''')

    refinement, times = ranking.refine(constraints, only_lower_bound_card_constraints=True, max_deviation=0.5, debug=True, method=RefinementMethod.MILP_OPT, useful_method=UsefulMethod.QUERY_DISTANCE)
    print(refinement.conditions)