import queue
import random

from BackTrack import BackTrack


class CSPSolver:
    worklist = queue.Queue()  # a queue of arcs (this can be a queue or set in ac-3)

    # arcs: list of tuples
    # domains: dict of { tuples: list }
    # constraints: dict of { tuples: list }
    def __init__(self, arcs, domains, constraints, ao_set):
        self.arcs = arcs  # [(a1,a2), (a2,a1)...]
        self.domains = domains  # { a1: [0,...len(ao_set)], a2: [0,...len(ao_set)] }
        self.constraints = constraints  # {(a1,a2) : lambda ...}
        self.ao_set = ao_set
        """ Domains contain all the operation in ao_set """

    # returns an empty dict if an inconsistency is found and domains for variables otherwise
    # generate: bool (choose whether or not to use a generator)
    def solve(self):
        result = self.solve_helper()
        if result is None:  # if one of the domains is empty, solve_helper yield None
            return None
        if result[0] is None:  # the result row
            """ Find placement for the operations """
            b = BackTrack(domains=self.domains, constraints=self.constraints)
            new_chromo = b.find_sequence()
            return new_chromo

    # returns a generator for each step in the algorithm, including the end result
    # each yield is a tuple containing: (edge, new domains, edges to consider)
    def solve_helper(self):
        # setup queue with given arcs
        [self.worklist.put(arc) for arc in self.arcs]

        # continue working while worklist is not empty
        while not self.worklist.empty():
            (xi, xj) = self.worklist.get()  # get 2 AOs that has a constraint between them
            if self.revise(xi, xj):  # if true - we removed domain from xi domains.
                if len(self.domains[xi]) == 0:
                    # found an inconsistency - There isn't a solution.
                    return None
                # get all of xi's neighbors - when xi is in right size in the arc (constraint).
                neighbors = [neighbor for neighbor in self.arcs if neighbor[1] == xi]

                # put all neighbors into the worklist to be evaluated
                [self.worklist.put(neighbor) for neighbor in neighbors]

            """ relevant if we want to see the all steps of the result"""
            #     yield (xi, xj), self.domains, neighbors
            # else:
            #     yield (xi, xj), self.domains, None

        # yield the final return value
        return None, self.domains, None

    # returns true if and only if the given domain i
    def revise(self, xi, xj):  # There is a constraint between xi, xj.
        revised = False
        # get the domains for xi and xj
        xi_domain = self.domains[xi]
        xj_domain = self.domains[xj]

        # get a list of constraints for (xi, xj)
        # self.constraints is a dict, dict[0] - get the key of the fist item in the dict
        # item = (a,b), item[0] = a.
        # constraint = (a1, a2).  constraint[0] = a1
        # constraints = [constraint for constraint in self.constraints if constraint[0] == xi and constraint[1] == xj]

        for x in xi_domain[:]:
            satisfies = False  # there is a value in xjDomain that satisfies the constraint(s) between xi and xj
            for y in xj_domain:
                # for constraint in constraints:  # run over keys: (a,b)
                #     check_function = self.constraints[constraint]  # the lambda of the constraint (value of dict)
                check_function = self.constraints[(xi, xj)]  # the lambda of the constraint (value of dict)
                # check y against x for each constraint
                if check_function(x, y):
                    satisfies = True
                    break

            if not satisfies:
                # delete x from xiDomain because there are not a value in xj_domain that satisfies it.
                xi_domain.remove(x)
                revised = True

        return revised
