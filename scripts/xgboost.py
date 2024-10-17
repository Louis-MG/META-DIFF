import argparse

import numpy as np
import sklearn as sk
import pandas as pd
import seaborn as sns
from typing import Union
import os

def check_output(path: Union[str, bytes, os.PathLike]):
    """
    Checks if output directory exists and makes it if necessary.
    :param path: The output directory path.
    """
    if os.path.isdir(path):
        print(f"WARNING: output directory {path} already exists.")
    else:
        os.makedirs(path)


def check_input(matrix_path: Union[str, bytes, os.PathLike]):
    """
    Checks if input files exist.
    :param matrix_path: The input file path.
    """
    if not os.path.exists(matrix_path):
        print(f"ERROR: matrix input file {matrix_path} does not exist.")
        exit(1)

def load_matrix(matrix_path: Union[str, bytes, os.PathLike]):
    """
    Loads matrix as a pandas dataframe from input file and shapes it.
    :param matrix_path: path to the matrix index.tsv file.
    """
    matrix = pd.read_csv(matrix_path, sep="\t", header=None)
    matrix = matrix.transpose()
    matrix.columns = matrix.iloc[0]
    matrix = matrix.drop(matrix.index[0])
    # ajouter un shuffle ou quelque chose
    return matrix

def preprocess_matrix(matrix: pd.DataFrame):
    """
    Normalises the matrix and separates it into a train and test set.
    :param matrix: The matrix to normalise.
    """


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--matrix', required=True, type=str, help='Matrix of unitig abundances.')
    args = parser.parse_args()

    check_input(args.matrix)
    check_output(args.output)

if __name__ == '__main__':
    main()
