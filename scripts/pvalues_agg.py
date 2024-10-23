#!/bin/python3

import argparse
import os
import sys
import re
from typing import Union
from math import tan, pi
from scipy.stats import cauchy


def getArgs():
	parser = argparse.ArgumentParser(description='Aggregates pvalues from kmdiff to a single p-value per unitig.')
	parser.add_argument('-k', '--kmdiff', type=str, dest = 'kmdiff_input_path', action = 'store', required=True,
                    help = 'Path to the kmdiff fasta file.')
	parser.add_argument('-u', '--unitigs', type=str, dest= 'unitigs_input_path', action= 'store', required=True,
		    help = 'Path to the unitigs fasta file.' )
	parser.add_argument('-o', '--output', type=str, dest = 'output_path', action = 'store', required=True,
		    help = 'Path to the output directory.')
	parser.add_argument('-p', '--prefix', type=str, dest = 'prefix', action = 'store', required=True,
                    help = 'String for the output file prefix.')
	args = parser.parse_args()
	return(args)


def verif_input(path: Union[str, bytes, os.PathLike]):
	"""
	Verifies that the input path is valid.
	:param path: Path to the input file.
	:return: nothing
	"""
	path = str(path)
	if os.path.isfile(path):
		pass
	else:
		print(f"ERROR: file {path} does not exist or is not a file.")
		sys.exit()


def verif_output(path: Union[str, bytes, os.PathLike], prefix: str):
	"""
	Checks that the output directory exists and that no file with output name exists already.
	:param path : string or path-like object to the output directory.
	:param prefix : string for the output file prefix.
	:return: nothing
	"""
	path = str(path)
	if os.path.isdir(path) :
		pass
	else:
		print(f"ERROR: folder {path} not found.")
		sys.exit()
	if os.path.isfile(path+"/"+prefix+".aggregated.fa") :
		print(f"ERROR: folder {path} contains a '{prefix}_unassigned.aggregated.fa' file already.")
		sys.exit()


def write_output(path: Union[str, bytes, os.PathLike], list_unitigs: list[object], prefix: str):
	"""
	Writes output.
	:param path : string or path-like object to the output directory.
	:param list_unitigs : list of objects Unitig.
	:param prefix : string for the output file prefix.
	:return: nothing
	"""
	with open(path+"/"+prefix+".aggregated.fa", 'w') as f:
		for i in list_unitigs:
			f.write(i.header+"_pval="+str(i.pvalue))
			f.write("\n"+i.sequence)


def load_pvalue_dict(path: Union[str, bytes, os.PathLike]) -> dict[str, float]:
	"""
	Loads the fasta file from kmdiff output as a dictionary :  {'sequence':'p-value'} and returns the dictionary.
	:param path: string or path-like object.
	:return: A dictionary containing kmers and their pvalues.
	"""
	kmer_2_pvalue = dict()
	with open(path) as f :
		for line in f :
			if line.startswith(">") :
				temp_str = re.sub('.*pval=', '', line)
				temp_str = re.sub('_control=.*', '', temp_str)
				pvalue = float(temp_str)
			else :
				sequence = line.rstrip('\n')
				try :
					kmer_2_pvalue[str(sequence)] = pvalue
				except MemoryError :
					size = sys.getsizeof(kmer_2_pvalue)
					size += sum(map(sys.getsizeof, kmer_2_pvalue.values())) + sum(map(sys.getsizeof, kmer_2_pvalue.keys()))
					print(size)
					exit()
	return kmer_2_pvalue


def reverse_complement(kmer: str):
	"""
	Reverse complement a kmer.
	:param kmer: string
	:return: reversed complement string of the kmer.
	"""
	rev_compl_kmer = ""
	rev_kmer = kmer[::-1]
	dict_reverse_nucleotides = {"A":"T", "T":"A", "C":"G", "G":"C"}
	for i in range(0, len(kmer)) :
			rev_compl_kmer += dict_reverse_nucleotides[rev_kmer[i]]
	return rev_compl_kmer


