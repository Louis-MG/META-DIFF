#!/bin/bash

set -e

Help() {
	echo "
This script generates the file of file (fof.txt) for kmdiff. Its arguments are:
	--cases -c <PATH> path to the directory of cases samples.
	--controls -C <PATH> path to the directory of control samples.
	--output -o <PATH> path to where the fof should be.
	-R1 <STRING> -R2 <STRING> strings to determine forward and reverse reads.
	--help -h displays this help message and exits.

Output is :
	- a fof.txt named after the output parameter. The file is tab separated, format:
		control1: /path/to/control1_read1.fastq ; /path/to/control1_read2.fastq
		control2: /path/to/control2_read1.fastq ; /path/to/control2_read2.fastq
		case1: /path/to/case1_read1.fastq ; /path/to/case1_read2.fastq
		case2: /path/to/case2_read1.fastq ; /path/to/case2_read2.fastq

WARNING: depending of the denomination of your files for paired ends (R1 and R2, _1 and _2 ...), you will have to modify lines 55-56 and 60-61. Yeah it's annoying. Not yet suitable for single end.
"

}

if [[ $# -eq 0 ]]
then
	Help
	exit
fi

while [[ $# -gt 0 ]]
do
	case $1 in
	-c | --cases) cases="$2"
	shift 2;;
	-C | --controls) controls="$2"
	shift 2;;
	-o | --output) output="$2"
	shift 2;;
	-1) R1="$2"
	shift 2;;
	-2)  R2="$2"
	shift 2;;
	-h | --help) Help; exit;;
	-* | --*) unknown="$1"; echo -e "Unknown option: ${unknown}"; Help; exit;;
	*) shift;
	esac
done

if [ -d $output ]
then
	echo -e "WARNING: ${output} already exists !"
else
	mkdir "$output"
fi

number_controls=$(ls -1 ${controls} | wc -l)
number_controls=$(("${number_controls}" / 2))
number_cases=$(ls -1 ${cases} | wc -l)
number_cases=$(("${number_cases}" / 2))
seq -f 'control%g:' 1 "${number_controls}" > tempcol1
seq -f 'case%g:' 1 "${number_cases}" >> tempcol1

readlink -f ${controls}*"$R1"* > tempcol2
readlink -f ${cases}*"$R1"* >> tempcol2

paste tempcol1 tempcol2 > temp

readlink -f ${controls}*"$R2"* > tempcol3
readlink -f ${cases}*"$R2"* >> tempcol3

sum=$(("$number_controls" + "$number_cases"))
printf ";%0.s\n" $(seq 1 $sum) > tempsep
paste temp tempsep tempcol3 > "${output}"/kmdiff_fof.txt

rm temp tempsep tempcol1 tempcol2 tempcol3
