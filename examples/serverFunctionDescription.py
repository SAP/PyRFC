from pyrfc import FunctionDescription, TypeDescription

animals = TypeDescription("ANIMALS", nuc_length=20, uc_length=28)
animals.add_field(name='LION', field_type='RFCTYPE_CHAR',
    nuc_length=5, uc_length=10,
    nuc_offset=0, uc_offset=0
)
animals.add_field(name='ELEPHANT', field_type='RFCTYPE_FLOAT', decimals=16,
    nuc_length=8, uc_length=8,
    nuc_offset=8, uc_offset=16,
)
animals.add_field(name='ZEBRA', field_type='RFCTYPE_INT',
    nuc_length=4, uc_length=4,
    nuc_offset=16, uc_offset=24
)

func_desc = FunctionDescription("I_DONT_EXIST")
func_desc.add_parameter(name='DOC', field_type='RFCTYPE_INT',
    direction='RFC_IMPORT',
    nuc_length=4,
    uc_length=4
)
func_desc.add_parameter(name='CAT', field_type='RFCTYPE_CHAR',
    direction='RFC_IMPORT',
    nuc_length=5,
    uc_length=10
)
func_desc.add_parameter(name='ZOO', field_type='RFCTYPE_STRUCTURE',
    direction='RFC_IMPORT',
    nuc_length=20,
    uc_length=28,
    type_description=animals
)
func_desc.add_parameter(name='BIRD', field_type='RFCTYPE_FLOAT',
    direction='RFC_IMPORT',
    nuc_length=8,
    uc_length=8,
    decimals=16
)
func_desc.add_parameter(name='COW', field_type='RFCTYPE_CHAR',
    direction='RFC_EXPORT',
    nuc_length=3,
    uc_length=6
)
func_desc.add_parameter(name='STABLE', field_type='RFCTYPE_STRUCTURE',
    direction='RFC_EXPORT',
    nuc_length=20,
    uc_length=28,
    type_description=animals
)
func_desc.add_parameter(name='HORSE', field_type='RFCTYPE_INT',
    direction='RFC_EXPORT',
    nuc_length=4,
    uc_length=4
)
