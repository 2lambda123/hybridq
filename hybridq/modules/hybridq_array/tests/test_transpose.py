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
"""
from hybridq_array.linalg import transpose
import numpy as np
import pytest


@pytest.fixture(autouse=True)
def set_seed():
    from numpy import random
    from os import environ
    from sys import stderr

    # Get random seed
    seed = random.randint(2**32 - 1)

    # Get state
    state = random.get_state()

    # Set seed
    random.seed(seed)

    # Print seed
    print(f"# Used seed [{environ['PYTEST_CURRENT_TEST']}]: {seed}",
          file=stderr)

    # Wait for PyTest
    yield

    # Set state
    random.set_state(state)


@pytest.mark.parametrize('type,ndim,npos', ([type, ndim, npos] for type in [
    'float', 'float16', 'float32', 'float64', 'float128', 'int8', 'int16',
    'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'complex64',
    'complex128'
] for ndim in [10, 16] for npos in [2, 4, 6, 8, 10]))
def test_transpose(type, ndim, npos):
    # Get random array
    a = (1000 * np.random.random((2,) * ndim)).astype(type)

    # Get imaginary part
    if np.iscomplexobj(a):
        a += 1j * np.random.random((2,) * ndim)

    # Get random permutation
    axes = np.random.permutation(npos)
    axes = np.concatenate(
        [np.arange(a.ndim - axes.size), a.ndim - axes[::-1] - 1])

    # Check transposition
    np.testing.assert_allclose(np.transpose(a, axes), transpose(a, axes))