class Unitig(object):
	"""
	Object representing a unitig, with its sequence and aggregated pvalue.
	"""
	sequence : ""
	pvalue : 0
	kmer_pvalues : []
	header : ""
	def __init__(self, sequence, pvalue, kmer_pvalues, header) :
		self.sequence = sequence
		self.pvalue = pvalue
		self.kmer_pvalues = kmer_pvalues
		self.header = header


def make_unitig(sequence: str, kmer_dict: dict[str, float], header: str) -> object:
	"""
	Takes a sequence and/or a pvalue to build and return an object of class unitig.
	sequence : string
	pvalue : float
	kmer_pvalues : list of floats
	:return: an object of class Unitig
	"""
	list_kmer_pvalues = []
	for i in range(0, len(sequence)-31):
		kmer = str(sequence[i:i+31])
		try :
			list_kmer_pvalues.append(kmer_dict[kmer])
		except KeyError :
			rev_compl_kmer = reverse_complement(kmer)
			list_kmer_pvalues.append(kmer_dict[rev_compl_kmer])
	unitig = Unitig(sequence, 0, list_kmer_pvalues, header)
	return unitig


def load_unitigs(path: Union[str, bytes, os.PathLike], kmer_dict: dict[str, float]) -> list[object]:
	"""
	Loads unitigs as objects from the unitigs fasta file.
	:param path : string or path-like object.
	:param kmer_dict : dictionary of kmers and their corresponding pvalues.
	:return: list of objects of class Unitig with aggregated pvalues.
	"""
	list_unitigs = []
	with open(path) as f :
		for line in f :
			if line.startswith(">") :
				header = line.rstrip('\n')
			else :
				sequence = line
				unitig = make_unitig(sequence=sequence, kmer_dict=kmer_dict, header=header)
				unitig_CCT = CCT(unitig)
				list_unitigs.append(unitig_CCT)
	return list_unitigs


def CCT(unitig: object) -> object:
	"""
	Calculates the CCT of a unitig.
	:param unitig: an object of class Unitig
	:return: object of class Unitig with aggregated pvalues.
	"""
	cauchy_values = [tan((0.5-x)*pi) for x in unitig.kmer_pvalues]
	cauchy_stat = sum(cauchy_values)/len(cauchy_values)
	unitig.pvalue = 1-cauchy.cdf(cauchy_stat, loc=0, scale=1)
	return unitig


#def aggregate_pvalues(list_unitigs: list[object]) -> list[object]:
#	"""
#	Tranforms the pvalues of kmers of each unitigs into the unitigs' pvalues.
#	list_unitigs: list of objects Unitigs
#	"""
#	list_modified_unitigs = [CCT(unitig) for unitig in list_unitigs]
#	list_modified_unitigs.sort(key = lambda x: (x.pvalue, len(x.sequence)))
#	return list_modified_unitigs


def main(kmdiff_input_path: Union[str, bytes, os.PathLike], unitigs_input_path: Union[str, bytes, os.PathLike], output_path: Union[str, bytes, os.PathLike], prefix: str):
	"""
	Main function for running pvalues aggregation on unitigs.
	"""
	verif_input(kmdiff_input_path)
	verif_input(unitigs_input_path)
	verif_output(output_path, prefix)
	kmer_dict = load_pvalue_dict(kmdiff_input_path)
	list_unitigs_with_pvalues = load_unitigs(unitigs_input_path, kmer_dict)
	#list_unitigs_with_pvalues = aggregate_pvalues(list_unitigs) si marche pas remettre et la ligne au dessus est juste list_unitigs, et enlever la ligne en dessous
	list_unitigs_with_pvalues.sort(key = lambda x: (x.pvalue, -len(x.sequence)))
	write_output(output_path, list_unitigs_with_pvalues, prefix)
	print("Aggregation done !")


if __name__ == "__main__":
	args = getArgs()
	main(args.kmdiff_input_path, args.unitigs_input_path, args.output_path, args.prefix)
