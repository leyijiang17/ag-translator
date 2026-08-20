using Oscar

P2 = projective_space(NormalToricVariety, 2)
D = torusinvariant_prime_divisors(P2)

DD = toric_divisor(P2, [4, 2, 3])
is_cartier(DD)
is_principal(DD)

EE = toric_divisor(P2, [4, 2, -6])
is_cartier(EE)
is_principal(EE)

coefficients(DD)
P = polyhedron(DD)
is_feasible(P)

ClP2 = class_group(P2)
picard_group(P2)
