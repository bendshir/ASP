import ast
import statistics
import mysql.connector
import random
import time
import itertools
from time import localtime, strftime
from termcolor import colored
import pandas as pd
import os
from Assembly_operation import AO
from Chromosome import Chromosome
from ac3 import CSPSolver


"""
Model assumptions:
1.  Assembly operation is generic. The number of assembly operations that will be generated for each id, 
    as the number of combinations after spreading all the options between the actors.
2.  Length of sequence is equal to number of interactions in the process.
3.  For each AO could be only one proximity constraint - ao that need to be located exactly one place before him.
    if ao1 has ao2 in his proximity constraint -> ao1 = ao2+1.
4.  very important! proximity cancelled priority! do not add proximity and priority to the same interaction! leave only
    proximity
    {"id": 5, "con_type": "pih", "priority": [3], "materials": ["hose_1", "connector_2"], "proximity": [3]} - No
    {"id": 5, "con_type": "pih",  "materials": ["hose_1", "connector_2"], "proximity": [3]} - Yes
"""


def calc_space_len(msg):
    msg_len = len(msg)
    half_space = int((89 - msg_len) / 2)
    return half_space


def print_time_line_sep(msg):
    """
    :param msg: massage to print
    print len sep with current date time.
    """
    dt_fmt = "%d/%m/%Y %H:%M:%S"
    space_len = calc_space_len(msg) + 2
    line_msg = " " * space_len + msg
    line_sep = "-" * 35 + " " + strftime(dt_fmt, localtime()) + " " + "-" * 35 + '\n'
    print(line_msg)
    print(line_sep)


def print_end_msg(start_time, end_time):
    """
    print the time - the total time of all the assignment
    :param start_time: read the time at the beginning of the program
    :param end_time: read the time at the end of the program
    """
    minutes, seconds = divmod(end_time - start_time, 60)
    time_msg = "{:0>2}:{:0>2}".format(int(minutes), int(seconds))
    msg = f"The total running time was {time_msg} (mm:ss)"
    print('\n' + msg)


def prGreen(skk): print("\033[92m {}\033[00m".format(skk))


def prRed(skk): print("\033[91m {}\033[00m".format(skk))


def find_variant_num(index):
    """
    get an index of location of the (product, wci) in product_wci list.
    :param index: location of (product, wci)
    :return: number of variant.
    """
    if index <= 2:
        return index + 1
    elif index <= 5:
        return index - 2
    else:
        return index - 5


def select_similar_products(product_name):
    """
    :param product_name: product name
    :return: list of similar product
    """
    product_name = product_name[:-1]
    query = """select process_name from sequences where SUBSTRING(process_name FROM 1 FOR 
    CHAR_LENGTH(process_name) - 1) = %s """
    cursorObject.execute(query, (product_name,))
    result = list(set([value for value, in cursorObject.fetchall()]))
    return result


def find_parent(probability):
    """
    find parent to crossover
    :param probability: list of probabilities to be chosen
    :return: index of the chosen parent
    """
    pick_num = random.uniform(0, 1)
    summed_number = 0
    for p in range(len(probability)):
        summed_number += probability[p]
        if pick_num < summed_number:
            if pick_num > summed_number - probability[p]:
                return p


def get_ao_material_type(a):
    """
    Got an assembly operation, return list of the material types.
    including duplicates
    :param a:  assembly operation
    :return: list
    """
    ao_types = []  # materials type of this AO
    query = """select material_type,quantity from ao_materials where assembly_operation_id = %s """
    cursorObject.execute(query, (a,))
    result = cursorObject.fetchall()
    for r in result:
        ao_types += r[1] * [r[0]]  # r[1] - quantity , r[0] - the material type
    return ao_types


def get_ao_actor_type(a):
    """
    Got an assembly operation, return list of the actors types.
    including duplicates
    :param a:  assembly operation
    :return: list
    """

    query = """select actor_type from ao_actors where assembly_operation_id = %s """
    cursorObject.execute(query, (a,))
    ao_types = [value for value, in cursorObject.fetchall()]

    return ao_types


def random_seq(ao_set):
    """
    Get set of assembly operation.
    Find random order and check the priority constraints
    :param ao_set: list contains AOs type.
    :return: a sequence or None.
    """
    random.shuffle(ao_set)  # random order of operations.
    if check_priority_constraint(ao_set):  # True - the chromosome meets the priority constraints.
        if check_proximity_constraint(ao_set):
            return ao_set
        else:
            return None
    else:
        return None


def set_similar_sequences(similar_products):
    """
    For each product name in the similar_products list, get all their sequences in the DB.
    Find for each operation the connection type.
    :param similar_products: names of similar products
    :return: list of similar sequences. nested list. return only the connection type!!!
    """
    seqs_ids = []
    sequences = []
    for n in similar_products:  # n - name of product
        query = """SELECT sequence_id FROM sequences WHERE process_name = %s"""
        cursorObject.execute(query, (n,))
        seqs_ids.append(value for value, in cursorObject.fetchall())  # append the seqs ids into the seqs_ids list.
    seqs_ids = [value for sublist in seqs_ids for value in sublist]
    for s in seqs_ids:  # s - seq id
        query = """SELECT a.connection_type FROM sequences_operations as s inner join 
        assembly_operations as a on s.assembly_operation_id = a.assembly_operation_id WHERE sequence_id = %s """
        cursorObject.execute(query, (s,))
        seq = [value for value, in cursorObject.fetchall()]
        sequences.append(seq)
    if len(sequences) == 0:
        print(colored("Cant find sequences for this process, try different process as LCS measure ", 'red'))
        exit()

    return sequences


def get_materials(inter):
    """
    get an interaction return materials types and ids of this interaction.
    :param inter: interaction field (only) in the process_interactions table.
    :return: list of materials types, list of materials ids
    """
    materials_ids = inter['materials']
    in_params = ','.join(['%s'] * len(materials_ids))
    q = " select material_type from materials where material_id IN (%s) " % in_params
    cursorObject.execute(q, materials_ids)
    materials_types = [value for value, in cursorObject.fetchall()]
    if len(materials_ids) != len(materials_types):
        print(colored("Got an problem: :", 'red'))
        print(colored("No material type to at least one of the materials ids, interaction number: " + str(inter['id'])
                      + ".  Check for spelling mistakes.", 'red'))
        exit()

    return materials_types, materials_ids


