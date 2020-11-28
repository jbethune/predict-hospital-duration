#!/usr/bin/env python3

from argparse import ArgumentParser
from csv import reader

def greater_than(value):
    if value.startswith('>'):
        return int(value[1:])
    elif value == 'None':
        return 0
    elif value == 'Norm':
        return 1
    else:
        raise ValueError('Not part of category greather than: %s' % value)

def interval_take_first(value):
    from_, to = value.split('-')
    return int(from_[1:])

def dict_get(d):
    def result(key):
        return d[key]
    return result

def read_encoding_file(filename):
    result = [] # column_index -> numeric_callback
    with open(filename) as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            column_name, column_type, type_details = parts
            if column_type == 'numeric':
                if type_details == 'int':
                    fn = int
                else:
                    raise ValueError('not supported: %s' % type_details)
            elif column_type == 'categorical':
                lookup = {
                        category: index
                        for index, category in enumerate(type_details.split('|'))
                }

                fn = dict_get(lookup) # avoid late binding
            elif column_type == 'greater_than':
                fn = greater_than
            elif column_type == 'interval':
                if type_details == 'take_first':
                    fn = interval_take_first
                else:
                    raise ValueError('not supported: %s' % type_details)
            else:
                raise ValueError('not supported: %s' % column_type)
            result.append(fn)
    return result


            

def main(args):
    encoding = read_encoding_file(args.encoding_file)
    headers = None
    with open(args.data_file) as f:
        csv = reader(f)
        for line_no, values in enumerate(csv):
            if line_no == 0: # header
                print('\t'.join(values))
                continue

            print('\t'.join(
                str(fn(value))
                for value, fn in zip(values, encoding)
            ))


if __name__ == '__main__':
    parser = ArgumentParser('Transform raw SyntheticData2020 diabetes data into numerical values')
    parser.add_argument('encoding_file')
    parser.add_argument('data_file')
    main(parser.parse_args())
