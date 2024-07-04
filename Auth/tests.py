


# Example fuzzy sets A and B
INPUT = {
    2: 0.1,
    3: 0.5,
    4: 0.3,
    5: 0.8,
    6: 0.6,
    7: 1,
    8: 1,
    9: 0.7,
    10: 1,
    11: 1,
    12: 0.8,
    13: 0.9,
    14: 0.2,
    15: 0.1
}
def fuzzy_set_intersection(A, B):
    intersection = {}
    # Add elements that are common in both A and B
    for element in A.keys() & B.keys():
        intersection[element] = min(A[element], B[element])

    return intersection

def fuzzy_set_union(A, B):
    union = {}
    # Add all elements from A to the union
    for element, degree in A.items():
        union[element] = max(union.get(element, 0), degree)

    # Add all elements from B to the union
    for element, degree in B.items():
        union[element] = max(union.get(element, 0), degree)

    return union


# A_0_5 = [{element:degree} for element, degree in INPUT.items() if degree > 0.5]
A_0_5 = {element:degree for element, degree in INPUT.items() if degree > 0.5}
A_0_6_strong = {element:degree for element, degree in INPUT.items() if degree >= 0.6}


print(A_0_5)
# Calculate the union of A and B
union_result = fuzzy_set_union(A_0_5, A_0_6_strong)
print("Union of A and B:", union_result)
#
#
intersection_result = fuzzy_set_intersection(A_0_5, A_0_6_strong)
print("Intersection of A and B:", intersection_result)

import math

######################################################################################
# Function to calculate Hausdorff distance between two fuzzy sets
def fuzzy_set_distance(A, B):
    max_distance_A_to_B = -math.inf
    max_distance_B_to_A = -math.inf

    # Calculate max distance from A to B
    for elem_A, deg_A in A.items():
        min_distance_A_to_B = math.inf
        for elem_B, deg_B in B.items():
            distance = abs(elem_A - elem_B)
            if distance < min_distance_A_to_B:
                min_distance_A_to_B = distance
        if min_distance_A_to_B > max_distance_A_to_B:
            max_distance_A_to_B = min_distance_A_to_B

    # Calculate max distance from B to A
    for elem_B, deg_B in B.items():
        min_distance_B_to_A = math.inf
        for elem_A, deg_A in A.items():
            distance = abs(elem_B - elem_A)
            if distance < min_distance_B_to_A:
                min_distance_B_to_A = distance
        if min_distance_B_to_A > max_distance_B_to_A:
            max_distance_B_to_A = min_distance_B_to_A

    # Hausdorff distance is the maximum of the two max distances
    hausdorff_distance = max(max_distance_A_to_B, max_distance_B_to_A)

    return hausdorff_distance


# Example fuzzy sets A and B (re-using from previous examples)
A = {
    1: 0.5,
    2: 1,
    3: 0.3
}

B = {
    2: 0.4,
    3: 0.4,
    4: 0.1
}

# Calculate the Hausdorff distance between A and B
distance = fuzzy_set_distance(A, B)
print("Hausdorff distance between A and B:", distance)


class FuzzyNumber:
    def __init__(self, core, support):
        self.core = core  # Core value of the fuzzy number
        self.support = support  # Support value of the fuzzy number

    def __add__(self, other):
        # Calculate core of the resulting fuzzy number
        new_core = self.core + other.core

        # Calculate support of the resulting fuzzy number
        new_support = self.support + other.support

        return FuzzyNumber(new_core, new_support)

    def __str__(self):
        return f"Core: {self.core}, Support: {self.support}"


# Define fuzzy numbers A and B
A = [
    FuzzyNumber(core=0.3, support=1),
    FuzzyNumber(core=0.6, support=2),
    FuzzyNumber(core=1.0, support=3),
    FuzzyNumber(core=0.7, support=4),
    FuzzyNumber(core=0.2, support=5)
]

B = [
    FuzzyNumber(core=0.5, support=10),
    FuzzyNumber(core=1.0, support=11),
    FuzzyNumber(core=0.5, support=12)
]


# Function to add multiple fuzzy numbers with different lengths
def add_multiple_fuzzy_numbers(A, B):
    result = []

    max_length = max(len(A), len(B))

    for i in range(max_length):
        fuzzy_A = A[i] if i < len(A) else FuzzyNumber(core=0, support=0)
        fuzzy_B = B[i] if i < len(B) else FuzzyNumber(core=0, support=0)

        result.append(fuzzy_A + fuzzy_B)

    return result


# Add fuzzy numbers A and B
result = add_multiple_fuzzy_numbers(A, B)

# Print the result
print("Result of addition of multiple fuzzy numbers (A + B):")
for idx, fuzzy in enumerate(result):
    print(f"Fuzzy {idx + 1}: {fuzzy}")