def ao_by_conn_type(conn_type):
    """
    Get a connection type of interaction, return list of assembly operations of this interaction.
    """
    query = """select assembly_operation_id from assembly_operations where connection_type = %s"""
    cursorObject.execute(query, (conn_type,))
    ao = [value for value, in cursorObject.fetchall()]
    return ao


def ao_by_materials_types(ao, inter_materials_types, inter_dict):
    """
    Find suitable assembly operations, base on materials type. Each assembly need to contain the same materials types
    and their quantity as the interaction.
    :param ao:  <list> of assembly operations according to connection type.
    :param inter_materials_types: materials types of the interaction. with duplicates.
    :param inter_dict: Json field from process_interactions table <dict>
    :return: list of assembly operations.
    """
    next_level_aos = []
    for a in ao:  # for each assembly operation
        ao_types = []  # materials type of this ao
        query = """select material_type,quantity from ao_materials where assembly_operation_id = %s """
        cursorObject.execute(query, (a,))
        result = cursorObject.fetchall()
        for r in result:
            ao_types += r[1] * [r[0]]  # r[1] - quantity , r[0] - the material type
        if sorted(inter_materials_types) == sorted(ao_types):
            next_level_aos.append(a)
    if len(next_level_aos) == 0:  # no appropriate ao for this interaction
        print(colored("No suitable assembly operation for :", 'red'))
        print(colored("Interaction number:" + str(inter_dict['id']) + "  can't find operation with this materials "
                                                                      "types", 'red'))
        exit()
    else:
        return next_level_aos


def set_priority_constraints(a_after, a_before):
    """
    Add constraints to specific assembly operation.
    :param a_after: assembly operation that need to be after.
    :param a_before: assembly operation that need to be before.
    """
    if (a_after, a_before) not in a_after.constraints:  # prevent duplicates
        a_after.constraints[(a_after, a_before)] = lambda a_af, a_b: a_af > a_b
        a_before.constraints[(a_before, a_after)] = lambda a_b, a_af: a_b < a_af


def set_proximity_constraints(a_after, a_before):
    """
    Add constraints to specific assembly operation.
    :param a_after: assembly operation that need to be after. (localized in x+1)
    :param a_before: assembly operation that need to be before. (localized in x)
    """
    if (a_after, a_before) not in a_after.constraints:  # prevent duplicates
        a_after.constraints[(a_after, a_before)] = lambda a_af, a_b: a_af == a_b + 1
        a_before.constraints[(a_before, a_after)] = lambda a_b, a_af: a_b + 1 == a_af


def check_priority_constraint(c):
    """
    check priority constraints
    :param c: candidate chromosome < type : list of assembly operations >
    :return: True - the chromosome meets the priority constraints.
    """
    for i in range(len(c)):
        a1 = c[i]  # a1 = assembly operation
        if a1.priority is not None:  # a1 have priority constraints
            if i == 0:  # it cannot be that the first ao in the sequence has priority ao
                return False
            # need to go through all his priority and check that they are met.
            for inter in a1.priority:  # inter = interaction id that have to come before a1 operation.
                for j in range(0, i):
                    if c[j].interaction_id == inter:  # found operation that proves the constraint
                        break
                    if j == i - 1:  # does not meet the constraint
                        return False
    return True


def check_proximity_constraint(c):
    """
      check proximity constraints
      :param c: candidate chromosome < type : list of assembly operations >
      :return: True - the chromosome meets the proximity constraints.
      """
    for e in range(len(c)):
        a1 = c[e]  # a1 = assembly operation
        if a1.proximity is not None:  # a1 have proximity constraints - only 1 constraint!
            if e == 0:  # it can't be that the first ao in the sequence has proximity ao - ao that need to be before him
                return False
            if c[e - 1].interaction_id not in a1.proximity:
                return False
    return True


def set_num_interactions(process_interactions):
    """
    Get process_interactions table -> set the number of interactions_ids in this process
    :return: interactions_ids <list> of interactions ids.
    """
    ids = []
    for row in process_interactions:
        if row[2] == 'init' or row[2] == 'end':
            continue
        else:
            ids.append(int(row[1]))
    return sorted(ids)


def select_set_operations(interactions_dict_AOs):
    """
    select a set of operations for the sequence. Does not specify order.
    :param interactions_dict_AOs: assembly operations into dict according their interactions ids.
    :return: <list>
    """
    set_operations = []
    for key, value in interactions_dict_AOs.items():
        ao = random.sample(value, 1)
        set_operations.append(ao)
    set_operations = [item for sublist in set_operations for item in sublist]  # flat list
    return set_operations


def find_operations_with_material(m_id, list_of_aos):
    """
    Get a material id, return all operations with this material from the given list (can be from self.AOs)
    """
    return_list = []
    for a in list_of_aos:
        if m_id in a.materials:
            return_list.append(a)
    return return_list


def check_fitness_input(fitness_type):
    """
    check that the weight of the fitness function sum to 1.
    :param fitness_type: list : [use threshold? , time_weight, lcs_weight].
    :return: fitness_type
    """
    if fitness_type[1] + fitness_type[2] != 1:
        while fitness_type[1] + fitness_type[2] != 1:
            print("check 1")
            print(fitness_type[1] + fitness_type[2])
            fitness_type[1] = float(input("The weight of the fitness function, does not sum to 1.\n"
                                          " Please enter duration weight:"))
            print(fitness_type[1])
            fitness_type[2] = float(input(" Please enter lcs weight:"))
            print(fitness_type[2])
    return fitness_type


