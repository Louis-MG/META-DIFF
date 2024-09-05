import argparse
from Bio import SeqIO
from typing import Dict, Union, List
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

def check_input(annot_path: Union[str, bytes, os.PathLike], gene_seq_path: Union[str, bytes, os.PathLike], unitigs_path: Union[str, bytes, os.PathLike]):
    """
    Checks if input files exist.
    :param annot_path: path to [case,control]_protein_translation.faa.annot file.
    :param gene_seq_path: path to [case,control]_protein_translation.faa file.
    :param unitigs_path: path to [case,control]_unitigs.filtered.fa file.
    """
    for i in [annot_path, gene_seq_path, unitigs_path]:
        if not os.path.exists(i):
            print(f"ERROR: input file {i} does not exist.")
            exit(1)

def get_gene_header_to_gene_function_dict(annot_path: Union[str, bytes, os.PathLike]) -> Dict[str, List[str]]:
    """
    Builds the dictionary of gene headers to their KO number and function.
    :param annot_path: path to [case,control]_protein_translation.faa.annot file.
    :return: A dictionary of gene headers to the list of their KO number and function.
    """
    gene_to_function_dict = {}
    with open(annot_path, "r") as f:
        for line in f:
            gene_to_function_dict[line.strip().split("\t")[1]] = [line.strip().split("\t")[4], line.strip().split("\t")[5]]
    return gene_to_function_dict

def get_gene_header_to_gene_seq_dict(gene_seq_path: Union[str, bytes, os.PathLike]) -> Dict[str, str]:
    """
    Builds the dictionary of gene headers to their translated sequence.
    :param gene_seq_path: path to [case,control]_protein_translation.faa file.
    :return: A dictionary of gene headers to their translated sequence.
    """
    gene_header_to_gene_seq_dict = {}
    with open(gene_seq_path, "r") as f:
        for record in SeqIO.parse(gene_seq_path, "fasta"):
            gene_header_to_gene_seq_dict[record.id.rstrip('#')] = record.seq
    return gene_header_to_gene_seq_dict

def get_unitigs_dict(unitigs_path: Union[str, bytes, os.PathLike]) -> Dict[str, str]:
    """
    Builds the dictionary of unitigs header and their sequence.
    :param unitigs_path: path to the [case, control]_unitigs.filtered.fa file.
    :return: A dictionary of unitigs headers and their sequence.
    """
    unitigs_dict = {}
    for record in SeqIO.parse(unitigs_path, "fasta"):
        unitigs_dict[record.id] = record.seq
    return unitigs_dict

def write_output(path_output: Union[str, bytes, os.PathLike], gene_header_to_gene_function_dict: Dict[str, List[str]], unitigs_dict: Dict[str, str], gene_header_to_gene_seq_dict):
    """
    Writes tab-separated output file to the output directory. Format is gene header, gene translated sequence, corresponding
    unitig header, unitig sequence, KO umber, gene function.
    :param path_output: path to output file.
    :param gene_header_to_gene_function_dict: dictionary of gene headers to their KO number and function.
    :param unitigs_dict: dictionary of unitigs headers and their sequence.
    :param gene_header_to_gene_seq_dict: dictionary of gene headers to their translated sequence.
    """
    with open(path_output, "w") as f:
        f.write(f"{'gene_header'}\t{'gene_seq'}\t{'unitig_header'}\t{'unitig_seq'}\t{'gene_KO'}\t{'gene_function'}\n")
        for gene in gene_header_to_gene_seq_dict.keys():
            f.write(f"{gene}\t{gene_header_to_gene_seq_dict[gene]}\t{gene.rstrip('_')}\t{unitigs_dict[gene.rstrip('_')]}\t{gene_header_to_gene_function_dict[gene][1]}\t{gene_header_to_gene_function_dict[gene][2]}\n")
    print(f"Output written to {path_output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annot', required=True, type=str, help='Genes annotation file.')
    parser.add_argument('-g', '--gene_seq', required=True, type=str, help='Gene translation file.')
    parser.add_argument('-o', '--output', required=True, type=str, help='Output folder.')
    parser.add_argument('-u', '--unitigs', required=True, type=str, help='Unitigs file.')
    args = parser.parse_args()

    check_input(args.annot, args.gene_seq, args.unitigs)
    check_output(args.output)

    gene_header_to_gene_function = get_gene_header_to_gene_function_dict(args.annot)
    gene_header_to_gene_seq = get_gene_header_to_gene_seq_dict(args.gene_seq)
    unitigs = get_unitigs_dict(args.unitigs)

    output_file_path = args.output + "/unitigs_to_gene_functions.tsv"
    write_output(output_file_path, gene_header_to_gene_function_dict=gene_header_to_gene_function, unitigs_dict=unitigs, gene_header_to_gene_seq_dict=gene_header_to_gene_seq)


if __name__ == '__main__':
    main()