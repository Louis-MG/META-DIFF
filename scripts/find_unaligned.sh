#!/bin/bash

set -e

Help() {
echo "
This script finds unaligned unitigs in a fasta file from a .m8 (mmseq2 output). Its arguments are :
	-f --fasta <PATH> path to the fasta file.
	-m --m8 <PATH> path to the mmseq2 report file in .m8 format.
	-o --output <PATH> path to the desired output directory.
	-p --prefix <STRING> prefix for output files.
	-h --help displays this help message and exits.

It output the following files :
	- {prefix}_unclassified.unitigs.fasta file containing the unaligned sequences.
"
}

if [ $# -eq 0 ]
then
	Help
	exit 0
fi

while [ $# -gt 0 ]
do
	case $1 in
	-f | --fasta) fasta="$2"
	shift 2;;
	-m | --m8) m8="$2"
	shift 2;;
	-o | --output) output="$2"
	shift 2;;
	-p | --prefix) prefix="$2"
	shift 2;;
	-h | --help) Help; exit 0;;
	-* | --*) unknown="$1"; echo -e "ERROR: unknown argument: $unknown. Exiting."; exit 1;;
	*) shift ;;
	esac
done

if [ ! -e "$fasta" ]
then
	echo -e "ERROR: $fasta file does not exist. Exiting."
elif [ ! -e "$m8" ]
then
	echo -e "ERROR: $m8 file does not exist. Exiting."
elif [ ! -d "$output" ]
then
	echo -e "ERROR: $output directory does not exist or is not a directory. Exiting"
fi

#gets the index of the aligned unitigs
#calculates index of headers et sequence lines for aligned unitigs
echo "Obtaining indexes of aligned unitigs to get unaligned unitgs, this is gonna take  a while ..."
awk -F '\t' 'BEGIN {OFS="\n"} FNR == NR {index_seq=($1+1)*2; index_header=2*($1+1)-1; to_delete[index_header]++; to_delete[index_seq]++} FNR != NR && !(FNR in to_delete) {print $0 }' "$m8" "$fasta" > "$output"/"$prefix"_unclassified.unitigs.fa