class GA(object):
    def __init__(self, population_size, mutation_rate, crossover_rate, termination_condition, threshold_value,
                 num_final_chromosomes, use_csp, process_name, work_cell, similar_products, start_time, fitness_type,
                 constraints_percentage):
        """ Initialize GA parameters """
        self.process_name = process_name
        self.work_cell = work_cell
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.termination_condition = termination_condition
        self.threshold_value = threshold_value
        self.use_csp = use_csp  # bool
        self.chromosomes = []  # < type: Chromosome >
        self.num_final_chromosomes = num_final_chromosomes
        self.best_chromosome = None
        self.best_value_fitness = 0
        self.AOs = []  # < type: AO > duplicate the names with actors ids and materials ids.
        self.counter_round = 0
        self.domain_code = self.set_domain()
        self.process_materials = self.set_materialsID()  # list: materials id of this process
        self.materials_priorities = self.set_materials_prior()  # list of tuples (material_prior, material_post)
        self.dict_actors = self.organize_actorsID_into_type()
        self.wci_rules = self.set_wci_rules()
        self.similar_sequences = set_similar_sequences(similar_products)  # nested list of connections types
        self.interactions_ids = []  # without init and end interactions. sorted list.
        self.total_time = 10 * 60  # 10 minutes
        self.start_time = start_time
        self.runtime = lambda current_time: current_time - self.start_time < self.total_time
        self.fitness_type = check_fitness_input(fitness_type)  # list : [use threshold? , time_weight, lcs_weight].
        self.constraints_percentage = constraints_percentage / 100  # Percentage of constraints to include in all AOs.

    def set_domain(self):
        # find domain code from process name
        query = """SELECT domain_code FROM process_details WHERE process_name = %s"""
        cursorObject.execute(query, (self.process_name,))
        result = cursorObject.fetchall()
        return result[0][0]

    def set_wci_rules(self):
        # find work cell id rules - the connections between the actors ids.
        # return - tuples of actors id that have to connect.
        query = """SELECT equipment_id, connection_rule FROM work_cells WHERE work_cell_id = %s
        and connection_rule is not null"""
        cursorObject.execute(query, (self.work_cell,))
        rules = cursorObject.fetchall()
        return rules

    def organize_actorsID_into_type(self):
        """
        organize work cell actors type to actors id.
        :return: m_dict: { actor_type1 : [ actor_id1, actor_id2],actor_type2 : [ actor_id1, actor_id2] }
        """
        # find work_cell_id actors type
        query = """ select equipment.equipment_id, equipment_type from work_cells inner join equipment on 
        work_cells.equipment_id = equipment.equipment_id where work_cells.work_cell_id = %s"""
        cursorObject.execute(query, (self.work_cell,))
        m_dict = {}
        actors = cursorObject.fetchall()
        for actor_id, actor_type in actors:  # for each actor type in the work cell
            if actor_type not in m_dict.keys():
                m_dict[actor_type] = [actor_id]
            else:  # this key (type) already exist in the dict
                m_dict[actor_type].append(actor_id)
        return m_dict

    def set_materialsID(self):
        # find the materials ids for the process name
        query = """ select material_id from process_details inner join process_materials on 
                process_details.process_materials = process_materials.group_mtr 
                where process_details.process_name = %s """
        cursorObject.execute(query, (self.process_name,))
        return [value for value, in cursorObject.fetchall()]

    def set_materials_prior(self):
        """
        Set materials priorities constraints from process_materials_priorities table.
        :return: list of tuples (material_prior, material_post) or None
        """
        query = """ select material_id_prior, material_id_post  from process_materials_priorities inner join
         process_details on process_details.process_materials = process_materials_priorities.group_mtr 
                        where process_details.process_name = %s """
        cursorObject.execute(query, (self.process_name,))
        prior_list = cursorObject.fetchall()
        if len(prior_list) == 0:  # No materials priorities constraints in this process
            prior_list = None
        return prior_list

    def remove_un_possible_connections(self, actors_combinations):
        """
        Remove combinations of actors that can not connect.
        For each rule in self.wci_rules, if one of the actors appear in the combination the second actor have to appear
        too.
        :param actors_combinations: all combination of actors id for a specific ao
        :return: only possible combination according to the wci rules.
        """
        final_comb = actors_combinations
        for r in self.wci_rules:  # tuple of two actors ids
            for c in actors_combinations:  # combinations of actors ids
                if r[0] in c and r[1] not in c:
                    final_comb.remove(c)
                if r[1] in c and r[0] not in c:
                    final_comb.remove(c)
        return final_comb

    def ao_by_actors(self, ao, inter_dict):
        """
        find ao according to the actors exist in the work cell.
        Check for each type that if this type of actor appear in this ao X times, the work cell have X
        actors id in this type.
        :param inter_dict: JSON interaction to dict.
        :param ao: <list> of assembly operations.
        :return: <list> of assembly operations.
        """
        final_aos = []
        for a in ao:
            query = """ select actor_type from ao_actors where assembly_operation_id = %s """
            cursorObject.execute(query, (a,))
            actors_types = [value for value, in cursorObject.fetchall()]
            for r in actors_types:  # r = actor type
                quantity = actors_types.count(r)  # count how much times this type needed in the ao
                actor_type = r
                if actor_type in self.dict_actors:  # if this actor type in the work cell
                    if not len(self.dict_actors[actor_type]) >= quantity:
                        # if list of actors id is not bigger or equal to quantity of type.
                        break
                else:
                    break
            else:  # the else suite is executed after the for, but only if the for terminates normally (not by a break).
                final_aos.append(a)
        if len(final_aos) == 0:  # no appropriate ao that can occur in this work cell.
            prGreen("No suitable assembly operation for this work cell:")
            print("Interaction number:", inter_dict['id'], "can't find operation with this materials types and exists"
                                                           " actors")
            exit()
        else:
            return final_aos

    def generate_AOs(self, a_name, inter_materials_ids, ao_actors_types, connection_type, inter_dict):
        """
        Generate AOs objects
        :param a_name: assembly operation id
        :param inter_materials_ids: materials ids of this ao
        :param ao_actors_types: actors types of this ao
        :param connection_type: of this ao
        :param inter_dict: Json field from process_interactions table <dict>
        """
        # -------- Combination of actors id ----------
        filter_dict_a = {i: self.dict_actors[filter_key] for i, filter_key in enumerate(ao_actors_types)}
        all_combination_actors = [p for p in itertools.product(*filter_dict_a.values()) if len(set(p)) == len(p)]
        all_combination_actors = list(set(tuple(sorted(sub)) for sub in all_combination_actors))
        # in all_combination_actors we should remove not possible combinations according to the connections in the wci.
        all_combination_actors = self.remove_un_possible_connections(all_combination_actors)

        # -------- Generate ----------:
        for z in range(len(all_combination_actors)):
            ao = AO(a_id=a_name, materials=inter_materials_ids, actors=all_combination_actors[z],
                    connection_type=connection_type, inter_dict=inter_dict)
            self.AOs.append(ao)

    def find_assembly_operations(self):
        """
        Find suitable assembly operations base on:
        1 - connection type
        2 - materials types fit materials ids of interactions_ids
        3 - actors in the work cell.
        """
        print_time_line_sep("find suitable assembly operations")
        q = """ select * from process_interactions where process_name = %s"""
        cursorObject.execute(q, (self.process_name,))
        process_interactions = cursorObject.fetchall()
        if len(process_interactions) == 0:
            print(colored(" No interactions for this process name: " + self.process_name, 'red'))
            exit()
        self.interactions_ids = set_num_interactions(process_interactions)
        for inter in process_interactions:  # inter = row in the table
            # 1: find suitable AOs base on connection type.
            connection_type = inter[2]
            ao = ao_by_conn_type(connection_type)  # inter[2] = connection_type
            # 2: base on materials types.
            inter_dict = ast.literal_eval(inter[-1])  # turn JSON interaction to dict.
            inter_materials_types, inter_materials_ids = get_materials(inter_dict)
            ao = ao_by_materials_types(ao, inter_materials_types, inter_dict)
            # 3: base on actors in the chosen work cell.
            final_ao = self.ao_by_actors(ao, inter_dict)
            # 4: generate aos.
            for a in final_ao:
                ao_actors_types = get_ao_actor_type(a)
                self.generate_AOs(a, inter_materials_ids, ao_actors_types, connection_type, inter_dict)

    def check_set_interactions(self, c):
        """
        check if all the interactions_ids of this process are in the candidate chromosome (c).
        :param c: candidate chromosome < type: list >.
        :return:is the condition occur <type: boolean >.
        """
        c_interactions = []  # the interactions in this chromosome
        for gen in c:  # for each gen in this AO, except init and end operations.
            c_interactions.append(gen.interaction_id)
        # check if c_interactions contains all the items from the interactions ids:
        feasible = all(elem in c_interactions for elem in self.interactions_ids)
        if feasible:
            return True
        else:
            return False

    def isDuplicates(self, c):
        """
        Check if the chromosome is already exist in self.chromosomes (condition to get in the population)
        :param c: candidate chromosome < type: list >
        :return: True - if chromosome already exist < type: boolean >
        """
        for chromosome in self.chromosomes:
            if c == chromosome.gens:
                return True
        return False

    def find_init_end(self):
        """
        separate init and end operations.
        REMOVE init and end operation from self.AOs
        :return: init_ao, end_ao
        """
        init, end = [], []
        AOs = []
        for a in self.AOs:
            if 'INIT' in a.a_id:
                init.append(a)
            elif 'END' in a.a_id:
                end.append(a)
            else:
                AOs.append(a)
        self.AOs = AOs
        if len(init) == 1 and len(end) == 1:
            return init[0], end[0]
        else:  # need to decide on the init and end operations.
            # The operation with the biggest number of actors will be selected.
            init.sort(key=lambda o: len(o.actors), reverse=True)  # sort from big to small
            end.sort(key=lambda o: len(o.actors), reverse=True)  # sort from big to small
            return init[0], end[0]

    def find_constraint_between_aos(self, a1, con_interactions_list, constraint_func):
        """
        Get an ao with constraint with type: constraint_type. Find AOs that includes in his constraint, and set
        the values.
        :param a1: assembly operation
        :param con_interactions_list: a1.priority or a1.proximity.
        :param constraint_func: according to constraint_type, the function to use to set the constraints.
        """
        for i2 in range(len(self.AOs)):
            a2 = self.AOs[i2]
            if a1 == a2:
                continue
            elif a2.interaction_id in con_interactions_list:
                # priority constraint between them - a2 before a1 -> a2 < a1.
                #  OR proximity constraint between them - a2 before a1 -> a2+1 = a1.
                n = random.uniform(0, 1)
                if n < self.constraints_percentage:
                    # limited the number of constraint included in the problem
                    constraint_func(a1, a2)

    def get_constraints(self):
        """
        Prepare the data for the  CSP problem
        Update AO.constraints. Which AO should be before another.
        base on priority constraint from interaction and materials priority constraints.
        and base on proximity constraints. proximity means - 2 operations one after the other.
        """
        # -------- priority constraint from materials --------
        # update a.priority (between interactions)  base on materials priorities
        if self.materials_priorities is not None:  # There are materials priorities constraints
            for m_prior, m_post in self.materials_priorities:
                m_prior_list = find_operations_with_material(m_prior, self.AOs)
                m_post_list = find_operations_with_material(m_post, self.AOs)
                for a1 in m_prior_list:
                    for a2 in m_post_list:
                        if a1.interaction_id == a2.interaction_id:
                            continue
                        elif a2.priority is None:
                            a2.priority = [a1.interaction_id]
                        elif a1.interaction_id not in a2.priority:
                            a2.priority.append(a1.interaction_id)

        """-------- set priority and proximity constraint from interaction --------"""

        for i1 in range(len(self.AOs)):
            a1 = self.AOs[i1]
            if a1.priority is not None:  # if a1 have any priority constraint (ao before him).
                self.find_constraint_between_aos(a1=a1, con_interactions_list=a1.priority,
                                                 constraint_func=set_priority_constraints)
                # for i2 in range(len(self.AOs)):
                #     a2 = self.AOs[i2]
                #     if a1 == a2:
                #         continue
                #     elif a2.interaction_id in a1.priority:
                #         # priority constraint between them - a2 before a1 -> a2 < a1.
                #         n = random.uniform(0, 1)
                #         if n < self.constraints_percentage:
                #             # limited the number of constraint included in the problem
                #             set_priority_constraints(a1, a2)
            if a1.proximity is not None:  # if a1 have any proximity constraint (ao before him).
                self.find_constraint_between_aos(a1=a1, con_interactions_list=a1.proximity,
                                                 constraint_func=set_proximity_constraints)
                # for i3 in range(len(self.AOs)):
                #     a2 = self.AOs[i3]
                #     if a1 == a2:
                #         continue
                #     elif a2.interaction_id in a1.proximity:
                #         # proximity constraint between them - a2 before a1 -> a2+1 = a1.
                #         n = random.uniform(0, 1)
                #         if n < self.constraints_percentage:
                #             # limited the number of constraint included in the problem
                #             set_proximity_constraints(a1, a2)

    def value_to_triangular(self):
        """
        Get the values to the triangular distribution. This distribution decide on the number of operations in seq.
        lb = number of materials id in the process.
        mean = average length  of similar sequences
        ub = max of similar sequences * 1.5
        :return: mean, ub
        """
        lb = len(self.process_materials)
        lengths = []  # all the lengths of the similar sequences
        for s in self.similar_sequences:  # s is a seq
            lengths.append(len(s))
        mean = max(statistics.mean(lengths), lb)  # max between the mean and the lb , in order to avoid error.
        ub = min(max(lengths) * 1.5, len(self.AOs))  # ub can not be bigger than number of AOs.
        return lb, mean, ub

    def ao_by_interactionID(self):
        """
        split the assembly operations into dict according their interactions ids
        :return:interactions_dict
        """
        interactions_dict = {}
        for a in self.AOs:
            if a.interaction_id not in interactions_dict.keys():
                interactions_dict[a.interaction_id] = [a]
            else:  # this key (interaction id) already exist in the dict
                interactions_dict[a.interaction_id].append(a)
        return interactions_dict

    def filter_domain_to_wiring(self, ao_set, domains):
        """
        get an ao_set (wiring ),and their fully domain. filter domain for each ao -
        save place to all the operations that after this ao.
        :return: filter domain <dict>  decreases the domain
        """
        if self.materials_priorities is None:
            return domains
        # self.materials_priorities - list of tuples (material_prior, material_post)
        for m_id in self.process_materials:  # run over all the materials ids in this process
            list_of_post_m_ids = [constraint[1] for constraint in self.materials_priorities if constraint[0] == m_id]
            count = 0
            for m_id_post in list_of_post_m_ids:
                count += len(find_operations_with_material(m_id_post, ao_set))
            list_of_ao_with_m_id = find_operations_with_material(m_id, ao_set)
            if count != 0:
                for a in list_of_ao_with_m_id:
                    domains[a] = domains[a][: - count]
        return domains

    def csp(self, ao_set):
        """
        Get set of assembly operation.
        Find their order with CSP algorithm
        :param ao_set: list contains type AO.
        :return: a sequence or None.
        """
        arcs = []  # [(a1,a2), (a2,a1)...]
        domains = {}  # { a1: [0,...len(ao_set)], a2: [0,...len(ao_set)] }
        constraints = {}  # {(a1,a2) : lambda ...}
        for a in ao_set:  # a - assembly operation
            domains[a] = list(range(0, len(ao_set)))
            for k in a.constraints:  # k = (a1,a2)
                if k[0] in ao_set and k[1] in ao_set:
                    arcs.append(k)  # list of the constraints keys
                    constraints[k] = a.constraints[k]  # add both side of constraint according to set_constraint().
        if self.domain_code == 'ELE':  # wiring
            domains = self.filter_domain_to_wiring(ao_set, domains)
        arcs = list(set(arcs))  # remove duplicates
        solver = CSPSolver(arcs, domains, constraints, ao_set)  # solve the given CSP
        new_chromosome = solver.solve()  # True indicates that we are using the method as a generator
        return new_chromosome

    def initial_population(self):
        """
        Update: self.chromosomes
        Generate an initial population.
        In each iteration, try to generate a seq in length of number of interaction for product.
        If the seq meet the conditions - generate a Chromosome object.
        """
        init, end = self.find_init_end()  # find init/end assembly. Drop them from self.AOs
        self.get_constraints()
        interactions_dict_AOs = self.ao_by_interactionID()
        time_1 = time.time()
        print_time_line_sep("Start creating initial population")
        while len(self.chromosomes) < self.population_size and self.runtime(time.time()):
            ao_set = select_set_operations(interactions_dict_AOs)  # With all the interactions.
            """ ao_set does not contain init and end operations"""
            if self.use_csp:
                new_chromo = self.csp(ao_set)
            else:
                new_chromo = random_seq(ao_set)
            if new_chromo is not None and not self.isDuplicates(new_chromo):  # we got new feasible sequence
                # print("new chromosome:  (", len(new_chromo), "),", new_chromo)
                new_chromo.insert(0, init)
                new_chromo.append(end)
                c = Chromosome(new_chromo)
                # todo
                c.evaluate(cursorObject, self.similar_sequences)  # evaluate chromosome indices
                if self.fitness_type[0]:  # there is a threshold condition for lcs value
                    if (c.lcs / len(c.gens)) >= 0.5:
                        self.chromosomes.append(c)
                else:
                    self.chromosomes.append(c)
                # todo end
        if len(self.chromosomes) == self.population_size:
            success = True
            self.scale()
        else:  # did not succeeded to generate enough chromosomes
            success = False
        return time.time() - time_1, success

    def get_time_list(self):
        l = []
        for c in self.chromosomes:
            l.append(1.0 / c.duration)
        return l

    def get_lcs_list(self):
        l = []
        for c in self.chromosomes:
            l.append(c.lcs)
        return l

    def get_fitness_list(self):
        l = []
        for c in self.chromosomes:
            l.append(c.fitness)
        return l

    def scale(self):
        """
        Update: Chromosome.fitness_function - Max function.
        scale time and lcs indices into one index - fitness function.
        """
        inverse_time_list = self.get_time_list()  # time from all the chromosomes
        if len(inverse_time_list) != 0:  # for cases that the initial population, didn't succeed to generate sequences
            # at  all.
            max_time = max(inverse_time_list)  # max of the inverse list
            lcs_list = self.get_lcs_list()
            max_lcs = max(lcs_list)
            for c in self.chromosomes:
                inverse_time = 1.0 / c.duration
                c.fitness = self.fitness_type[1] * (inverse_time / max_time) + self.fitness_type[2] * (c.lcs / max_lcs)

    def selection(self):
        """
        The probability of each chromosome being selected for crossover in the next generation.
        The higher the value of the fitness function, the higher the chance of the chromosome being selected.
        formula - fitness value(chromosome i)/ sum(fitness values)
        :return: list of probabilities
        """
        fitness_list = self.get_fitness_list()
        denominator = sum(fitness_list)
        probability = [a / denominator for a in fitness_list]
        return probability

    def find_parents_to_crossover(self):
        """
        Find two different parents (chromosomes) to crossover
        i1,i2 - indices of the chromosomes parents.
        :return: 2 chromosomes to crossover
        """
        probability = self.selection()
        i1 = find_parent(probability)
        p1 = self.chromosomes[i1]
        i2 = find_parent(probability)
        while i1 == i2:
            i2 = find_parent(probability)
        p2 = self.chromosomes[i2]
        return p1, p2

    def check_assembly_constraints(self, c):
        """
        Get a candidate chromosome (only gens) and add it to self.chromosomes if it feasible.
        :param c: candidate chromosome < type : list >
        """
        if not self.isDuplicates(c):  # this chromosome is not already exist (check type of gens and their order)
            if self.check_set_interactions(c):  # all the interactions id needed to produce this process are in c
                if check_proximity_constraint(c):
                    if check_priority_constraint(c):  # the chromosome meets the priority constraints.
                        new_c = Chromosome(c)  # generate the chromosome
                        new_c.evaluate(cursorObject, self.similar_sequences)
                        if self.fitness_type[0]:  # there is a threshold condition for lcs value
                            if (new_c.lcs / len(new_c.gens)) >= 0.5:
                                self.chromosomes.append(new_c)
                                print("New chromosome added to the population:", c)
                        else:
                            self.chromosomes.append(new_c)
                            print("New chromosome added to the population:", c)

    def delete_chromosomes(self):
        """
        Delete chromosome until the population is in size self.population_size.
        """
        self.chromosomes.sort(key=lambda chromosome: chromosome.fitness,
                              reverse=False)  # sorted_chromosomes - sort by fitness
        while len(self.chromosomes) > self.population_size:
            """ delete the chromosome with the smallest fitness function"""
            self.chromosomes.pop(0)

    def crossover(self):
        """
        Generate new chromosome.
        Generate self.population_size * self.crossover_rate new chromosomes
        After - deletes as the number of chromosomes added. may delete new chromosomes. depend of their
        fitness function.
        """
        print_time_line_sep("Crossover function")
        mating_number = round(self.population_size * self.crossover_rate)
        num_run = 0
        while len(self.chromosomes) < (self.population_size + mating_number) and self.runtime(time.time()):
            num_run += 1
            """ each loop can generate between 0 - 2 new chromosomes """
            p1, p2 = self.find_parents_to_crossover()
            # print("p1: ", p1.gens)
            # print("p2: ", p2.gens)
            """min and max length of gens in the parents chromosomes"""
            min_num_gen = min(len(p1.gens), len(p2.gens))
            max_num_gen = max(len(p1.gens), len(p2.gens))
            """generate number between 0 to min gens -1 in both parents (-1 so at least one gen will be replace)"""
            separate_val = random.randint(0, min_num_gen - 2)
            c_new1, c_new2 = [], []
            for g in range(max_num_gen):  # for each gen
                if g <= separate_val:
                    c_new1.insert(g, p1.gens[g])
                    c_new2.insert(g, p2.gens[g])
                elif separate_val < g < min_num_gen:
                    c_new1.insert(g, p2.gens[g])
                    c_new2.insert(g, p1.gens[g])
                else:
                    if len(p1.gens) > len(p2.gens):
                        c_new2.insert(g, p1.gens[g])
                    else:
                        c_new1.insert(g, p2.gens[g])
            self.check_assembly_constraints(c_new1)  # check and add the new chromosome if it fits the conditions
            self.check_assembly_constraints(c_new2)
            if num_run == 1000:
                break
            # print("----- number of chromosomes found:", int(len(self.chromosomes) - self.population_size))
        self.scale()
        self.delete_chromosomes()

    def mutation(self):
        """
        replace the value in the chosen indexes.
        made mutation in probability of mutation_probability
        """
        print_time_line_sep("mutate chromosome")
        if self.runtime(time.time()):
            random_val = random.uniform(0, 1)
            if random_val <= self.mutation_rate:  # will mutate
                c_mutate = random.choice(self.chromosomes)  # randomly pick chromosome to mutate
                if len(c_mutate.gens) > 3:  # otherwise you will mutate chromosome with: init - ao -end
                    i1 = random.randint(1, len(c_mutate.gens) - 2)  # generate the indexes to switch
                    # (except init and end ao).
                    i2 = random.randint(1, len(c_mutate.gens) - 2)
                    while i1 == i2:
                        i2 = random.randint(1, len(c_mutate.gens) - 2)
                    new_chromosome_gens = c_mutate.gens.copy()  # copy the mutate chromosome gens
                    """ switch gens"""
                    new_chromosome_gens[i1], new_chromosome_gens[i2] = c_mutate.gens[i2], c_mutate.gens[i1]
                    # check and add the new chromosome if in the conditions
                    self.check_assembly_constraints(new_chromosome_gens)
                    self.scale()
                    self.delete_chromosomes()

    def update_best_in_round(self):
        """
        Update the new best chromosome and it fitness function.
        If the difference between the fitness function of the new chromosome and the fitness function of the
        best chromosome so far, smaller than self.threshold_value - self.counter_round +1.
        """
        fitness_list = self.get_fitness_list()
        if len(fitness_list) != 0:  # for the case that no chromosome was generator.
            index_max_fitness = fitness_list.index(max(fitness_list))
            best_chromosome_in_round = self.chromosomes[index_max_fitness]
            if abs(best_chromosome_in_round.fitness - self.best_value_fitness) <= self.threshold_value:
                # if the different in  abs is less then threshold_value:
                self.counter_round = self.counter_round + 1
            if best_chromosome_in_round.fitness > self.best_value_fitness:  # the new chromosome is better
                """ update the best chromosome """
                self.best_chromosome = best_chromosome_in_round
                self.best_value_fitness = best_chromosome_in_round.fitness
            # prGreen(self.best_value_fitness)

    def pick_best_seqs(self):
        best_solutions_chromosomes = None
        try:
            self.chromosomes.sort(key=lambda chromosome: chromosome.fitness, reverse=True)  # sort from big to small.
            best_solutions_chromosomes = self.chromosomes[0:self.num_final_chromosomes]
        except(ValueError, IndexError):
            pass
        return best_solutions_chromosomes

    def add_seq_to_DB(self, best_solution, seq_name):
        query1 = "INSERT INTO sequences (sequence_id, work_cell_id, process_name,no_AO_QT,creation_method," \
                 "average_duration, SD_duration,flow_diagram_file,seq_eng_cost,sum_ao_qt_eng_cost,editor, " \
                 "editing_time,execution_file ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s) "
        val1 = (
            seq_name, self.work_cell, self.process_name, len(best_solution.gens), 'GA', None, None, None, None, None,
            'Shir', time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), None)
        cursorObject.execute(query1, val1)
        dataBase.commit()

        val2 = []
        for i in range(len(best_solution.gens)):
            val2.append((seq_name, i + 1, 'ao', best_solution.gens[i].a_id, best_solution.gens[i].interaction_id, None,
                         None))
        print("val2:", val2)
        query2 = "INSERT INTO sequences_operations (sequence_id, op_num, op_type,assembly_operation_id," \
                 "interaction_id, quality_test_id, values_to_update) VALUES (%s, %s, %s, %s,%s, %s,  %s) "
        cursorObject.executemany(query2, val2)
        dataBase.commit()

    def check_if_seq_valid(self, seq):
        if self.check_set_interactions(seq.gens):  # all the interactions id needed to produce this process are in c
            if check_proximity_constraint(seq.gens):
                if check_priority_constraint(seq.gens):  # the chromosome meets the priority constraints.
                    return True
        return False


