import random
import time


def sort_func(k):
    if k.priority is None:
        return 0
    else:
        return len(k.priority)


class BackTrack(object):

    def __init__(self, domains, constraints):
        self.domains = domains
        self.constraints = constraints
        self.sorted_ao = self.set_sorted_domain()
        self.flag = 0
        self.new_chromo = [None] * len(self.sorted_ao)  # generate chromosome in length of the AOs.
        self.domain_BT = self.set_domain_BT()

    def set_sorted_domain(self):
        # sort self.domains. From the key with the least values in the domain to the most values.
        # return list of keys  - AOs.
        return sorted(self.domains, key=lambda k: len(self.domains[k]), reverse=False)  # return list
        # return sorted(self.domains, key=sort_func, reverse=True)

    def set_domain_BT(self):
        new_d = {}
        for key, value in self.domains.items():
            new_d[key] = value.copy()
        return new_d

    def backTrack(self):
        """

        :return:
        """
        time_start_BT = time.time()
        while time.time() - time_start_BT <= 60 * 9:
            if self.flag == len(self.sorted_ao):  # find a sequence
                return True
            if self.flag == -1:  # No solution -> get back from variable 1.
                return False
            ao = self.sorted_ao[self.flag]
            move_ao = False  # move to the next ao or get back to the last ao
            while not move_ao:
                if len(self.domain_BT[ao]) == 0:  # no assigment for this AO
                    self.step_back()
                    move_ao = True
                else:
                    place = random.choice(self.domain_BT[ao])  # randomly pick placement to this AO from his domains
                    # --- check constraints: ---
                    # constraint 1: inequality between AOs
                    if self.new_chromo[place] is not None:  # There is a operation place there yet -  spot is not empty
                        self.domain_BT[ao].remove(place)
                    # constraint 2: priority
                    else:
                        did_break = False
                        for i in range(0, self.flag):  # for each AO that already get a place in the sequence.
                            place_ao = self.sorted_ao[i]
                            if (place_ao, ao) in self.constraints:  # There is a constraint between them.
                                check = self.constraints[(place_ao, ao)]
                                if not check(self.find_index(place_ao), place):  # Does not meet constraints
                                    self.domain_BT[ao].remove(place)
                                    did_break = True
                                    break
                        if not did_break:  # All constraints meets.
                            self.new_chromo[place] = ao
                            self.flag += 1
                            move_ao = True

    def find_sequence(self):
        result = self.backTrack()
        if result:  # find sequence
            return self.new_chromo
        else:
            return None

    def step_back(self):
        cur_ao = self.sorted_ao[self.flag]
        self.domain_BT[cur_ao] = self.domains[cur_ao].copy()  # return values (domain) to the current AO.
        self.flag -= 1
        return_ao = self.sorted_ao[self.flag]  # the AO that return to him.
        val_to_remove = self.find_index(return_ao)
        self.domain_BT[return_ao].remove(val_to_remove)  # remove the inconsistent value from the lat ao
        self.new_chromo[val_to_remove] = None  # remove assigment from new_chromo

    def find_index(self, place_ao):
        """
        Get an AO, need to find his assigment - index in new_chromo
        :param place_ao: assembly operation that already assign.
        :return: index (AO assignment)
        """
        val = self.new_chromo.index(place_ao)
        return val
