from configparser import ConfigParser
import sys

from pyrfc import Connection,\
    ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError


def parameter_key_function(parameter):
    """ returns a key for sorting parameters """
    value = {'RFC_IMPORT':1,
             'RFC_CHANGING':2,
             'RFC_TABLES':3,
             'RFC_EXPORT':4}
    return value[parameter['direction']]

def main(function_name):
    config = ConfigParser()
    config.read('sapnwrfc.cfg')
    params_connection = config._sections['connection']

    try:
        connection = Connection(**params_connection)
        func_desc = connection.get_function_description(function_name)
        print("Parameters of function: {0}".format(function_name))

        parameter_keys = ['name', 'parameter_type', 'direction',
                          'nuc_length', 'uc_length', 'decimals',
                          'default_value', 'optional',
                          'type_description', 'parameter_text']
        parameter_widths = [20, 17, 11, 10, 9, 9, 15, 10, 15, 20]
        for key, width in zip(parameter_keys, parameter_widths):
            sys.stdout.write("{0}".format(key).ljust(width).upper() + " ")
        sys.stdout.write("\n")

        for parameter in sorted(func_desc.parameters, key=parameter_key_function):
            for key, width in zip(parameter_keys, parameter_widths):
                if key == 'type_description' and parameter[key] is not None:
                    sys.stdout.write(
                        "{0}".format(parameter[key].name).ljust(width) + " "
                    )
                else:
                    sys.stdout.write(
                        "{0}".format(parameter[key]).ljust(width) + " "
                    )
            sys.stdout.write("\n")
            type_desc = parameter['type_description']
            if type_desc is not None:
                # type_desc of class TypeDescription
                field_keys = ['name', 'field_type', 'nuc_length',
                              'nuc_offset', 'uc_length', 'uc_offset',
                              'decimals', 'type_description']
                field_widths = [20, 17, 10, 10, 9, 9, 10, 15]

                sys.stdout.write(" " * 4 + "-----------( Structure of {0.name} (n/uc_length={0.nuc_length}/{0.uc_length})--\n".format(type_desc))
                for key, width in zip(field_keys, field_widths):
                    sys.stdout.write("{0}".format(key).ljust(width).upper() + " ")
                sys.stdout.write("\n")

                for field_description in type_desc.fields:
                    for key, width in zip(field_keys, field_widths):
                        sys.stdout.write("{0}".format(field_description[key]).ljust(width) + " ")
                    sys.stdout.write("\n")
                sys.stdout.write(" " * 4 + "-----------( Structure of {0.name} )-----------\n".format(type_desc))
            sys.stdout.write("-" * sum(parameter_widths) + "\n")
        connection.close()

    except CommunicationError:
        print("Could not connect to server.")
        raise
    except LogonError:
        print("Could not log in. Wrong credentials?")
        raise
    except (ABAPApplicationError, ABAPRuntimeError):
        print("An error occurred.")
        raise

if __name__ == '__main__':
    if len(sys.argv)<2:
        print("No function name provided.")
        sys.exit()
    main(sys.argv[1])
