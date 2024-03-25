#!/bin/bash

set -e

Help() {
echo "
This script gets kmers counts of the top 100 unaligned unitigs. Its arguments are :
	-i --input <PATH> path to the input file(s): unaligned unitigs sorted by aggregated pvalue. Can be several path separated by a comma: case_unaligned.aggregated.pvalue.fa,control_unaligned.aggregated.pvalue.fa
	-o --output <PATH> path to the output folder.
	-m --matrix <PATH> path to the matrix of kmer counts for each sample.
	-h --help displays this help message and exits.

Output:
	- a matrix with counts of kmers in samples.
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
	-i | --input) input="$2"
	shift 2;;
	-o | --output) output="$2"
	shift 2;;
	-m | --matrix) matrix="$2"
	shift 2;;
	-h | --help) Help; exit 0;;
	-* | --*) unknown="$1"; echo -e "ERROR: unknown argument: $unknown. Exiting."; exit 1;;
	*) shift ;;
	esac
done

IFS=',' read -r -a array <<< "$input"

for i in "${array[@]}"
do
	if [  ! -e "$i" ]
	then
		echo "ERROR: $i does not exist. Exiting."
	fi
done

if [ ! -e "$output" ]
then
	mkdir "$output"
else
	echo "WARNING: $output already exist"
fi

truncate -s 0 "$output"/tmp.txt
for i in "${array[@]}"
do
	head -n 300 "$i" >> "$output"/tmp.txt
done

source ~/.bashrc
mamba activate seqkit

seqkit sliding --window 31 --step 1 "$output"/tmp.txt > "$output"/top_unknown_kmers.fa
grep '^[^>]' "$output"/top_unknown_kmers.fa > "$output"/tmp.txt
nbr_match=$(cat "$output"/tmp.txt | wc -l)
zgrep -m "$nbr_match" -F -f "$output"/tmp.txt "$matrix" > "$output"/top_unknown_matrix.txt
rm "$output"/tmp.txt
