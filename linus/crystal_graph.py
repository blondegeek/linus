import numpy as np
from se3cnn.SO3 import basis_transformation_Q_J
from se3cnn.util.cache_file import cached_dirpklgz
from symmetry_finding import ylms_within_r_cutoff
import torch

def get_indices_for_irrep(irrep, L_max):
    if irrep not in range(L_max + 1):
        return None
    start_index = 0
    for cur_irrep in range(L_max + 1):
        if cur_irrep != irrep:
            start_index += 2 * cur_irrep + 1
        else:
            break
    end_index = start_index + (2 * irrep + 1)
    return slice(start_index, end_index)


# This is in torch, but it doesn't have to be
@cached_dirpklgz("cache/compute_Q")
def compute_Q(L1_max, L2_max, L3_max, eps=1e-8):
    Ls1 = list(range(L1_max + 1))
    Ls2 = list(range(L2_max + 1))
    Ls3 = list(range(L3_max + 1))
    rep_sum1 = sum([2 * L + 1 for L in range(L1_max + 1)])
    rep_sum2 = sum([2 * L + 1 for L in range(L2_max + 1)])
    rep_sum3 = sum([2 * L + 1 for L in range(L3_max + 1)])
    basis_trans = torch.zeros(rep_sum1, rep_sum2, rep_sum3)
    for L1 in Ls1:
        for L2 in Ls2:
            for L3 in Ls3:
                if L2 in list(range(abs(L1 - L3), L1 + L3 + 1)):
                    Q = basis_transformation_Q_J(L2, L1, L3).view(2 * L3 + 1, 2 * L1 + 1, 2 * L2 + 1)
                    Q = Q.transpose(0,1).transpose(1,2)
                    # Q /= (torch.norm(Q, dim=-1, keepdim=True) + eps)
                    L1_slice, L2_slice, L3_slice = (get_indices_for_irrep(L1, L1_max),
                                                    get_indices_for_irrep(L2, L2_max),
                                                    get_indices_for_irrep(L3, L3_max))
                    basis_trans[L1_slice, L2_slice, L3_slice] = Q
    return basis_trans


class TensorProduct(object):
    """
    Tensor product with no learned parameters. Paths are summed.
    """
    def __init__(self, L1_max, L2_max, L3_max):
        super().__init__()
        self.L1_max = L1_max
        self.L2_max = L2_max
        self.L3_max = L3_max
        self.Q_matrix = compute_Q(L1_max, L2_max, L3_max).detach().numpy()

    def compute(self, input1, input2):
        return np.einsum('i,j,ijk->k', input1, input2, self.Q_matrix)
        # With channels this would be
        # return np.einsum('ci,cj,ijk->ck', input1, input2, self.Q_matrix)


class CrystalGraph(object):
    def __init__(self, coords, r_max=5.0, L_max=5):
        self.coords = coords
        self.r_max = r_max
        self.L_max = L_max
        N, _ = coords.shape
        self.diff_M = coords.reshape(1, N, 3) - coords.reshape(N, 1, 3)
        self.dist_M = np.linalg.norm(self.diff_M, axis=-1)
        self.adjacency = np.where((self.dist_M < r_max) & (self.dist_M > 0), 1, 0)
        self.edges = set(map(frozenset,
                             list(zip(*np.array(np.where(self.adjacency)).tolist()))))
        self.edges = list(map(sorted, map(list, list(self.edges))))
        self.edges = {tuple(edge): None for edge in self.edges}
        # featurize sites
        self.sites = []
        for i in range(N):
            self.sites.append(
                ylms_within_r_cutoff(self.diff_M[i], self.r_max, self.L_max)[0].sum(axis=-1))
        # featurize edges
        self.tp = TensorProduct(self.L_max, self.L_max, self.L_max)
        for a,b in self.edges.keys():
            self.edges[(a,b)] = self.tp.compute(self.sites[a], self.sites[b])
