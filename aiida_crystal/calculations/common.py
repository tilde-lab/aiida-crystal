"""
AiiDA CRYSTAL calculation plugin.
Code shared between serial and parallel CRYSTAL calculations.
"""

from __future__ import absolute_import
from ase.data import chemical_symbols
from aiida.engine import CalcJob
from aiida.orm import Dict, Code, StructureData
from aiida.common import InputValidationError
from aiida_crystal.data.basis_set import BasisSetData
from aiida_crystal.data.basis_family import CrystalBasisFamilyData


class CrystalCommonCalculation(CalcJob):
    """
    AiiDA calculation plugin for CRYSTAL code. As there're two different executables for serial and
    parallel version, we should provide two Calculations, one for each executable version.
    CrystalCommonCalculation incorporates code shared between two calculation classes

    """
    _INPUT_FILE_NAME = 'INPUT'
    _GEOMETRY_FILE_NAME = 'fort.34'
    _OUTPUT_FILE_NAME = 'crystal.out'
    _BASIS_PREFIX = 'basis_'

    @classmethod
    def define(cls, spec):
        """ Define input and output ports
        """
        super(CrystalCommonCalculation, cls).define(spec)
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=StructureData, required=True)
        spec.input('parameters', valid_type=Dict, required=True)
        spec.input_namespace('basis', valid_type=BasisSetData, required=False, dynamic=True)
        spec.input('basis_family', valid_type=CrystalBasisFamilyData, required=False)

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(CrystalCommonCalculation, self)._init_internal_params()

        # parser entry point defined in setup.json
        self._default_parser = 'crystal'

        # input files
        self._DEFAULT_INPUT_FILE = self._INPUT_FILE_NAME

        # output files
        self._DEFAULT_OUTPUT_FILE = self._OUTPUT_FILE_NAME

    def _validate_input(self, inputdict):
        """Input validation; returns the dict of validated data"""
        validated_dict = {}

        try:
            validated_dict['code'] = inputdict.pop('code')
        except KeyError:
            raise InputValidationError("No code specified for this "
                                       "calculation")

        try:
            validated_dict['structure'] = inputdict.pop('structure')
        except KeyError:
            raise InputValidationError("No structure specified for this "
                                       "calculation")
        if not isinstance(validated_dict['structure'], StructureData):
            raise InputValidationError("structure not of type "
                                       "StructureData: {}".format(validated_dict['structure']))

        try:
            validated_dict['parameters'] = inputdict.pop('parameters')
        except KeyError:
            raise InputValidationError("No parameters specified for this "
                                       "calculation")
        if not isinstance(validated_dict['parameters'], Dict):
            raise InputValidationError("parameters not of type "
                                       "ParameterData: {}".format(validated_dict['parameters']))

        # settings are optional
        validated_dict['settings'] = inputdict.pop('settings', None)
        if validated_dict['settings'] is not None:
            if not isinstance(validated_dict['settings'], Dict):
                raise InputValidationError(
                    "settings not of type ParameterData: {}".format(validated_dict['settings']))

        # basis family input
        basis_present = False
        validated_dict['basis_family'] = inputdict.pop('basis_family', None)
        if validated_dict['basis_family'] is not None:
            basis_present = True
            if not isinstance(validated_dict['basis_family'], CrystalBasisFamilyData):
                raise InputValidationError(
                    "basis_family not of type CrystalBasisFamilyData: {}".format(validated_dict['basis_family']))

        basis_inputs = [_ for _ in inputdict if _.startswith(self._BASIS_PREFIX)]
        basis_dict = {}

        if (not basis_present) and (not basis_inputs):
            raise InputValidationError('No basis sets specified for calculation!')
        for basis_name in basis_inputs:
            if basis_present:
                raise ValueError("Either basis or basis family (not both) must be present in calculation inputs")

            _, symbol = basis_name.split('_')
            if symbol not in chemical_symbols:
                raise InputValidationError('Basis set provided for element not in periodic table: {}'.format(symbol))
            basis = inputdict.pop(basis_name)
            basis_dict[symbol] = basis
            basis_present = True
        validated_dict['basis'] = basis_dict

        # if inputdict:
        #     raise ValidationError("Unknown inputs remained after validation: {}".format(inputdict))

        return validated_dict

    @classmethod
    def _get_linkname_basis(cls, element):
        """Returns a link name for basis, one for each element"""
        return "{}{}".format(cls._BASIS_PREFIX, element)
