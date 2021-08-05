from termcolor import colored


def set_priority(inter_dict):
    if 'priority' in inter_dict:
        return inter_dict['priority']
    else:
        return None


def set_proximity(inter_dict):
    if 'proximity' in inter_dict:
        return inter_dict['proximity']
    else:
        return None


class AO(object):
    def __repr__(self):
        return "AO: " + str(self.a_id) + "  id: " + str(self.interaction_id)

    #  + colored(str(self.interaction_id), 'red')

    def __init__(self, a_id, materials, actors, connection_type, inter_dict):
        """ Initialize AO parameters """
        self.a_id = a_id
        self.interaction_id = inter_dict['id']
        self.materials = materials  # ids
        self.actors = actors
        self.connection_type = connection_type
        self.constraints = {}
        self.priority = set_priority(inter_dict)  # interactions_ids: ids that should be before this interaction.
        self.proximity = set_proximity(inter_dict)

    def check_materials(self, a):
        """
        get another assembly operation with the same id. check if they have the same materials.
        :param a: assembly operation
        :return: True - the same materials
        """
        if sorted(self.materials) == sorted(a.materials):
            return True
        else:
            return False
