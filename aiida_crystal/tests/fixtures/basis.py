#  Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""
Pytest fixtures dealing with basis sets
"""

import os
import pytest


@pytest.fixture
def test_basis(aiida_profile):
    from aiida.common.exceptions import NotExistent
    from aiida_crystal.tests import TEST_DIR
    from aiida_crystal.data.basis_set import BasisSetData
    upload_basisset_family = BasisSetData.upload_basisset_family
    try:
        BasisSetData.get_basis_group('sto-3g')
    except NotExistent:
        upload_basisset_family(
            os.path.join(TEST_DIR, "input_files", "sto3g"),
            "sto-3g",
            "minimal basis sets",
            stop_if_existing=True,
            extension=".basis")

    return BasisSetData.get_basis_group_map('sto-3g')
