import itertools
import sys

# This function reads the training data from the file and convert it into a list of tuples
def read_training_data(file_path):
    """Reads the training data from a file and returns it as a list of tuples."""
    with open(file_path, "r") as file:
        return [tuple(map(int, line.strip().split())) for line in file.readlines()]

# This function computes the Conditional Probability Tables (CPT) for the Bayesian Network from the training data
def calculate_cpt(training_data):
    """Calculates Conditional Probability Tables (CPTs) for the Bayesian Network."""
    counts = {
        "B": {0: 0, 1: 0},
        "G|B": {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0},
        "F|G,C": {(0, 0, 0): 0, (0, 0, 1): 0, (0, 1, 0): 0, (0, 1, 1): 0,
                  (1, 0, 0): 0, (1, 0, 1): 0, (1, 1, 0): 0, (1, 1, 1): 0},
        "C": {0: 0, 1: 0},
    }
    total = len(training_data)
    
    for b, g, c, f in training_data:
        counts["B"][b] += 1
        counts["C"][c] += 1
        counts["G|B"][(g, b)] += 1
        counts["F|G,C"][(f, g, c)] += 1

    cpt = {
        "P(B)": {b: counts["B"][b] / total for b in [0, 1]},
        "P(C)": {c: counts["C"][c] / total for c in [0, 1]},
        "P(G|B)": {(g, b): counts["G|B"][(g, b)] / counts["B"][b] for g, b in itertools.product([0, 1], repeat=2)},
        "P(F|G,C)": {(f, g, c): counts["F|G,C"][(f, g, c)] / 
                      sum(counts["F|G,C"][(x, g, c)] for x in [0, 1]) 
                      for f, g, c in itertools.product([0, 1], repeat=3)}
    }
    return cpt

# This function implements the Inference by Enumeration algorithm. This function recursively computes the joint probability for a list of variables,
# given evidence and CPTs.
def enumerate_all(variables, evidence, cpt):
    """Inference by enumeration algorithm."""
    if not variables:
        return 1.0
    Y = variables[0]
    rest = variables[1:]
    if Y in evidence:
        return probability(Y, evidence[Y], evidence, cpt) * enumerate_all(rest, evidence, cpt)
    else:
        total = 0
        for y in [0, 1]:
            extended_evidence = evidence.copy()
            extended_evidence[Y] = y
            total += (probability(Y, y, extended_evidence, cpt) * 
                      enumerate_all(rest, extended_evidence, cpt))
        return total

# This function calculates the probability of a specific variable taking a given value, considering the evidence and CPTs
def probability(var, value, evidence, cpt):
    """Returns the probability of a variable given evidence."""
    if var == "B":
        return cpt["P(B)"][value]
    elif var == "C":
        return cpt["P(C)"][value]
    elif var == "G":
        return cpt["P(G|B)"][(value, evidence["B"])]
    elif var == "F":
        return cpt["P(F|G,C)"][(value, evidence["G"], evidence["C"])]
    else:
        raise ValueError(f"Unknown variable: {var}")

# This function parses a user query into query variables and evidence
def parse_query(query):
    """Parses the query string and returns query variables and evidence."""
    parts = query.split(" given ")
    query_vars = parts[0].split()
    evidence = {}
    
    if len(parts) > 1:
        evidence_parts = parts[1].split()
        for ev in evidence_parts:
            evidence[ev[0]] = 1 if ev[1] == 't' else 0

    parsed_query = {qv[0]: 1 if qv[1] == 't' else 0 for qv in query_vars}
    return parsed_query, evidence

# This function computes the probability of the query using the Inference by Enumeration algorithm
def query_bayes_net(query, cpt):
    """Computes the probability for the query using enumeration."""
    query_vars, evidence = parse_query(query)
    all_vars = ["B", "G", "C", "F"]
    hidden_vars = [v for v in all_vars if v not in query_vars and v not in evidence]

    # Calculate numerator (P(query_vars & evidence))
    numerator_evidence = evidence.copy()
    numerator_evidence.update(query_vars)
    numerator = enumerate_all(all_vars, numerator_evidence, cpt)

    # Calculate denominator (P(evidence)) if evidence is provided
    if evidence:
        denominator = enumerate_all(all_vars, evidence, cpt)
    else:
        denominator = 1

    return numerator / denominator

def main():
    if len(sys.argv) != 2:
        print("Usage: bnet.py <training_data_file>")
        return

    training_data_file = sys.argv[1]
    try:
        training_data = read_training_data(training_data_file)
        cpt = calculate_cpt(training_data)
        while True:
            query = input("Query: ").strip()
            if query.lower() == "none":
                break
            probability = query_bayes_net(query, cpt)
            print(f"Probability: {probability:.9f}")
    except FileNotFoundError:
        print(f"Error: File '{training_data_file}' not found.")
    except ValueError as e:
        print(f"Error: Invalid training data format. {e}")

if __name__ == "__main__":
    main()