def get_product_name():
    product_name = input("Please enter product name:")
    if product_name == "":
        print('light panel assembly 1 wire')
        return 'light panel assembly 1 wire'
    return product_name


def get_wci_name():
    product_name = input("Please enter work cell id")
    if product_name == "":
        print('WCI-1')
        return 'WCI-1'
    return product_name


def optimal_sequences(i):
    optimal_seq = [
        ('init', 'pnc', 'glue', 'pih', 'glue', 'pih', 'end'),
        ('init', 'pnc', 'glue', 'pih', 'glue', 'pih', 'glue', 'end'),
        ('init', 'pnc', 'glue', 'pih', 'glue', 'pih', 'end'),

        ('init', 'place', 'insert', 'fix', 'end'),
        ('init', 'place', 'insert', 'fix', 'end'),
        ('init', 'place', 'insert', 'fix', 'end'),

        ('init', 'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'end'),

        ('init', 'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'prep', 'snap_s', 'place', 'pnc', 'snap_f',
         'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'prep', 'snap_s', 'place', 'pnc', 'snap_f',
         'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'prep', 'snap_s', 'place', 'pnc', 'snap_f' 'end'),

        ('init', 'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'prep', 'snap_s', 'place', 'pnc', 'snap_f', 'snap', 'end')
    ]
    return optimal_seq[i]


def main_GA(G):
    """
    main loop of the GA
    :param G: GA object
    :return:
    """
    GA_params = {'time_end': None, 'best_solutions': None, 'initial_pop_time': None, 'pop_flag': None}
    G.find_assembly_operations()
    """ ----- Initial population + Evaluation ----- """
    initial_pop_time, pop_flag = G.initial_population()
    while G.counter_round < G.termination_condition and pop_flag:
        """ ----- Selection + Crossover ----- """
        G.crossover()  # + evaluation
        """ ----- Mutation ----- """
        G.mutation()  # + evaluation
        G.update_best_in_round()
    time_end = time.time()
    best_solutions = G.pick_best_seqs()
    print("------ best solutions: ------ ")
    print(best_solutions)
    GA_params['time_end'] = time_end
    GA_params['best_solutions'] = best_solutions
    GA_params['initial_pop_time'] = initial_pop_time
    GA_params['pop_flag'] = pop_flag
    return GA_params


def lcs_experiment():
    product_wci = [('hose assembly1', 'WCI-3'), ('hose assembly2', 'WCI-3'), ('hose assembly1', 'WCI-30'),
                   ('lid assembly1', 'WCI-2'), ('lid assembly2', 'WCI-2'), ('lid assembly1', 'WCI-20'),
                   ('light panel assembly1', 'WCI-1'), ('light panel assembly2', 'WCI-1'), ('light panel assembly3',
                                                                                            'WCI-1')]
    row_in_csv = {'id': None, 'domain': None, 'variant_num': None, 'product_name': None, 'wci': None,
                  'fitness_type': None, '% constraints': None, 'runtime': None, 'initial_pop_runtime': None,
                  'len_chromosomes': None, 'duration': None, 'success': None, 'gens': None, 'is_seq_valid': None,
                  '% similar_to_expert': None,'expert': None}
    # fitness_types = list : [use threshold? , time_weight, lcs_weight].
    fitness_types = [[True, 1, 0], [False, 0.5, 0.5], [False, 1, 0]]
    constraints_pre = [100, 60]
    random.seed(12)
    s = 0
    for product, wci in product_wci:
        expert_seq = optimal_sequences(s)
        s += 1
        for f in fitness_types:
            for c in constraints_pre:
                for j in range(20):
                    time_0 = time.time()
                    print("product:", product, "wci:", wci, "fitness type:", f, "% constraint:", c)
                    G = GA(population_size=10, mutation_rate=0.05, crossover_rate=0.5, termination_condition=3,
                           threshold_value=0.1, num_final_chromosomes=1, use_csp=True, process_name=product,
                           work_cell=wci, similar_products=select_similar_products(product), start_time=time_0,
                           fitness_type=f, constraints_percentage=c)
                    GA_params = main_GA(G)
                    row_in_csv['id'] = j
                    row_in_csv['domain'] = G.domain_code
                    row_in_csv['variant_num'] = G.domain_code + "-" + str(find_variant_num(
                        index=product_wci.index((product, wci))))
                    row_in_csv['product_name'] = product
                    row_in_csv['wci'] = wci
                    row_in_csv['fitness_type'] = str(f)
                    row_in_csv['% constraints'] = c
                    row_in_csv['runtime'] = GA_params['time_end'] - time_0
                    row_in_csv['initial_pop_runtime'] = GA_params['initial_pop_time']
                    row_in_csv['len_chromosomes'] = len(G.chromosomes)
                    row_in_csv['success'] = [0 if GA_params['time_end'] - time_0 >= G.total_time else 1]
                    row_in_csv['expert'] = str(expert_seq)
                    row_in_csv['length'] = str(len(expert_seq))
                    try:
                        row_in_csv['duration'] = GA_params['best_solutions'][0].duration
                        row_in_csv['gens'] = str(GA_params['best_solutions'][0].gens)
                        row_in_csv['is_seq_valid'] = G.check_if_seq_valid(GA_params['best_solutions'][0])
                        row_in_csv['% similar_to_expert'] = GA_params['best_solutions'][0].get_lcs([expert_seq])
                    except(ValueError, IndexError):
                        row_in_csv['duration'] = None
                        row_in_csv['gens'] = None
                        row_in_csv['is_seq_valid'] = None
                        row_in_csv['% similar_to_expert'] = None
                    df = pd.DataFrame(data=row_in_csv, index=[0])
                    if not os.path.isfile('run_lcs_24May_3.csv'):
                        df.to_csv('run_lcs_24May_3.csv', header=True, index=False)
                    else:  # else it exists so append without writing the header
                        df.to_csv('run_lcs_24May_3.csv', mode='a', header=False, index=False)


def csp_experiment():
    # product_wci = [('hose assembly1', 'WCI-3'), ('hose assembly2', 'WCI-3'), ('hose assembly1', 'WCI-30'),
    #                ('lid assembly1', 'WCI-2'), ('lid assembly2', 'WCI-2'), ('lid assembly1', 'WCI-20'),
    #                ('light panel assembly1', 'WCI-1'), ('light panel assembly2', 'WCI-1'), ('light panel assembly3',
    #                                                                                         'WCI-1')]
    product_wci = [('light panel assembly2', 'WCI-1')]
    row_in_csv = {'id': None, 'domain': None, 'variant_num': None, 'product_name': None, 'wci': None, 'algorithm': None,
                  'runtime': None, 'initial_pop_runtime': None, 'len_chromosomes': None, 'finish_initial_pop': None,
                  'duration': None, 'success': None, 'gens': None}
    random.seed(12)
    for product, wci in product_wci:
        for i in range(2):  # 0- CSP , 1 - random
            if i == 0:
                is_csp = True
            else:
                is_csp = False
            for j in range(20):
                time_0 = time.time()
                print("##################################################")
                print("Product:", product, "WCI:", wci, "use csp?", is_csp)
                G = GA(population_size=10, mutation_rate=0.05, crossover_rate=0.5, termination_condition=3,
                       threshold_value=0.1, num_final_chromosomes=1, use_csp=is_csp, process_name=product,
                       work_cell=wci, similar_products=select_similar_products(product), start_time=time_0,
                       fitness_type=[False, 0.5, 0.5], constraints_percentage=100)
                GA_params = main_GA(G)
                # ------ Export to CSV file ------
                row_in_csv['id'] = j
                row_in_csv['domain'] = G.domain_code
                row_in_csv['variant_num'] = G.domain_code + "-" + str(find_variant_num(
                    index=product_wci.index((product, wci))))
                row_in_csv['product_name'] = product
                row_in_csv['wci'] = wci
                row_in_csv['algorithm'] = ['CSP' if is_csp is True else 'Random']
                row_in_csv['initial_pop_runtime'] = GA_params['initial_pop_time']
                row_in_csv['runtime'] = GA_params['time_end'] - time_0
                row_in_csv['len_chromosomes'] = len(G.chromosomes)
                row_in_csv['finish_initial_pop'] = GA_params['pop_flag']
                row_in_csv['success'] = [0 if GA_params['time_end'] - time_0 >= G.total_time else 1]
                try:
                    row_in_csv['duration'] = GA_params['best_solutions'][0].duration
                    row_in_csv['gens'] = str(GA_params['best_solutions'][0].gens)
                except(ValueError, IndexError):
                    row_in_csv['duration'] = None
                    row_in_csv['gens'] = None
                df = pd.DataFrame(data=row_in_csv, index=[0])
                if not os.path.isfile('run_csp_ELE3.csv'):
                    df.to_csv('run_csp_ELE3.csv', header=True, index=False)
                else:  # else it exists so append without writing the header
                    df.to_csv('run_csp_ELE3.csv', mode='a', header=False, index=False)


def presentation():  # write the best sequence to the DB
    time_0 = time.time()
    random.seed(12)
    # product = get_product_name()
    # wci = get_wci_name()
    # product = input("Please enter product name:")
    # wci = input("Please enter work cell id")
    product = 'light panel assembly2'
    wci = 'WCI-1'
    G = GA(population_size=10, mutation_rate=0.05, crossover_rate=0.5, termination_condition=3,
           threshold_value=0.1, num_final_chromosomes=1, use_csp=True, process_name=product,
           work_cell=wci, similar_products=select_similar_products(product), start_time=time_0,
           fitness_type=[False, 0.5, 0.5], constraints_percentage=100)

    # ['hose assembly1', 'hose assembly2'] - WCI-3
    # light panel assembly1 - WCI-1
    # lid assembly1 - WCI-2
    GA_params = main_GA(G)
    print_end_msg(time_0, GA_params['time_end'])
    # print("Run time:", time_end - time_0)
    save = input(" Do you want to save this sequence in the DB? (please enter yes/no)")
    if save == 'yes':
        seq_name = input("Please enter sequence name that will identify the current sequence in the DB")
        G.add_seq_to_DB(GA_params['best_solutions'][0], seq_name)


if __name__ == "__main__":
    """Connect to the DataBase"""
    dataBase = mysql.connector.connect(
        host="robot-db.cmemwv1xnh6c.eu-west-1.rds.amazonaws.com",
        port=8080,
        user="admin",
        passwd="bguBGU1234",
        database="micro_macro",
        use_pure=True)
    # preparing a cursor object
    cursorObject = dataBase.cursor()
    presentation()
