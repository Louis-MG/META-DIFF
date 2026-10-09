#!/bin/python3

import argparse

from Bio import SeqIO
from typing import Dict, Union, List, Tuple
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


def check_input(
    annot_path: Union[str, bytes, os.PathLike],
    gene_seq_path: Union[str, bytes, os.PathLike]
):
    """
    Checks if input files exist.
    :param annot_path: path to [case,control]_protein_translation.faa.annot file.
    :param gene_seq_path: path to [case,control]_protein_translation.faa file.
    :param unitigs_path: path to [case,control]_unitigs.filtered.fa file.
    """
    for i in [annot_path, gene_seq_path]:
        if not os.path.exists(i):
            print(f"ERROR: input file {i} does not exist.")
            exit(1)


def get_gene_header_to_gene_function_dict(
    annot_path: Union[str, bytes, os.PathLike],
) -> Dict[str, List[str]]:
    """
    Builds the dictionary of gene headers to their gene name, product, annotation source.
    :param annot_path: path to [case,control].tsv file.
    :return: A dictionary of gene headers to the list of their gene name, product and annotation source.
    """
    gene_to_function_dict = {}
    with open(annot_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                pass
            else :
                try:
                    gene_to_function_dict[line.split("\t")[5]] = [
                        line.split("\t")[0],
                        line.split("\t")[7],
                        line.split("\t")[8]
                    ]
                except KeyError:
                    problematic_line = line.split("\t")
                    print(f'This line causes an issu: {problematic_line}')
    return gene_to_function_dict


def get_gene_header_to_gene_seq_dict(
    gene_seq_path: Union[str, bytes, os.PathLike],
) -> Dict[str, str]:
    """
    Builds the dictionary of gene headers to their translated sequence.
    :param gene_seq_path: path to [case,control].tsv file.
    :return: A dictionary of gene headers to their translated sequence.
    """
    gene_header_to_gene_seq_dict = {}
    with open(gene_seq_path, "r") as f:
        for record in SeqIO.parse(gene_seq_path, "fasta"):
            gene_header_to_gene_seq_dict[record.id.rstrip("#")] = record.seq
    return gene_header_to_gene_seq_dict


def get_clade_and_unitigs(
    kraken_output_path: Union[str, bytes, os.PathLike],
) -> Tuple[dict[str, str], dict[str, int]]:
    """
    Builds a dictionary of unitigs to the clade they were assigned to by Kraken2
    :param kraken_output_path: path to the .output kraken output file
    """
    clade_align_base = {}
    unitigs_to_clade = {}
    with open(kraken_output_path, "r") as f:
        for line in f:
            if line.startswith("U"):
                unitigs_to_clade[line.split("\t")[1]] = "Unclassified"
                try:
                    clade_align_base["Unclassified"] += int(line.split("\t")[3])
                except KeyError:
                    clade_align_base["Unclassified"] = int(line.split("\t")[3])
            else:
                unitigs_to_clade[line.split("\t")[1]] = line.split("\t")[2]
                try:
                    clade_align_base[line.split("\t")[2]] += int(line.split("\t")[3])
                except KeyError:
                    clade_align_base[line.split("\t")[2]] = int(line.split("\t")[3])
    return unitigs_to_clade, clade_align_base


def write_output_gene_table(
    path_output: Union[str, bytes, os.PathLike],
    gene_header_to_gene_function_dict: Dict[str, List[str]],
    gene_header_to_gene_seq_dict,
    unitigs_to_clade_dict: Dict[str, str],
):
    """
    Writes tab-separated output file to the output directory. Format is gene header, gene translated sequence, corresponding
    unitig header, product, annotation source.
    :param path_output: path to output file.
    :param gene_header_to_gene_function_dict: dictionary of gene headers to their gene name, product and annotation source.
    :param gene_header_to_gene_seq_dict: dictionary of gene headers to their translated sequence.
    """
    with open(path_output, "w") as f:
        f.write(
            f"{'gene_header'}\t{'gene_translated_seq'}\t{'unitig_header'}\t{'unitig_seq'}\t{'gene_product'}\t{'gene_annotation_source'}\t{'unitig_clade'}\n"
        )
        for gene in gene_header_to_gene_seq_dict.keys():
            unitig_header = gene_header_to_gene_function_dict[gene][0]
            try:
                f.write(
                    f"{gene}\t{gene_header_to_gene_seq_dict[gene]}\t{unitig_header}\t{gene_header_to_gene_function_dict[gene][1]}\t{gene_header_to_gene_function_dict[gene][2]}\t{unitigs_to_clade_dict[unitig_header]}\n"
                )
            except KeyError:
                print(f'This is the unitig header causing an issue: {unitig_header}')
                exit(1)
    print(f"Output written to {path_output}")


def write_output_clades_ordered(
    path_output: Union[str, bytes, os.PathLike],
    clades_to_align_length_dict: Dict[str, int],
    condition: str,
):
    """
    Writes the output with clades ordered by total alignment length of unitigs.
    :param path_output: path to output directory.
    :param clades_to_align_length_dict: dictionary of clades to their alignment length.
    """
    with open(path_output, "w") as f:
        sorted_clades = sorted(
            clades_to_align_length_dict.items(), key=lambda x: x[1], reverse=True
        )
        for clade in sorted_clades:
            f.write(f"{clade[0]}\t{clade[1]}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--annot", required=True, type=str, help="Genes annotation file."
    )
    parser.add_argument(
        "-g",
        "--gene_translation_seq",
        required=True,
        type=str,
        help="Gene translation file.",
    )
    parser.add_argument(
        "-o", "--output", required=True, type=str, help="Output folder."
    )
    parser.add_argument(
        "-c", "--case", required=True, type=str, help="Case or Control condition."
    )
    parser.add_argument(
        "-k",
        "--kraken_output",
        required=True,
        type=str,
        help="Kraken2 classification output file.",
    )
    args = parser.parse_args()

    check_input(args.annot, args.gene_translation_seq)
    check_output(args.output)

    gene_header_to_gene_function = get_gene_header_to_gene_function_dict(args.annot)
    gene_header_to_gene_seq = get_gene_header_to_gene_seq_dict(
        args.gene_translation_seq
    )
    unitigs_to_clade, clade_base_align = get_clade_and_unitigs(args.kraken_output)
    output_table_path = (
        args.output + "/" + args.case + "_unitigs_to_clade_and_gene_functions.tsv"
    )
    output_clades_path = args.output + "/" + args.case + "_clades.tsv"

    print("step 3    done")
    write_output_gene_table(
        output_table_path,
        gene_header_to_gene_function_dict=gene_header_to_gene_function,
        gene_header_to_gene_seq_dict=gene_header_to_gene_seq,
        unitigs_to_clade_dict=unitigs_to_clade,
    )
    write_output_clades_ordered(
        output_clades_path,
        clades_to_align_length_dict=clade_base_align,
        condition=args.case,
    )


if __name__ == "__main__":
    main()
