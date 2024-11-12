import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
from io import StringIO
import pathlib as pl
import sys
import csv

parser = ap.ArgumentParser(
        prog='LaboDraw',
        description='Graphing and calculation program designed for PH Lab course',
        epilog='Hello'
)

# parser.add_argument('-h', '--help', action='help', help='Display help')
parser.add_argument('filename', action='store', help='CSV file which the data is read from')
parser.add_argument('-l', '--labels', action='store_true', help='Indicate that the first row is used for data labels')
parser.add_argument('-d', '--delim', default=',', help='Set the CSV delimiter (default , )')
parser.add_argument('-m', '--markersize', default=50, type=int, help='Set the marker size of plt.scatter')
parser.add_argument('-xlabel', default='', help='Set the horizontal axis label.')
parser.add_argument('-ylabel', default='', help='Set the vertical axis label.')
parser.add_argument('-xunits', default='', help='Set the horizontal axis units.')
parser.add_argument('-yunits', default='', help='Set the vertical axis units.')
parser.add_argument('-t', '--title', default='', help='Set the title.')
parser.add_argument('-e', '--errors', action='store_true', help='Indicate that the formulas for errors are included in the first rows')
# parser.add_argument('--hello', action='store_true', help='Prints hello')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(color, msg):
    print(f"{color}{msg}{bcolors.ENDC}")

def print_warn(msg):
    print_colored(bcolors.WARNING, msg)

def print_error(msg):
    print_colored(bcolors.FAIL, msg)

def print_ok(msg):
    print_colored(bcolors.OKGREEN, msg)


class Hd:  # Header Types
    LABELS = 'labels'
    ERRORS = 'errors'

def calc_err(expression, X, Y):
    return eval(expression, {"X": X, "Y": Y})

def main():
    parsed = parser.parse_args(sys.argv[1:])
   
    csv_filepath = parsed.filename
    path = pl.Path(csv_filepath)
    if not path.exists():
        print_error(f"The file {csv_filepath} does not exist.")
        return 1

    print_ok("The file exists.")
    print(parsed)

    delim = parsed.delim

    lines = None
    data = None

    header_row_usage = {Hd.LABELS : parsed.labels, Hd.ERRORS : parsed.errors}
    row_used = np.array(list(header_row_usage.values()))
    total_row_used = np.sum(row_used)
    print(row_used)
    row_indices = dict(zip(header_row_usage.keys(), list(np.cumsum(row_used) - 1)))

    with open(csv_filepath, 'r') as fp:
        try:
            content = fp.read()
            reader = csv.reader(StringIO(content), delimiter=delim)
            lines = list(reader)
            data = np.loadtxt(StringIO(content), unpack=True, skiprows=total_row_used, delimiter=parsed.delim)
        except ValueError as ve:
            print(str(ve))
            print_error("If the first row is dedicated to labels, consider using -l option.")
            return 1
    
    data_type_num = data.shape[0]
    if data_type_num < 2:
        print_error("There are less than two data columns; nothing to show")
        return 1
    
    empty = data_type_num * ['']
    labels = (lines[0] if parsed.labels else empty)
    if not parsed.labels:
        print_warn("Labels are not assigned.")
    
    xlbl, ylbl = parsed.xlabel, parsed.ylabel
    if parsed.xunits != '':
        xlbl += f" [{parsed.xunits}]"
    if parsed.yunits != '':
        ylbl += f" [{parsed.yunits}]"

    print(labels[0])

    plt.xlabel(xlbl)
    plt.ylabel(ylbl)
    
    # Calculation of error
    err_formulas = lines[row_indices[Hd.ERRORS]]
    print(err_formulas)
    errors = np.zeros_like(data)
    for col in range(0, data_type_num, 2):
        x_err = err_formulas[col]
        y_err = err_formulas[col + 1]
        x_errors = np.zeros(data.shape[1])
        y_errors = np.zeros(data.shape[1])
        
        if parsed.errors:
            for row in range(0, data[col].size):
                x_errors[row] = calc_err(x_err, data[col][row], data[col+1][row])
                y_errors[row] = calc_err(y_err, data[col][row], data[col+1][row])
        
        errors[col], errors[col+1] = x_errors, y_errors

    for data_i in range(0, data_type_num, 2):
        x_data, y_data = data[data_i], data[data_i + 1]
        x_err, y_err = errors[data_i], errors[data_i + 1]
        if parsed.errors:
            plt.errorbar(x_data, y_data, xerr=x_err, yerr=y_err, label=labels[data_i], marker='o', linestyle='', capsize=3, ecolor='black')
        else:
            plt.scatter(x_data, y_data, s=parsed.markersize, label=labels[data_i])
        
    plt.title(parsed.title)
    plt.legend()
    plt.show()

    return 0

if __name__ == "__main__":
    main()

