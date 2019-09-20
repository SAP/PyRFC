import sysconfig
print('From sysconfig:')
for k in 'Py_DEBUG', 'WITH_PYMALLOC', 'Py_UNICODE_SIZE':
    try:
        print(k + ': ' + repr(sysconfig.get_config_var(k)))
    except:
        print('Error getting %s' % k)

print('From headers:')
h_file = sysconfig.get_config_h_filename()
conf_vars = sysconfig.parse_config_h(open(h_file))
for k in 'Py_DEBUG', 'WITH_PYMALLOC', 'Py_UNICODE_SIZE':
    try:
        print(k + ': ' + repr(conf_vars[k]))
    except:
        print('Error getting %s' % k)