def lcs2(X, Y):
    # find the length of the strings
    m = len(X)
    n = len(Y)

    # declaring the array for storing the dp values
    L = [[0] * (n + 1) for i in range(m + 1)]

    """Following steps build L[m + 1][n + 1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1].connection_type == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]


class Chromosome(object):
    def __repr__(self):
        return "Chromosome: " + str(self.gens) + " time: " + str(self.duration) + "\n"

    def __init__(self, gens):
        """ Initialize the chromosome parameters """
        self.gens = gens  # an array of the gens in their order. list of AO objects.
        self.fitness = 0
        self.duration = 0
        self.lcs = 0

    def evaluate(self, cursorObject, similar_seq):
        """
        Evaluate chromosome indices - time and connection strength.
        """
        self.duration = self.get_time(cursorObject)
        self.lcs = self.get_lcs(similar_seq)

    def get_time(self, cursorObject):
        time = 0
        for gen in self.gens:
            query = """select average_duration from assembly_operations where assembly_operation_id = %s"""
            cursorObject.execute(query, (gen.a_id,))
            result = cursorObject.fetchall()
            time += result[0][0]
        return time

    def get_lcs(self, similar_seq):
        """
        For each seq of similar product, compute lcs.
        return the max result.
        :param similar_seq: nested list
        :return: max lcs
        """
        results = []
        for s in similar_seq:
            r = lcs2(self.gens, s)
            results.append(r)
        return max(results)
