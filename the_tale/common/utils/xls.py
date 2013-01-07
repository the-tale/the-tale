# coding: utf-8

import xlrd


class XLSException(Exception): pass


def load_table(filename, sheet_index=0, encoding='utf-8', rows=None, columns=None):

    if rows and len(set(rows)) != len(rows):
        raise XLSException('duplicate row id')

    if columns and len(set(columns)) != len(columns):
        raise XLSException('duplicate column id')

    book = xlrd.open_workbook(filename, logfile=None, encoding_override=encoding)

    sheet = book.sheet_by_index(sheet_index)

    visited = False

    row_rows = []

    for row_number in xrange(sheet.nrows):

        row_data = list(sheet.row_values(row_number))

        if not any(row_data):
            if visited: break
            else: continue

        row_rows.append(row_data)

    left_border_index = 0
    right_border_index = -1

    for row in row_rows:
        for i, element in enumerate(row):
            if element != '':
                left_border_index = i
                break

        for i, element in enumerate(row[left_border_index:], start=left_border_index):
            if element == '' and i > right_border_index:
                right_border_index = i
                break

        if right_border_index == -1: right_border_index = len(row)

    data = [row[left_border_index:right_border_index+1] for row in row_rows]

    if rows and columns:
        new_data = {}

        real_columns = data[0][1:]

        if set(real_columns) != set(columns):
            raise XLSException('wrong columns ids: %r' % (real_columns, ))

        for row in data[1:]:
            row_id = row[0]

            if row_id not in rows:
                raise XLSException('unknown row id: "%s"' % (row_id,))

            if row_id in new_data:
                raise XLSException('duplicate row id: "%s"' % (row_id, ))

            if len(row[1:]) != len(columns):
                raise XLSException('wrong number of elements in row: %r' % (row[1:], ))

            new_data[row_id] = dict(zip(real_columns, row[1:]))

        return new_data

    elif rows:
        new_data = {}
        for row in data:
            row_id = row[0]
            if row_id not in rows:
                raise XLSException('unknown row id: "%s"' % (row_id,))
            if row_id in new_data:
                raise XLSException('duplicate row id: "%s"' % (row_id, ))

            new_data[row_id] = row[1:]

        return new_data

    elif columns:
        new_data = []

        real_columns = data[0]

        if set(real_columns) != set(columns):
            raise XLSException('wrong columns ids: %r' % (real_columns, ))

        for row in data[1:]:
            if len(row) != len(columns):
                raise XLSException('wrong number of elements in row: %r' % (row, ))
            new_data.append(dict(zip(real_columns, row)))
        return new_data

    return data
