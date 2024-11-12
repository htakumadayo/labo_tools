import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
from io import StringIO
import pathlib as pl
import sys
import csv
from config import *

parser = ap.ArgumentParser(
        prog='LaboDraw',
        description='Graphing and calculation program designed for PH Lab course',
        epilog='Hello'
)

# parser.add_argument('-h', '--help', action='help', help='Display help')
parser.add_argument('filename', action='store', help='CSV file which the data is read from')
parser.add_argument('-l', '--labels', action='store_true', help='Indicate that the first row is used for data labels')
parser.add_argument('-d', '--delim', default=',', help='Set the CSV delimiter (default , )')
parser.add_argument('-xlabel', default='', help='Set the horizontal axis label.')
parser.add_argument('-ylabel', default='', help='Set the vertical axis label.')
parser.add_argument('-xunits', default='', help='Set the horizontal axis units.')
parser.add_argument('-yunits', default='', help='Set the vertical axis units.')
parser.add_argument('-t', '--title', default='', help='Set the title.')
parser.add_argument('-e', '--errors', action='store_true', help='Indicate that the formulas for errors are included in the first rows')
parser.add_argument('--export', default="", help="When this option is set, save the figure with the given name. Example: --export Test.png")
parser.add_argument('-s', '--shape', action='append', help="Specifies the shape of dots for one scatter plot. An argument is used\
                    for a pair of columns, the first corresponding to the most left column. See https://matplotlib.org/stable/api/markers_api.html\
                    for available options.")
parser.add_argument('-p', '--param', action='append', nargs=2, metavar=('Name', 'Value'), help="Define a parameter that is used in error calculation.")
parser.add_argument('--allfit', action='store_true', help="Perform linear fit for all data.")
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

def convert_params_to_float(params):
    for i in range(len(params)):
        try:
            params[i][1] = float(params[i][1])
        except ValueError as e:
            print_err(f"An error occured while converting parameter {params[0]} to float: {str(e)}")
            params[i][1] = 0
    return params

def calc_err(expression, X, Y, params):
    try:
        param_dict = {"X": X, "Y": Y}
        param_dict.update(convert_params_to_float(params))
        return eval(expression, param_dict)
    except Exception as e:
        print_error(f"An error occured while evaluating error expression {expression}: {str(e)}")
        return 0

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
    mask = None

    header_row_usage = {Hd.LABELS : parsed.labels, Hd.ERRORS : parsed.errors}
    row_used = np.array(list(header_row_usage.values()))
    total_row_used = np.sum(row_used)
    print(row_used)
    row_indices = dict(zip(header_row_usage.keys(), list(np.cumsum(row_used) - 1)))

    # Load data
    with open(csv_filepath, 'r') as fp:
        try:
            content = fp.read()
            reader = csv.reader(StringIO(content), delimiter=delim)
            lines = list(reader)
            masked_array = np.genfromtxt(csv_filepath, unpack=True, skip_header=total_row_used, delimiter=parsed.delim, usemask=True, filling_values=1e+20)
            data, mask = masked_array.data, masked_array.mask
        except ValueError as ve:
            print(str(ve))
            print_error("If the first row is dedicated to labels, consider using -l option.")
            return 1
    data_type_num = data.shape[0]
    if data_type_num < 2:
        print_error("There are less than two data columns; nothing to show")
        return 1
   
    # Labeling
    empty = data_type_num * ['']
    labels = (lines[0] if parsed.labels else empty)
    if not parsed.labels:
        print_warn("Labels are not assigned.")
    
    xlbl, ylbl = parsed.xlabel, parsed.ylabel
    if parsed.xunits != '':
        xlbl += f" [{parsed.xunits}]"
    if parsed.yunits != '':
        ylbl += f" [{parsed.yunits}]"

    plt.xlabel(xlbl, fontsize=label_font_size)
    plt.ylabel(ylbl, fontsize=label_font_size)
    
    # Calculation of error
    if parsed.errors:
        err_formulas = lines[row_indices[Hd.ERRORS]]
        errors = np.zeros_like(data)
        for col in range(0, data_type_num, 2):
            x_err = err_formulas[col]
            y_err = err_formulas[col + 1]
            x_errors = np.zeros(data.shape[1])
            y_errors = np.zeros(data.shape[1])
            
            if parsed.errors:
                for row in range(0, data[col].size):
                    x_errors[row] = calc_err(x_err, data[col][row], data[col+1][row], parsed.param)
                    y_errors[row] = calc_err(y_err, data[col][row], data[col+1][row], parsed.param)
            
            errors[col], errors[col+1] = x_errors, y_errors

    # Actual plotting
    for data_i in range(0, data_type_num, 2):
        mask_i = np.logical_not(mask[data_i] & mask[data_i + 1])
        x_data, y_data = data[data_i][mask_i], data[data_i + 1][mask_i]
        marker = ('o' if parsed.shape is None or len(parsed.shape) <= data_i // 2 else parsed.shape[data_i // 2])
        if parsed.errors:
            x_err, y_err = errors[data_i][mask_i], errors[data_i + 1][mask_i]
            plt.errorbar(x_data, y_data, xerr=x_err, yerr=y_err, markersize=dots_size, label=labels[data_i], marker=marker,
                         linestyle='', capsize=cap_size, elinewidth=ethickness, markeredgewidth=ethickness, ecolor='black')
        else:
            plt.scatter(x_data, y_data, s=dots_size, label=labels[data_i], marker=marker)
        
    plt.title(parsed.title)
    plt.legend(fontsize=legend_font_size)
    plt.grid(show_grid)
    
    if parsed.export != "":
        plt.savefig(parsed.export, format="png")
    plt.show()

    return 0

if __name__ == "__main__":
    main()

