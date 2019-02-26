#   Copyright (c)  Andrey Sobolev, 2019. Distributed under MIT license, see LICENSE file.
"""Tests for properties parser
"""

# noinspection PyUnresolvedReferences
from aiida_crystal.tests.fixtures import *


def test_properties_parser(properties_calc, properties_calc_results):
    # from aiida.orm import DataFactory
    from aiida_crystal.parsers.properties import PropertiesParser
    parser = PropertiesParser(properties_calc)
    assert properties_calc._PROPERTIES_FILE in properties_calc_results.get_content_list()
    _, nodes = parser.parse_with_retrieved({"retrieved": properties_calc_results})
    nodes = dict(nodes)
    assert nodes
    # wavefunction tests
    # assert parser._linkname_wavefunction in nodes
    # assert isinstance(nodes[parser._linkname_wavefunction], DataFactory("singlefile"))
    # # output parameter tests
    # assert parser._linkname_parameters in nodes
    # assert isinstance(nodes[parser._linkname_parameters], DataFactory("parameter"))
    # assert nodes[parser._linkname_parameters].dict.energy == -7380.2216063748
