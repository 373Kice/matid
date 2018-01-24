"""This module defines functions for deriving geometry related quantities from
a atomic system.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import itertools

import numpy as np
from numpy.random import RandomState
import time

from ase.data import covalent_radii
from ase import Atom, Atoms
from ase.visualize import view
import ase.geometry

from systax.data.element_data import get_covalent_radii
from systax.exceptions import SystaxError
from systax.core.linkedunits import Substitution

from sklearn.cluster import DBSCAN

from scipy.spatial import Delaunay


def get_nearest_atom(system, position):
    """Finds the index of the atom nearest to the given position in the given
    system.

    Args:
        system(ase.Atoms): The system from which the atom is searched from.
        position(np.ndarray): The position to search.

    Returns:
        int: Index of the nearest atom.
    """
    positions = system.get_positions()
    distances = get_distance_matrix(position, positions)
    min_index = np.argmin(distances)

    return min_index


def get_nearest_neighbours(system, dist_matrix_pbc):
    """For each atom in the given system, returns a list of indices for the
    nearest neighbours and a list of distances to the neighbour.

    Args:
        system(ase.Atoms): The system from which the nearest neighbours are
            calculated

    Returns:
        int: Index of the nearest atom.
    """
    cell = system.get_cell()
    min_basis = np.linalg.norm(cell, axis=1).min()
    dist_matrix_mod = np.array(dist_matrix_pbc)
    np.fill_diagonal(dist_matrix_mod, min_basis)

    columns = np.argmin(dist_matrix_mod, axis=1)
    rows = range(len(system))
    distances = dist_matrix_mod[rows, columns]

    return columns, distances


def get_dimensionality_new(
        system,
        cluster_threshold
    ):
    """Used to calculate the dimensionality of a system.

    Args:
        system (ASE.Atoms): The system for which the dimensionality is
            evaluated.
        cluster_threshold(float): The epsilon value for the DBSCAN algorithm
            that is used to identify clusters within the unit cell.
        disp_tensor (np.ndarray): A precalculated displacement tensor for the
            system.
        disp_tensor_pbc (np.ndarray): A precalculated displacement tensor that
            takes into account the periodic boundary conditions for the
                system.
        distances(np.ndarray): A precalculated array of the distances used for
            clustering the system.

    Returns:
        int: The dimensionality of the system.
        np.ndarray: Boolean array indicating the presence of vacuum gaps.

    Raises:
        SystaxError: If the dimensionality can't be detected
    """

    # 1x1x1 system
    # pos = system.get_positions()
    # cell = system.get_cell()
    # num = system.get_atomic_numbers()
    # pbc = system.get_pbc()
    # displacements_pbc = get_displacement_tensor(pos, pos, cell, pbc, mic=True)
    # dist_matrix_pbc = np.linalg.norm(displacements_pbc, axis=2)
    # radii = covalent_radii[num]
    # radii_matrix = radii[:, None] + radii[None, :]
    # dist_matrix_radii_pbc = dist_matrix_pbc - radii_matrix

    # # Check the number of clusters. We don't want the clustering to hog all
    # # resources, so the cpu's are limited to one
    # db = DBSCAN(eps=cluster_threshold, min_samples=1, metric='precomputed', n_jobs=1)
    # db.fit(dist_matrix_radii_pbc)
    # clusters_finite = db.labels_
    # n_clusters_finite = len(np.unique(clusters_finite))
    # print(n_clusters_finite)

    # # 2x2x2 system
    # system = system.repeat((2, 2, 2))
    # pos = system.get_positions()
    # cell = system.get_cell()
    # num = system.get_atomic_numbers()
    # pbc = system.get_pbc()
    # displacements_pbc = get_displacement_tensor(pos, pos, cell, pbc, mic=True)
    # dist_matrix_pbc = np.linalg.norm(displacements_pbc, axis=2)
    # radii = covalent_radii[num]
    # radii_matrix = radii[:, None] + radii[None, :]
    # dist_matrix_radii_pbc = dist_matrix_pbc - radii_matrix

    # # Check the number of clusters. We don't want the clustering to hog all
    # # resources, so the cpu's are limited to one
    # db = DBSCAN(eps=cluster_threshold, min_samples=1, metric='precomputed', n_jobs=1)
    # db.fit(dist_matrix_radii_pbc)
    # clusters_finite = db.labels_
    # n_clusters_finite = len(np.unique(clusters_finite))
    # print(n_clusters_finite)

    # Calculate the displacements in the finite system taking into account
    # periodicity
    # if pbc.any():
        # if disp_tensor_pbc is not None:
            # displacements_finite_pbc = disp_tensor_pbc
        # else:
            # displacements_finite_pbc = get_displacement_tensor(pos, pos, cell, pbc, mic=True)
    # else:
        # if disp_tensor is not None:
            # displacements_finite_pbc = disp_tensor
        # else:
            # displacements_finite_pbc = get_displacement_tensor(pos, pos)
    # if radii_matrix is None:
        # radii = covalent_radii[num]
        # radii_matrix = radii[:, None] + radii[None, :]
    # if dist_matrix_radii_pbc is None:
        # dist_matrix_radii_pbc = np.linalg.norm(displacements_finite_pbc, axis=2)
        # dist_matrix_radii_pbc -= radii_matrix

    # # Check the number of clusters. We don't want the clustering to hog all
    # # resources, so the cpu's are limited to one
    # db = DBSCAN(eps=cluster_threshold, min_samples=1, metric='precomputed', n_jobs=1)
    # db.fit(dist_matrix_radii_pbc)
    # clusters_finite = db.labels_
    # n_clusters_finite = len(np.unique(clusters_finite))

    # # If the system consists of multiple components that are not connected
    # # according to the clustering done here, then we cannot assess the
    # # dimensionality.
    # if n_clusters_finite > 1:
        # raise SystaxError(
            # "Could not determine the dimensionality because there are more than"
            # " one energetically isolated components in the unit cell"
        # )

    # Bring the one cluster together and calculate internal displacements
    # without pbc
    # seed_pos = pos[0, :]
    # disp_seed = displacements_finite_pbc[0, :, :]
    # pos1 = seed_pos + disp_seed
    # displacements_finite = get_displacement_tensor(pos1, pos1)

    # clustered = Atoms(
        # positions=pos1,
        # symbols=num,
        # cell=cell,
        # pbc=pbc
    # )
    # view(clustered)
    # view(clustered.repeat((2, 1, 1)))
    # view(clustered.repeat((1, 2, 1)))
    # view(clustered.repeat((1, 1, 2)))

    # For each basis direction, add the basis vector to the displacements to
    # get the distance between two neighbouring copies of the cluster. If the
    # minimum distance between two copies is bigger or equal to the vacuum gap,
    # then remove one dimension.
    # dim = 3
    # vacuum_gaps = np.array((False, False, False))
    # for i_basis, basis in enumerate(cell):

        # # If the system is not periodic in this direction, reduce the
        # # periodicity
        # i_pbc = pbc[i_basis]
        # if not i_pbc:
            # dim -= 1
            # vacuum_gaps[i_basis] = True
            # continue

        # # If system is periodic in this direction, calculate the distance
        # # between the periodicly repeated cluster by also taking radii into
        # # account
        # disp = np.array(displacements_finite)
        # disp += basis
        # dist = np.linalg.norm(disp, axis=2)
        # dist -= radii_matrix
        # min_dist = dist.min()
        # print(min_dist)
        # if min_dist >= cluster_threshold:
            # vacuum_gaps[i_basis] = True
            # dim -= 1

    # return dim, vacuum_gaps


def get_dimensionality(
        system,
        cluster_threshold,
        disp_tensor=None,
        disp_tensor_pbc=None,
        dist_matrix_radii_pbc=None,
        radii_matrix=None
    ):
    """Used to calculate the dimensionality of a system.

    Args:
        system (ASE.Atoms): The system for which the dimensionality is
            evaluated.
        cluster_threshold(float): The epsilon value for the DBSCAN algorithm
            that is used to identify clusters within the unit cell.
        disp_tensor (np.ndarray): A precalculated displacement tensor for the
            system.
        disp_tensor_pbc (np.ndarray): A precalculated displacement tensor that
            takes into account the periodic boundary conditions for the
                system.
        distances(np.ndarray): A precalculated array of the distances used for
            clustering the system.

    Returns:
        int: The dimensionality of the system.
        np.ndarray: Boolean array indicating the presence of vacuum gaps.

    Raises:
        SystaxError: If the dimensionality can't be detected
    """
    cell = system.get_cell()
    pbc = expand_pbc(system.get_pbc())
    pos = system.get_positions()
    num = system.get_atomic_numbers()

    # Calculate the displacements in the finite system taking into account
    # periodicity
    if pbc.any():
        if disp_tensor_pbc is not None:
            displacements_finite_pbc = disp_tensor_pbc
        else:
            displacements_finite_pbc = get_displacement_tensor(pos, pos, cell, pbc, mic=True)
    else:
        if disp_tensor is not None:
            displacements_finite_pbc = disp_tensor
        else:
            displacements_finite_pbc = get_displacement_tensor(pos, pos)
    if radii_matrix is None:
        radii = covalent_radii[num]
        radii_matrix = radii[:, None] + radii[None, :]
    if dist_matrix_radii_pbc is None:
        dist_matrix_radii_pbc = np.linalg.norm(displacements_finite_pbc, axis=2)
        dist_matrix_radii_pbc -= radii_matrix

    # Check the number of clusters. We don't want the clustering to hog all
    # resources, so the cpu's are limited to one
    db = DBSCAN(eps=cluster_threshold, min_samples=1, metric='precomputed', n_jobs=1)
    db.fit(dist_matrix_radii_pbc)
    clusters_finite = db.labels_
    n_clusters_finite = len(np.unique(clusters_finite))

    # If the system consists of multiple components that are not connected
    # according to the clustering done here, then we cannot assess the
    # dimensionality.
    if n_clusters_finite > 1:
        raise SystaxError(
            "Could not determine the dimensionality because there are more than"
            " one energetically isolated components in the unit cell"
        )

    # Bring the one cluster together and calculate internal displacements
    # without pbc
    seed_pos = pos[0, :]
    disp_seed = displacements_finite_pbc[0, :, :]
    pos1 = seed_pos + disp_seed
    displacements_finite = get_displacement_tensor(pos1, pos1)

    # For each basis direction, add the basis vector to the displacements to
    # get the distance between two neighbouring copies of the cluster. If the
    # minimum distance between two copies is bigger or equal to the vacuum gap,
    # then remove one dimension.
    dim = 3
    vacuum_gaps = np.array((False, False, False))
    for i_basis, basis in enumerate(cell):

        # If the system is not periodic in this direction, reduce the
        # periodicity
        i_pbc = pbc[i_basis]
        if not i_pbc:
            dim -= 1
            vacuum_gaps[i_basis] = True
            continue

        # If system is periodic in this direction, calculate the distance
        # between the periodicly repeated cluster by also taking radii into
        # account
        disp = np.array(displacements_finite)
        disp += basis
        dist = np.linalg.norm(disp, axis=2)
        dist -= radii_matrix
        min_dist = dist.min()
        if min_dist >= cluster_threshold:
            vacuum_gaps[i_basis] = True
            dim -= 1

    return dim, vacuum_gaps


def get_tetrahedra_decomposition(system, vacuum_gaps, max_distance):
    """Used to decompose a series of 3D atomic coordinates into non-overlapping
    tetrahedron that together represent the atomic structure.

    """
    # TODO: Reuse the distance matrix from the original system, just filter out
    # the entries that do not belong to the valid basis. This way we can avoid
    # recalculating the distances.

    # TODO: Determine the distance matrix of the padded system during the
    # construction of the padded system. This should be doable by simply using
    # the internal displacements and the cell periodicity.

    class TetrahedraDecomposition():
        """A class that represents a collection of tetrahedron.
        """
        def __init__(self, delaunay, invalid_simplex_indices):
            self.delaunay = delaunay
            self.invalid_simplex_indices = invalid_simplex_indices

        def find_simplex(self, pos):
            """Used to find the index of the simplex in which the given
            position resides in.

            Args:
                pos(np.nadrray): Position for which to find the simplex

            Returns:
                int: Index of the simplex in which the point is in. Returns
                None if simplex was not found.
            """
            index = self.delaunay.find_simplex(pos).item()
            if index == -1:
                return None
            if index not in self.invalid_simplex_indices:
                return index
            return None

    cell = system.get_cell()
    pos = system.get_positions()
    num = system.get_atomic_numbers()

    # Calculate a matrix containing the combined radii for each pair of atoms
    # in an extended system
    radii = covalent_radii[num]
    radii_matrix = radii[:, None] + radii[None, :]

    displacements_finite = get_displacement_tensor(pos, pos)

    # In order for the decomposition to cover also the edges, we have to extend
    # the system to cover also into the adjacent periodic images. That is done
    # within this loop.
    tesselation_atoms = system.copy()
    multipliers = np.array(list(itertools.product((-1, 0, 1), repeat=3)))

    for mult in multipliers:
        if tuple(mult) != (0, 0, 0):
            disloc = np.dot(mult, cell)

            # If system is periodic in this direction, calculate the distance
            # between atoms in the periodically repeated images and choose
            # atoms from the copies that are within a certain range when tha
            # radii are taken into account
            disp = np.array(displacements_finite)
            disp += disloc
            dist = np.linalg.norm(disp, axis=2)
            dist_radii = dist - radii_matrix
            connectivity_mask = np.where(dist_radii < max_distance)

            pad_pos = pos[connectivity_mask[1]] + disp[connectivity_mask[0], connectivity_mask[1]]
            pad_num = num[connectivity_mask[1]]
            pad_atoms = Atoms(positions=pad_pos, symbols=pad_num)
            tesselation_atoms += pad_atoms

    # view(tesselation_atoms)
    tesselation_pos = tesselation_atoms.get_positions()

    # The QJ options makes sure that all positions are included in the
    # tesselation
    tri = Delaunay(tesselation_pos, qhull_options="QJ")

    # Remove invalid simplices from the surface until only valid simplices are
    # found on the surface
    distance_matrix = get_covalent_distances(tesselation_atoms, mic=False)
    simplices = np.array(tri.simplices)
    neighbors = np.array(tri.neighbors)
    end = False
    invalid_indices = set()
    surface_simplices = np.any(neighbors == -1, axis=1)
    original_indices = np.arange(len(simplices))
    surface_simplex_indices = set(original_indices[surface_simplices])

    while not end:

        # Remove the surface simplices that are too big. Also update the
        # neighbour list.
        too_big_simplex_indices = []
        for i_simplex in surface_simplex_indices:
            simplex = simplices[i_simplex]
            for i, j in itertools.combinations(simplex, 2):
                distance = distance_matrix[i, j]
                if distance >= max_distance:
                    too_big_simplex_indices.append(i_simplex)
                    break
        invalid_indices = invalid_indices | set(too_big_simplex_indices)
        if len(too_big_simplex_indices) == 0:
            end = True
        else:
            # Find the neighbours of the simplices that were removed
            mask = np.isin(neighbors, too_big_simplex_indices)
            affected = np.any(mask, axis=1)
            new_surface_simplex_indices = set(original_indices[affected])
            new_surface_simplex_indices -= invalid_indices
            surface_simplex_indices = new_surface_simplex_indices

    tetrahedras = TetrahedraDecomposition(tri, invalid_indices)
    return tetrahedras


def get_moments_of_inertia(system, weight=True):
    """Calculates geometric inertia tensor, i.e., inertia tensor but with
    all masses are set to 1.

    I_ij = sum_k m_k (delta_ij * r_k^2 - x_ki * x_kj)
    with r_k^2 = x_k1^2 + x_k2^2 x_k3^2

    Args:
        system(ASE Atoms): Atomic system.

    Returns:
        (np.ndarray, np.ndarray): The eigenvalues and eigenvectors of the
        geometric inertia tensor.
    """
    # Move the origin to the geometric center
    positions = system.get_positions()
    centroid = get_center_of_mass(system, weight)
    pos_shifted = positions - centroid

    # Calculate the geometric inertia tensor
    if weight:
        weights = system.get_masses()
    else:
        weights = np.ones((len(system)))
    x = pos_shifted[:, 0]
    y = pos_shifted[:, 1]
    z = pos_shifted[:, 2]
    I11 = np.sum(weights*(y**2 + z**2))
    I22 = np.sum(weights*(x**2 + z**2))
    I33 = np.sum(weights*(x**2 + y**2))
    I12 = np.sum(-weights * x * y)
    I13 = np.sum(-weights * x * z)
    I23 = np.sum(-weights * y * z)

    I = np.array([
        [I11, I12, I13],
        [I12, I22, I23],
        [I13, I23, I33]])

    evals, evecs = np.linalg.eigh(I)

    return evals, evecs


def find_vacuum_directions(system, threshold):
    """Searches for vacuum gaps that are separating the periodic copies.

    TODO: Implement a n^2 search that allows the detection of more complex
    vacuum boundaries.

    Returns:
        np.ndarray: An array with a boolean for each lattice basis
        direction indicating if there is enough vacuum to separate the
        copies in that direction.
    """
    rel_pos = system.get_scaled_positions()
    pbc = system.get_pbc()

    # Find the maximum vacuum gap for all basis vectors
    gaps = np.empty(3, dtype=bool)
    for axis in range(3):
        if not pbc[axis]:
            gaps[axis] = True
            continue
        comp = rel_pos[:, axis]
        ind = np.sort(comp)
        ind_rolled = np.roll(ind, 1, axis=0)
        distances = ind - ind_rolled

        # The first distance is from first to last, so it needs to be
        # wrapped around
        distances[0] += 1

        # Find maximum gap in cartesian coordinates
        max_gap = np.max(distances)
        basis = system.get_cell()[axis, :]
        max_gap_cartesian = np.linalg.norm(max_gap*basis)
        has_vacuum_gap = max_gap_cartesian >= threshold
        gaps[axis] = has_vacuum_gap

    return gaps


def get_center_of_mass(system, weight=True):
    """
    """
    positions = system.get_positions()
    if weight:
        weights = system.get_masses()
    else:
        weights = np.ones((len(system)))
    cm = np.dot(weights, positions/weights.sum())

    return cm


def get_space_filling(system):
    """Calculates the ratio of vacuum to filled space by assuming covalent
    radii for the atoms.

    Args:
        system(ASE.Atoms): Atomic system.

    Returns:
        float: The ratio of occupied volume to the cell volume.
    """
    cell_volume = system.get_volume()
    atomic_numbers = system.get_atomic_numbers()
    occupied_volume = 0
    radii = get_covalent_radii(atomic_numbers)
    volumes = 4.0/3.0*np.pi*radii**3
    occupied_volume = np.sum(volumes)
    ratio = occupied_volume/cell_volume

    return ratio


def make_random_displacement(system, delta, rng=None):
    """Dislocate every atom in the given system in a random direction but by
    the same amount. Uses an internal random number generator to avoid touching
    the global numpy.random.seed()-function.

    Args:
        system(ASE.Atoms): The system for which the displacement are performed.
        delta(float): The magnitude of the displacements.
        rng(np.random.RandomState): Random number generator.
    """
    if rng is None:
        rng = RandomState()
    pos = system.get_positions()
    n_atoms = len(system)
    disloc = rng.rand(n_atoms, 3)
    disloc /= np.linalg.norm(disloc, axis=1)[:, None]
    disloc *= delta
    new_pos = pos + disloc
    system.set_positions(new_pos)


def get_extended_system(system, target_size):
    """Replicate the system in different directions to reach a suitable
    system size for getting the moments of inertia.

    Args:
        system (ase.Atoms): The original system.
        target_size (float): The target size for the extended system.

    Returns:
        ase.Atoms: The extended system.
    """
    pbc = system.get_pbc()
    cell = system.get_cell()

    repetitions = np.array([1, 1, 1])
    for i, pbc in enumerate(pbc):
        # Only extend in the periodic dimensions
        basis = cell[i, :]
        if pbc:
            size = np.linalg.norm(basis)
            i_repetition = np.maximum(np.round(target_size/size), 1).astype(int)
            repetitions[i] = i_repetition

    extended_system = system.repeat(repetitions)

    return extended_system


def get_clusters(system, distance_matrix, threshold):
    """
    """
    # Detect clusters
    db = DBSCAN(eps=threshold, min_samples=1, metric='precomputed', n_jobs=1)
    db.fit(distance_matrix)
    clusters = db.labels_

    # Make a list of the different clusters
    idx_sort = np.argsort(clusters)
    sorted_records_array = clusters[idx_sort]
    vals, idx_start, count = np.unique(sorted_records_array, return_counts=True,
                                    return_index=True)
    cluster_indices = np.split(idx_sort, idx_start[1:])

    return cluster_indices


def get_covalent_distances(system, mic=True):
    """Returns a distance matrix where the covalent radii have been taken into
    account. Clips negative values to be zero.
    """
    if system is not None:
        if len(system) == 1:
            return np.array([[0]])

        # Calculate distance matrix with radii taken into account
        distance_matrix = system.get_all_distances(mic=mic)

    # Remove the radii from distances and clip out negative values
    numbers = system.get_atomic_numbers()
    radii = covalent_radii[numbers]
    radii_matrix = radii[None, :] + radii[:, None]
    distance_matrix -= radii_matrix
    np.clip(distance_matrix, 0, None, out=distance_matrix)

    return distance_matrix


def get_biggest_gap_indices(coordinates):
    """Given the list of coordinates for one axis, this function will find the
    maximum gap between them and return the index of the bottom and top
    coordinates. The bottom and top are defined as:

    ===       ===============    --->
        ^top    ^bot               ^axis direction
    """
    # Find the maximum vacuum gap for all basis vectors
    sorted_indices = np.argsort(coordinates)
    sorted_comp = coordinates[sorted_indices]
    rolled_comp = np.roll(sorted_comp, 1, axis=0)
    distances = sorted_comp - rolled_comp

    # The first distance is from first to last, so it needs to be
    # wrapped around
    distances[0] += 1

    # Find maximum gap
    bottom_index = sorted_indices[np.argmax(distances)]
    top_index = sorted_indices[np.argmax(distances)-1]

    return bottom_index, top_index


def get_dimensions(system, vacuum_gaps):
    """Given a system with vacuum gaps, calculate its dimensions in the
    directions with vacuum gaps by also taking into account the atomic radii.
    """
    orig_cell_lengths = np.linalg.norm(system.get_cell(), axis=1)

    # Create a repeated copy of the system. The repetition is needed in order
    # to get gaps to neighbouring cell copies in the periodic dimensions with a
    # vacuum gap
    sys = system.copy()
    sys = sys.repeat([2, 2, 2])

    dimensions = [None, None, None]
    numbers = sys.get_atomic_numbers()
    positions = sys.get_scaled_positions()
    radii = covalent_radii[numbers]
    cell_lengths = np.linalg.norm(sys.get_cell(), axis=1)
    radii_in_cell_basis = radii[:, None]/cell_lengths[None, :]

    for i_dim, vacuum_gap in enumerate(vacuum_gaps):
        if vacuum_gap:
            # Make a data structure containing the atom location information as
            # intervals from one side of the atom to the other in each
            # dimension.
            intervals = Intervals()
            for i_pos, pos in enumerate(positions[:, i_dim]):
                i_radii = radii_in_cell_basis[i_pos, i_dim]
                i_axis_start = pos - i_radii
                i_axis_end = pos + i_radii
                intervals.add_interval(i_axis_start, i_axis_end)

            # Calculate the maximum distance between atoms, when taking radius
            # into account
            gap = intervals.get_max_distance_between_intervals()
            gap = gap*cell_lengths[i_dim]
            dimensions[i_dim] = orig_cell_lengths[i_dim] - gap

    return dimensions


def get_wrapped_positions(scaled_pos, precision=1E-5):
    """Wrap the given relative positions so that each element in the array
    is within the half-closed interval [0, 1)

    By wrapping values near 1 to 0 we will have a consistent way of
    presenting systems.
    """
    scaled_pos %= 1

    abs_zero = np.absolute(scaled_pos)
    abs_unity = np.absolute(abs_zero-1)

    near_zero = np.where(abs_zero < precision)
    near_unity = np.where(abs_unity < precision)

    scaled_pos[near_unity] = 0
    scaled_pos[near_zero] = 0

    return scaled_pos


def get_distance_matrix(pos1, pos2, cell=None, pbc=None, mic=False):
    """Calculates the distance matrix. If wrap_distances=True, calculates
    the matrix using periodic distances

    Args:
        pos1(np.ndarray): Array of cartesian positions
        pos2(np.ndarray): Array of cartesian positions
        cell():
        pbc():
        mic (bool): Whether to apply minimum image convention fo the distances,
            i.e. the distance to the closest periodic image is returned.
    """
    disp_tensor = get_displacement_tensor(pos1, pos2, cell, pbc, mic)
    distance_matrix = np.linalg.norm(disp_tensor, axis=2)

    return distance_matrix


def get_displacement_tensor_old(pos1, pos2, cell=None, pbc=None, mic=False, return_factors=False, return_distances=False):
    """Given an array of positions, calculates the 3D displacement tensor
    between the positions.

    The displacement tensor is a matrix where the entry A[i, j, :] is the
    vector pos1[i] - pos2[j], i.e. the vector from pos2 to pos1

    Args:
        pos1(np.ndarray): 2D array of positions
        pos2(np.ndarray): 2D array of positions
        cell(np.ndarray): Cell for taking into account the periodicity
        pbc(boolean or a list of booleans): Periodicity of the axes
        mic(boolean): Whether to return the displacement to the nearest
            periodic copy

    Returns:
        np.ndarray: 3D displacement tensor
    """
    if mic and cell is not None and pbc is not None:
        pbc = expand_pbc(pbc)
        if pbc.any():
            if cell is None:
                raise ValueError(
                    "When using periodic boundary conditions you must provide "
                    "the cell."
                )
    elif not mic and cell is None and pbc is None:
        pass
    else:
        raise ValueError(
            "Invalid arguments given. Either supply only cartesian positions, "
            "or if you wish to apply the minimum image convention please supply"
            " also cell, periodic boundary conditions and set mic to True"
        )

    # Make 1D into 2D
    shape1 = pos1.shape
    shape2 = pos2.shape
    if len(shape1) == 1:
        n_cols1 = len(pos1)
        pos1 = np.reshape(pos1, (-1, n_cols1))
    if len(shape2) == 1:
        n_cols2 = len(pos2)
        pos2 = np.reshape(pos2, (-1, n_cols2))

    # Add new axes so that broadcasting works nicely
    if mic:
        rel_pos1 = to_scaled(cell, pos1)
        rel_pos2 = to_scaled(cell, pos2)
        disp_tensor = rel_pos1[:, None, :] - rel_pos2[None, :, :]

        if return_factors:
            factors = np.floor(np.array(disp_tensor) + 0.5)
        disp_tensor = get_mic_positions(disp_tensor, cell, pbc)
    else:
        disp_tensor = pos1[:, None, :] - pos2[None, :, :]

    if return_distances:
        dist_matrix = np.linalg.norm(disp_tensor, axis=2)

    if return_factors and return_distances:
        return disp_tensor, factors, dist_matrix
    elif return_factors:
        return disp_tensor, factors
    elif return_distances:
        return disp_tensor, dist_matrix
    else:
        return disp_tensor


def get_displacement_tensor(
        pos1,
        pos2,
        cell=None,
        pbc=None,
        mic=False,
        return_factors=False,
        return_distances=False
    ):
    """Given an array of positions, calculates the 3D displacement tensor
    between the positions.

    The displacement tensor is a matrix where the entry A[i, j, :] is the
    vector pos1[i] - pos2[j], i.e. the vector from pos2 to pos1

    Args:
        pos1(np.ndarray): 2D array of positions
        pos2(np.ndarray): 2D array of positions
        cell(np.ndarray): Cell for taking into account the periodicity
        pbc(boolean or a list of booleans): Periodicity of the axes
        mic(boolean): Whether to return the displacement to the nearest
            periodic copy

    Returns:
        np.ndarray: 3D displacement tensor
        (optional) np.ndarray: The indices of the periodic copies in which the
            minimum image was found
        (optional) np.ndarray: The lengths of the displacement vectors
    """
    # Make 1D into 2D
    shape1 = pos1.shape
    shape2 = pos2.shape
    if len(shape1) == 1:
        n_cols1 = len(pos1)
        pos1 = np.reshape(pos1, (-1, n_cols1))
    if len(shape2) == 1:
        n_cols2 = len(pos2)
        pos2 = np.reshape(pos2, (-1, n_cols2))

    # Calculate the pairwise distance vectors
    disp_tensor = pos1[:, None, :] - pos2[None, :, :]
    tensor_shape = np.array(disp_tensor.shape)

    # If minimum image convention is used, get the corrected vectors
    if mic:
        flattened_disp = np.reshape(disp_tensor, (-1, 3))
        D, D_len, factors = find_mic(flattened_disp, cell, pbc)
        disp_tensor = np.reshape(D, tensor_shape)
        if return_factors:
            factors = np.reshape(factors, tensor_shape)
        if return_distances:
            lengths = np.reshape(D_len, (tensor_shape[0], tensor_shape[1]))

    if return_factors and return_distances:
        return disp_tensor, factors, lengths
    elif return_factors:
        return disp_tensor, factors
    elif return_distances:
        return disp_tensor, lengths
    else:
        return disp_tensor


def find_mic(D, cell, pbc=True):
    """Finds the minimum-image representation of vector(s) D"""

    cell = ase.geometry.complete_cell(cell)
    n_vectors = len(D)

    # Calculate the 4 unique unit cell diagonal lengths
    diags = np.sqrt((np.dot([[1, 1, 1],
                             [-1, 1, 1],
                             [1, -1, 1],
                             [-1, -1, 1],
                             ], cell)**2).sum(1))

    Dr = np.dot(D, np.linalg.inv(cell))

    # calculate 'mic' vectors (D) and lengths (D_len) using simple method
    # return mic vectors and lengths for only orthorhombic cells,
    # as the results may be wrong for non-orthorhombic cells
    if (max(diags) - min(diags)) / max(diags) < 1e-9:

        factors = np.floor(Dr + 0.5)*pbc
        D = np.dot(Dr - factors, cell)
        D_len = np.linalg.norm(D, axis=1)
        return D, D_len, factors
    # Non-orthorhombic cell
    else:
        D_len = np.linalg.norm(D, axis=1)

    # The cutoff radius is the longest direct distance between atoms
    # or half the longest lattice diagonal, whichever is smaller
    cutoff = min(max(D_len), max(diags) / 2.)

    # The number of neighboring images to search in each direction is
    # equal to the ceiling of the cutoff distance (defined above) divided
    # by the length of the projection of the lattice vector onto its
    # corresponding surface normal. a's surface normal vector is e.g.
    # b x c / (|b| |c|), so this projection is (a . (b x c)) / (|b| |c|).
    # The numerator is just the lattice volume, so this can be simplified
    # to V / (|b| |c|). This is rewritten as V |a| / (|a| |b| |c|)
    # for vectorization purposes.
    latt_len = np.linalg.norm(cell, axis=1)
    V = abs(np.linalg.det(cell))
    n = pbc * np.array(np.ceil(cutoff * np.prod(latt_len) /
                               (V * latt_len)), dtype=int)

    # Construct a list of translation vectors. For example, if we are
    # searching only the nearest images (27 total), tvecs will be a
    # 27x3 array of translation vectors. This is the only nested loop
    # in the routine, and it takes a very small fraction of the total
    # execution time, so it is not worth optimizing further.
    tvecs = []
    tvec_factors = []
    for i in range(-n[0], n[0] + 1):
        latt_a = i * cell[0]
        for j in range(-n[1], n[1] + 1):
            latt_ab = latt_a + j * cell[1]
            for k in range(-n[2], n[2] + 1):
                tvecs.append(latt_ab + k * cell[2])
                tvec_factors.append([i, j, k])
    tvecs = np.array(tvecs)
    tvec_factors = np.array(tvec_factors)

    # Translate the direct displacement vectors by each translation
    # vector, and calculate the corresponding lengths.
    D_trans = tvecs[np.newaxis] + D[:, np.newaxis]
    D_trans_len = np.linalg.norm(D_trans, axis=2)

    # Find mic distances and corresponding vector(s) for each given pair
    # of atoms. For symmetrical systems, there may be more than one
    # translation vector corresponding to the MIC distance; this finds the
    # first one in D_trans_len.
    D_min_ind = D_trans_len.argmin(axis=1)
    D_min_len = D_trans_len[list(range(n_vectors)), D_min_ind]
    D_min = D_trans[list(range(n_vectors)), D_min_ind]
    factors = tvec_factors[D_min_ind, :]

    # Negate the factors because of the order of the displacement
    factors *= -1

    return D_min, D_min_len, factors


def get_mic_positions(disp_tensor_rel, cell, pbc):
    """Used to wrap positions so that the minimum image convention is valid,
    i.e. the distances are to the nearest periodic neighbour.
    """
    wrapped_disp_tensor = np.array(disp_tensor_rel)
    for i, periodic in enumerate(pbc):
        if periodic:
            i_disp_tensor = disp_tensor_rel[:, :, i]
            factors = np.floor(i_disp_tensor + 0.5)
            i_disp_tensor -= factors
            wrapped_disp_tensor[:, :, i] = i_disp_tensor

            # pos_mask = i_disp_tensor > 0.5
            # i_disp_tensor[pos_mask] = i_disp_tensor[pos_mask] - 1
            # neg_mask = i_disp_tensor < -0.5
            # i_disp_tensor[neg_mask] = i_disp_tensor[neg_mask] + 1
            # wrapped_disp_tensor[:, :, i] = i_disp_tensor
    disp_tensor_cart = np.dot(wrapped_disp_tensor, cell)

    return disp_tensor_cart


def expand_pbc(pbc):
    """Used to expand a pbc definition into an array of three booleans.

    Args:
        pbc(boolean or a list of booleans): The periodicity of the cell. This
            can be any of the values that is also supprted by ASE, namely: a
            boolean or a list of three booleans.

    Returns:
        np.ndarray of booleans: The periodicity expanded as an explicit list of
        three boolean values.
    """
    if pbc is True:
        new_pbc = [True, True, True]
    elif pbc is False:
        new_pbc = [False, False, False]
    elif len(pbc) == 3:
        new_pbc = pbc
    else:
        raise ValueError(
            "Could not interpret the given periodic boundary conditions: '{}'"
            .format(pbc)
        )

    return np.array(new_pbc)


def change_basis(positions, basis, offset=None):
    """Transform the given cartesian coordinates to a basis that is defined by
    the given basis and origin offset.

    Args:
        positions(np.ndarray): Positions in cartesian coordinates.
        basis(np.ndarray): Basis to which to transform.
        offset(np.ndarray): Offset of the origins. A vector from the old basis
            origin to the new basis origin.
    Returns:
        np.ndarray: Relative positions in the new basis
    """

    if offset is not None:
        positions -= offset
    new_basis_inverse = np.linalg.inv(basis.T)
    pos_prime = np.dot(positions, new_basis_inverse.T)

    return pos_prime


def get_positions_within_basis(
        system,
        basis,
        origin,
        tolerance_low,
        tolerance_high,
        mask=[True, True, True],
        pbc=True
    ):
    """Used to return the indices of positions that are inside a certain basis.
    Also takes periodic boundaries into account.

    Args:
        system(ASE.Atoms): System from which the positions are searched.
        basis(np.ndarray): New basis vectors.
        origin(np.ndarray): New origin of the basis in cartesian coordinates.
        tolerance(float): The tolerance for the end points of the cell.
        mask(sequence of bool): Mask for selecting the basis's to consider.
        pbc(sequence of bool): The periodicity of the system.

    Returns:
        sequence of int: Indices of the atoms within this cell in the given
            system.
        np.ndarray: Relative positions of the found atoms.
        np.ndarray: The index of the periodic copy in which the position was
            found.
    """
    # If the search extend beyound the cell boundary and periodic boundaries
    # allow, we must divide the search area into multiple regions

    # Transform positions into the new basis
    cart_pos = system.get_positions()
    orig_cell = system.get_cell()

    pbc = expand_pbc(pbc)

    # See if the new positions extend beyound the boundaries. The original
    # simulation cell is always convex, so we can just check the corners of
    # unit cell defined by the basis
    max_a = origin + basis[0, :]
    max_b = origin + basis[1, :]
    max_c = origin + basis[1, :]
    max_ab = origin + basis[0, :] + basis[1, :]
    max_ac = origin + basis[0, :] + basis[2, :]
    max_bc = origin + basis[1, :] + basis[2, :]
    max_abc = origin + basis[0, :] + basis[1, :] + basis[2, :]
    vectors = np.array((max_a, max_b, max_c, max_ab, max_ac, max_bc, max_abc))
    rel_vectors = to_scaled(orig_cell, vectors, wrap=False, pbc=system.get_pbc())

    directions = set()
    directions.add((0, 0, 0))
    for vec in rel_vectors:
        i_direction = tuple(np.floor(vec))
        a_per = i_direction[0]
        b_per = i_direction[1]
        c_per = i_direction[2]
        allow = True
        if a_per != 0 and not pbc[0]:
            allow = False
        if b_per != 0 and not pbc[1]:
            allow = False
        if c_per != 0 and not pbc[2]:
            allow = False
        if allow:
            if i_direction != (0, 0, 0):
                directions.add(i_direction)

    # If the new cell is overflowing beyound the boundaries of the original
    # system, we have to also check the periodic copies.
    indices = []
    a_prec_low, b_prec_low, c_prec_low = tolerance_low/np.linalg.norm(basis, axis=1)
    a_prec_high, b_prec_high, c_prec_high = tolerance_high/np.linalg.norm(basis, axis=1)
    orig_basis = system.get_cell()
    cell_pos = []
    factors = []
    for i_dir in directions:

        vec_new_cart = cart_pos + np.dot(i_dir, orig_basis)
        vec_new_rel = change_basis(vec_new_cart - origin, basis)

        # If no positions are defined, find the atoms within the cell
        for i_pos, pos in enumerate(vec_new_rel):
            if mask[0]:
                x = 0 - a_prec_low <= pos[0] <= 1 - a_prec_high
            else:
                x = True
            if mask[1]:
                y = 0 - b_prec_low <= pos[1] <= 1 - b_prec_high
            else:
                y = True
            if mask[2]:
                z = 0 - c_prec_low <= pos[2] <= 1 - c_prec_high
            else:
                z = True

            if x and y and z:
                indices.append(i_pos)
                cell_pos.append(pos)
                factors.append(i_dir)

    cell_pos = np.array(cell_pos)
    indices = np.array(indices)
    factors = np.array(factors)

    return indices, cell_pos, factors


def get_matches(
        system,
        positions,
        numbers,
        tolerance):
    """Given a system and a list of cartesian positions and atomic numbers,
    returns a list of indices for the atoms corresponding to the given
    positions with some tolerance.

    Args:
        system(ASE.Atoms): System where to search the positions
        positions(np.ndarray): Positions to match in the system.
        tolerance(float): Maximum allowed distance that is required for a
            match in position.

    Returns:
        np.ndarray: indices of matched atoms
        list: list of substitutions
        list: list of vacancies
        np.ndarray: for each searched position, an integer array representing
            the number of the periodic copy where the match was found.
    """
    orig_num = system.get_atomic_numbers()
    orig_pos = system.get_positions()
    cell = system.get_cell()
    pbc = system.get_pbc()
    pbc = expand_pbc(pbc)
    scaled_pos2 = to_scaled(cell, positions, wrap=False)

    disp_tensor, factors, dist_matrix = get_displacement_tensor(
        positions,
        orig_pos,
        cell,
        pbc,
        mic=True,
        return_factors=True,
        return_distances=True
    )

    min_ind = np.argmin(dist_matrix, axis=1)
    matches = []
    substitutions = []
    vacancies = []
    copy_indices = []

    for i, ind in enumerate(min_ind):
        distance = dist_matrix[i, ind]
        a_num = orig_num[ind]
        b_num = numbers[i]
        match = None
        copy = None
        if distance <= tolerance:
            if a_num == b_num:
                match = ind
            else:
                # Wrap the substitute position
                # subst_pos = np.array(scaled_pos2[i])
                # subst_pos %= 1
                # subst_pos_cart = np.dot(subst_pos, cell)
                subst_pos_cart = orig_pos[i]
                substitutions.append(Substitution(ind, subst_pos_cart, b_num, a_num))

            # If a match was found the factor is reported based on the
            # displacement tensor
            i_move = factors[i][ind]
            copy = i_move
        else:
            vacancies.append(Atom(b_num, position=positions[i]))

            # If no match was found, the factor is reported from the scaled
            # positions
            copy = np.floor(scaled_pos2[i])

        matches.append(match)
        copy_indices.append(copy)

    return matches, substitutions, vacancies, copy_indices


def get_matches_old(
        system,
        positions,
        numbers,
        tolerance):
    """Given a system and a list of cartesian positions and atomic numbers,
    returns a list of indices for the atoms corresponding to the given
    positions with some tolerance.

    Args:
        system(ASE.Atoms): System where to search the positions
        positions(np.ndarray): Positions to match in the system.
        tolerance(float): Maximum allowed distance that is required for a
            match in position.

    Returns:
        np.ndarray: indices of matched atoms
        list: list of substitutions
        list: list of vacancies
        np.ndarray: for each searched position, an integer array representing
            the number of the periodic copy where the match was found.
    """
    orig_num = system.get_atomic_numbers()
    cell = system.get_cell()
    scaled_pos1 = system.get_scaled_positions()
    scaled_pos2 = to_scaled(cell, positions, wrap=False)

    # Calculate displacement tensor and the factors
    disp_tensor = get_displacement_tensor(scaled_pos2, scaled_pos1)

    # Calculate the factors
    factors = np.floor(disp_tensor + 0.5)

    # # Wrap the displacement tensor
    disp_tensor -= factors

    # Calculate the cartesian distance_matrix
    disp_tensor = np.dot(disp_tensor, cell)
    distance_matrix = np.linalg.norm(disp_tensor, axis=2)

    min_ind = np.argmin(distance_matrix, axis=1)
    matches = []
    substitutions = []
    vacancies = []
    copy_indices = []

    for i, ind in enumerate(min_ind):
        distance = distance_matrix[i, ind]
        a_num = orig_num[ind]
        b_num = numbers[i]
        match = None
        copy = None
        if distance <= tolerance:
            if a_num == b_num:
                match = ind
            else:
                # Wrap the substitute position
                subst_pos = np.array(scaled_pos2[i])
                subst_pos %= 1
                subst_pos_cart = np.dot(subst_pos, cell)
                substitutions.append(Substitution(ind, subst_pos_cart, b_num, a_num))

            # If a match was found the factor is reported based on the
            # displacement tensor
            i_move = factors[i][ind]
            copy = i_move
        else:
            vacancies.append(Atom(b_num, position=positions[i]))

            # If no match was found, the factor is reported from the scaled
            # positions
            i_move = np.floor(scaled_pos2[i])
            copy = i_move

        matches.append(match)
        copy_indices.append(copy)

    return matches, substitutions, vacancies, copy_indices


def to_scaled(cell, positions, wrap=False, pbc=False):
    """Used to transform a set of positions to the basis defined by the
    cell of this system.

    Args:
        system(ASE.Atoms): Reference system.
        positions (numpy.ndarray): The positions to scale
        wrap (numpy.ndarray): Whether the positions should be wrapped
            inside the cell.

    Returns:
        numpy.ndarray: The scaled positions
    """
    # Force 1D to 2D
    if len(positions.shape) == 1:
        positions = positions[None, :]
    pbc = expand_pbc(pbc)
    fractional = np.linalg.solve(
        cell.T,
        positions.T).T

    if wrap:
        for i, periodic in enumerate(pbc):
            if periodic:
                fractional[:, i] %= 1.0

    return fractional


def to_cartesian(cell, scaled_positions, wrap=False, pbc=False):
    """Used to transofrm a set of relative positions to the cartesian basis
    defined by the cell of this system.

    Args:
        system (ASE.Atoms): Reference system.
        positions (numpy.ndarray): The positions to scale
        wrap (numpy.ndarray): Whether the positions should be wrapped
            inside the cell.

    Returns:
        numpy.ndarray: The cartesian positions
    """
    pbc = expand_pbc(pbc)
    if wrap:
        for i, periodic in enumerate(pbc):
            if periodic:
                scaled_positions[:, i] %= 1.0

    cartesian_positions = np.dot(scaled_positions, cell)
    return cartesian_positions


def translate(system, translation, relative=False):
    """Translates the positions by the given translation.

    Args:
        translation (1x3 numpy.array): The translation to apply.
        relative (bool): True if given translation is relative to cell
            vectors.
    """
    if relative:
        rel_pos = system.get_scaled_positions()
        rel_pos += translation
        system.set_scaled_positions(rel_pos)
    else:
        cart_pos = system.get_positions()
        cart_pos += translation
        system.set_positions(cart_pos)


def get_surface_normal_direction(system):
    """Used to estimate a normal vector for a 2D like structure.

    Args:
        system (ase.Atoms): The system to examine.

    Returns:
        np.ndarray: The estimated surface normal vector
    """
    repeated = get_extended_system(system, 15)
    # vectors = system.get_cell()

    # Get the eigenvalues and eigenvectors of the moment of inertia tensor
    val, vec = get_moments_of_inertia(repeated)
    sorted_indices = np.argsort(val)
    val = val[sorted_indices]
    vec = vec[sorted_indices]

    # If the moment of inertia is not significantly bigger in one
    # direction, then the system cannot be described as a surface.
    moment_limit = 1.5
    if val[-1] < moment_limit*val[0] and val[-1] < moment_limit*val[1]:
        raise ValueError(
            "The given system could not be identified as a surface. Make"
            " sure that you provide a surface system with a sufficient"
            " vacuum gap between the layers (at least ~8 angstroms of vacuum"
            " between layers.)"
        )

    # The biggest component is the orhogonal one
    orthogonal_dir = vec[-1]

    return orthogonal_dir

    # Find out the cell direction that corresponds to the orthogonal one
    # cell = repeated.get_cell()
    # dots = np.abs(np.dot(orthogonal_dir, vectors.T))
    # orthogonal_vector_index = np.argmax(dots)
    # orthogonal_vector = vectors[orthogonal_vector_index]
    # orthogonal_dir = orthogonal_vector/np.linalg.norm(orthogonal_vector)

    return orthogonal_dir


def get_closest_direction(vec, directions, normalized=False):
    """Used to return the direction that is most parallel to a given one.

    Args:

    Returns:
    """
    if not normalized:
        directions = directions/np.linalg.norm(directions, axis=1)
    dots = np.abs(np.dot(vec, directions.T))
    index = np.argmax(dots)

    return index


class Intervals(object):
    """Handles list of intervals.

    This class allows sorting and adding up of intervals and taking into
    account if they overlap.
    """
    def __init__(self, intervals=None):
        """Args:
            intervals: List of intervals that are added.
        """
        self._intervals = []
        self._merged_intervals = []
        self._merged_intervals_need_update = True
        if intervals is not None:
            self.add_intervals(intervals)

    def _add_up(self, intervals):
        """Add up the length of intervals.

        Argument:
            intervals: List of intervals that are added up.

        Returns:
            Result of addition.
        """
        if len(intervals) < 1:
            return None
        result = 0.
        for interval in intervals:
            result += abs(interval[1] - interval[0])
        return result

    def add_interval(self, a, b):
        """Add one interval.

        Args:
            a, b: Start and end of interval. The order does not matter.
        """
        self._intervals.append((min(a, b), max(a, b)))
        self._merged_intervals_need_update = True

    def add_intervals(self, intervals):
        """Add list of intervals.

        Args:
            intervals: List of intervals that are added.
        """
        for interval in intervals:
            if len(interval) == 2:
                self.add_interval(interval[0], interval[1])
            else:
                raise ValueError("Intervals must be tuples of length 2!")

    def set_intervals(self, intervals):
        """Set list of intervals.

        Args:
            intervals: List of intervals that are set.
        """
        self._intervals = []
        self.add_intervals(intervals)

    def remove_interval(self, i):
        """Remove one interval.

        Args:
            i: Index of interval that is removed.
        """
        try:
            del self._intervals[i]
            self._merged_intervals_need_update = True
        except IndexError:
            pass

    def get_intervals(self):
        """Returns the intervals.
        """
        return self._intervals

    def get_intervals_sorted_by_start(self):
        """Returns list with intervals ordered by their start.
        """
        return sorted(self._intervals, key=lambda x: x[0])

    def get_intervals_sorted_by_end(self):
        """Returns list with intervals ordered by their end.
        """
        return sorted(self._intervals, key=lambda x: x[1])

    def get_merged_intervals(self):
        """Returns list of merged intervals so that they do not overlap anymore.
        """
        if self._merged_intervals_need_update:
            if len(self._intervals) < 1:
                return self._intervals
            # sort intervals in list by their start
            sorted_by_start = self.get_intervals_sorted_by_start()
            # add first interval
            merged = [sorted_by_start[0]]
            # start from second interval
            for current in sorted_by_start[1:]:
                previous = merged[-1]
                # new interval if not current and previous are not overlapping
                if previous[1] < current[0]:
                    merged.append(current)
                # merge if current and previous are overlapping and if end of previous is expanded by end of current
                elif previous[1] < current[1]:
                    merged[-1] = (previous[0], current[1])
            self._merged_intervals = merged
            self._merged_intervals_need_update = False
        return self._merged_intervals

    def get_max_distance_between_intervals(self):
        """Returns the maximum distance between the intervals while accounting for overlap.
        """
        if len(self._intervals) < 2:
            return None
        merged_intervals = self.get_merged_intervals()
        distances = []
        if len(merged_intervals) == 1:
            return 0.0
        for i in range(len(merged_intervals) - 1):
            distances.append(abs(merged_intervals[i + 1][0] - merged_intervals[i][1]))
        return max(distances)

    def add_up_intervals(self):
        """Returns the added up lengths of intervals without accounting for overlap.
        """
        return self._add_up(self._intervals)

    def add_up_merged_intervals(self):
        """Returns the added up lengths of merged intervals in order to account for overlap.
        """
        return self._add_up(self.get_merged_intervals())
