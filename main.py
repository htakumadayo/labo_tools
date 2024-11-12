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

    with open(csv_filepath, 'r') as fp:
        try:
            content = fp.read()
            reader = csv.reader(StringIO(content), delimiter=delim)
            lines = list(reader)
            data = np.loadtxt(StringIO(content), unpack=True, skiprows=int(parsed.labels), delimiter=parsed.delim)
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
    plt.xlabel(xlbl)
    plt.ylabel(ylbl)
    for data_i in range(0, data_type_num, 2):
        print(data_i)
        plt.scatter(data[data_i], data[data_i + 1], s=parsed.markersize, label=labels[data_i])

    plt.title(parsed.title)
    plt.legend()
    plt.show()

    return 0

if __name__ == "__main__":
    main()

