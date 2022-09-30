"""
Author: Salvatore Mandra (salvatore.mandra@nasa.gov)

Copyright © 2021, United States Government, as represented by the Administrator
of the National Aeronautics and Space Administration. All rights reserved.

The HybridQ: A Hybrid Simulator for Quantum Circuits platform is licensed under
the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

Types
-----
**`Array`**: `numpy.ndarray`
"""

from __future__ import annotations
from hybridq.utils import sort, argsort
import numpy as np
import numba


@numba.vectorize
def _parity(v):
    v ^= v >> 16
    v ^= v >> 8
    v ^= v >> 4
    v &= 0xf
    if (0x6996 >> v) & 1:
        return -1
    else:
        return 1


def prepare_state(state: str,
                  d: {int, iter[int]} = 2,
                  complex_type: any = 'complex64',
                  reshape: bool = True):
    """
    Prepare initial state accordingly to `state`.

    Parameters
    ----------
    state: str
        State used to prepare the quantum state. If `state` is a string, a
        quantum state of `len(str)` is created using the following notation:

        - `0`: qubit is set to `0` in the computational basis,
        - `1`: qubit is set to `1` in the computational basis,
        - `+`: qubit is set to `+` state in the computational basis,
        - `-`: qubit is set to `-` state in the computational basis.
    d: {int, iter[int]}
        Dimensions of qubits.
    complex_type: any, optional
        Complex type to use to prepare the quantum state.

    Returns
    -------
    Array
        Quantum state prepared from `state`.

    Example
    -------
    >>> prepare_state('+-+')
    array([ 0.35355338+0.j,  0.35355338+0.j, -0.35355338+0.j, -0.35355338+0.j,
            0.35355338+0.j,  0.35355338+0.j, -0.35355338+0.j, -0.35355338+0.j],
          dtype=complex64)
    """
    # Convert state to str
    try:
        state = str(state)
    except:
        raise ValueError("'state' must be convertible to 'str'.")

    # Get dimensions
    try:
        d = (int(d),) * len(state)
    except:
        d = tuple(int(x) for x in d)

    # Check that only allowed symbols are contained
    if set(state).difference('+-01'):
        raise ValueError(
            f"Symbols {set(state).difference('+-01')} are not allowed.")

    # Check no dimensions are zero
    if (isinstance(d, int) and d <= 0) or (isinstance(d, tuple) and
                                           any(d <= 0 for d in d)):
        raise ValueError("All dimensions must be positive")

    # Check n_qubits and dimensions are consistent
    if len(d) != len(state):
        raise ValueError("Number of qubits and dimensions are not consistent.")

    # Get dimensions
    d_a0 = tuple(d for d, b in zip(d, state) if b in '0')
    d_a1 = tuple(d for d, b in zip(d, state) if b in '1')
    d_p = tuple(d for d, b in zip(d, state) if b == '+')
    d_n = tuple(d for d, b in zip(d, state) if b == '-')

    # Get size
    p_a0 = np.prod(d_a0).astype(int)
    p_a1 = np.prod(d_a1).astype(int)
    p_p = np.prod(d_p).astype(int)
    p_n = np.prod(d_n).astype(int)

    # Get number of dimensions
    n_a0 = len(d_a0)
    n_a1 = len(d_a1)
    n_p = len(d_p)
    n_n = len(d_n)

    # Simple cases
    if n_p == n_n == 0:
        # Initialize in the computational basis
        q_state = np.zeros(p_a0 * p_a1, dtype=complex_type)
        q_state[int(state, 2)] = 1

    elif n_a0 == n_a1 == n_n:
        # Initialize to superposition
        q_state = np.ones(p_p, dtype=complex_type) / np.sqrt(p_p)

    else:
        # Get order
        order = argsort(state,
                        key=lambda x: {
                            '0': 0,
                            '1': 1,
                            '+': 2,
                            '-': 3
                        }[x])
        order = [order.index(i) for i in range(len(order))]

        # Check
        assert (n_a0 + n_a1 + n_p + n_n == len(state))

        # Initialize state
        q_state = np.zeros((p_a0 * p_a1, p_p, p_n), dtype=complex_type)

        # Assign state
        q_state[p_a1 - 1] = np.reshape(
            np.kron(np.ones(p_p), _parity(np.arange(p_n))) / np.sqrt(p_p * p_n),
            (p_p, p_n))

        # Transpose
        q_state = np.transpose(np.reshape(q_state, d_a0 + d_a1 + d_p + d_n),
                               order).ravel()

    # Return state
    return np.reshape(q_state, d) if reshape else q_state
