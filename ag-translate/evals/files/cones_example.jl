using Oscar

σ = positive_hull([-2 5; 1 0])
rays(σ)
facets(σ)

σⱽ = polarize(σ)

C0 = positive_hull([1 0; 1 1])
C1 = positive_hull([1 1; 0 1])
C01 = intersect(C0, C1)
dim(C01)

A = hilbert_basis(σⱽ)

Y = normal_toric_variety(σ)
is_smooth(Y)
is_normal(Y)
dim(Y)
is_simplicial(Y)
is_affine(Y)
