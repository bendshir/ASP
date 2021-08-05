from ac3 import CSPSolver

# Adds a interactive layer above csp_ac3.py to visually show the ac-3 algorithm
# Go to next step in the ac-3 algorithm by hitting the enter key


# Show the heading row
def show_head_row():
    print("Edge    | New Domain     | Edges to Reconsider")
    print("--------|----------------|--------------------")


# Display a single row of ac-3
def show_row(edge, xi, new_domain, edges_to_reconsider):
    print(str(edge) + "  |  " + str(xi) + "=" + str(new_domain) + "  |  " + str(edges_to_reconsider))


# solve the given CSP and print the results from the generated solve funcion
def show_solver(arcs, domains, constraints):
    solver = CSPSolver(arcs, domains, constraints)
    result = solver.solve(True)  # True indicates that we are using the method as a generator

    for step in result:
        # continue_input = input()  # continue with the function generator only on user input (ex: enter key)

        if step == None:  # if one of the domains is empty, solve_helper yield None
            # found an inconsistency
            print("Inconsistent!. No solution possible.")
        else:
            edge = step[0]

            if edge is None:
                # reached the final result
                final_domain = step[1]
                print("Result:", final_domain)
            else:
                xi = edge[0]
                new_domain = step[1][xi]
                edges_to_reconsider = step[2]
                show_row(edge, xi, new_domain, edges_to_reconsider)


if __name__ == "__main__":
    show_head_row()

    # arcs, domains, and constraints
    arcs = [('a', 'b'), ('b', 'a'), ('b', 'c'), ('c', 'b'), ('c', 'a'), ('a', 'c')]

    domains = {
        'a': [2, 3, 4, 5, 6, 7,10,11],
        'b': [4, 5, 6, 7, 8, 9,20,11,12],
        'c': [1, 2, 3,  5, 10,11]
    }

    # constraints:
    # b = 2*a
    # a = c

    # b >= c - 2
    # b <= c + 2
    constraints = {
        ('a', 'b'): lambda a, b: a * 2 == b,
        ('b', 'a'): lambda b, a: b == 2 * a,
        ('a', 'c'): lambda a, c: a == c,
        ('c', 'a'): lambda c, a: c == a,
        ('b', 'c'): lambda b, c: b >= c - 2,
        ('b', 'c'): lambda b, c: b <= c + 2,
        ('c', 'b'): lambda c, b: b >= c - 2,
        ('c', 'b'): lambda c, b: b <= c + 2
    }

    show_solver(arcs, domains, constraints)


# example:
# a<b<c
# d< e
# Y > a,b,c,d,e
arcs = [('a', 'b'), ('b', 'a'), ('b', 'c'), ('c', 'b'), ('d', 'e'), ('e', 'd'), ('y', 'a'), ('y', 'b'), ('y', 'c'),
        ('a', 'y'), ('b', 'y'), ('c', 'y'), ('d', 'y'), ('e', 'y')]

domains = {
        'a': [1,2,3,4,5,6],
        'b': [1,2,3,4,5,6],
        'c':[1,2,3,4,5,6],
        'd': [1, 2, 3, 4, 5, 6],
        'e': [1, 2, 3, 4, 5, 6],
        'y': [1, 2, 3, 4, 5, 6]
}


constraints = {
        ('a', 'b'): lambda a, b: a < b,
        ('b', 'a'): lambda b, a: b > a,

        ('b', 'c'): lambda b, c: b < c,
        ('c', 'b'): lambda c, b: c > b,

        ('d', 'e'): lambda d, e: d < e,
        ('e', 'd'): lambda e, d: e > d,

        ('y', 'a'): lambda y, a: y > a,
        ('y', 'b'): lambda y, b: y > b,
        ('y', 'c'): lambda y, c: y > c,
        ('y', 'a'): lambda y, d: y > d,
        ('y', 'a'): lambda y, e: y > e,

        ('a', 'y'): lambda a, y: a < y,
        ('b', 'y'): lambda b, y: b < y,
        ('c', 'y'): lambda c, y: c < y,
        ('d', 'y'): lambda d, y: d < y,
        ('e', 'y'): lambda e, y: e < y,

}

print(constraints.keys())
ao_set = ['a', 'b', 'c', 'd', 'e', 'y']
solver = CSPSolver(arcs, domains, constraints, ao_set)  # solve the given CSP
new_chromosome = solver.solve()