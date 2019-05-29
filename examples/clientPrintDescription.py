from ConfigParser import ConfigParser
import sys

from pyrfc import Connection,\
    ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError


def parameter_key_function(parameter):
    """ returns a key for sorting parameters """
    value = {u'RFC_IMPORT':1,
             u'RFC_CHANGING':2,
             u'RFC_TABLES':3,
             u'RFC_EXPORT':4}
    return value[parameter['direction']]

def main(function_name):
    config = ConfigParser()
    config.read('sapnwrfc.cfg')
    params_connection = config._sections['connection']

    try:
        connection = Connection(**params_connection)
        func_desc = connection.get_function_description(function_name)
        print (u"Parameters of function: {0}".format(function_name))

        parameter_keys = [u'name', u'parameter_type', u'direction',
                          u'nuc_length', u'uc_length', u'decimals',
                          u'default_value', u'optional',
                          u'type_description', u'parameter_text']
        parameter_widths = [20, 17, 11, 10, 9, 9, 15, 10, 15, 20]
        for key, width in zip(parameter_keys, parameter_widths):
            sys.stdout.write(u"{0}".format(key).ljust(width).upper() + u" ")
        sys.stdout.write(u"\n")

        for parameter in sorted(func_desc.parameters, key=parameter_key_function):
            for key, width in zip(parameter_keys, parameter_widths):
                if key == u'type_description' and parameter[key] is not None:
                    sys.stdout.write(
                        u"{0}".format(parameter[key].name).ljust(width) + u" "
                    )
                else:
                    sys.stdout.write(
                        u"{0}".format(parameter[key]).ljust(width) + u" "
                    )
            sys.stdout.write(u"\n")
            type_desc = parameter['type_description']
            if type_desc is not None:
                # type_desc of class TypeDescription
                field_keys = [u'name', u'field_type', u'nuc_length',
                              u'nuc_offset', u'uc_length', u'uc_offset',
                              u'decimals', u'type_description']
                field_widths = [20, 17, 10, 10, 9, 9, 10, 15]

                sys.stdout.write(u" " * 4 + u"-----------( Structure of {0.name} (n/uc_length={0.nuc_length}/{0.uc_length})--\n".format(type_desc))
                for key, width in zip(field_keys, field_widths):
                    sys.stdout.write(u"{0}".format(key).ljust(width).upper() + u" ")
                sys.stdout.write(u"\n")

                for field_description in type_desc.fields:
                    for key, width in zip(field_keys, field_widths):
                        sys.stdout.write(u"{0}".format(field_description[key]).ljust(width) + u" ")
                    sys.stdout.write(u"\n")
                sys.stdout.write(u" " * 4 + u"-----------( Structure of {0.name} )-----------\n".format(type_desc))
            sys.stdout.write(u"-" * sum(parameter_widths) + u"\n")
        connection.close()

    except CommunicationError:
        print u"Could not connect to server."
        raise
    except LogonError:
        print u"Could not log in. Wrong credentials?"
        raise
    except (ABAPApplicationError, ABAPRuntimeError):
        print u"An error occurred."
        raise

if __name__ == '__main__':
    if len(sys.argv)<2:
        print("No function name provided.")
        sys.exit()
    main(sys.argv[1])
