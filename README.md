# META-DIFF :microbe:

This is the repository of the pipeline META-DIFF, which detects sequences in differential abundance between two conditions, and annotates them taxonomicaly and functionaly.

# Motivation

Metagenomics becomes increasingly important in building our knowledge about microbes. Links between microbiome perturbations and diseases are regularily uncovered. Using kmer-based methods, this pipeline allows its users to quickly find microbial DNA sequences in differential abundances between two conditions (e.g. healthy and not healthy), and annotate them taxonomicaly and functionaly. The pipeline also isolates unclassified sequences and builds a predictive model based on the most significant unitigs' kmers abundances. 

:exclamation: Important note: the pipeline can predict genes and annotate functions for prokaryotes only. :exclamation: 

# Workflow

The workflow is described by the following figure :

![Schematic of the META-DIFF pipeline](/figures/pipeline.jpg?raw=true "Pipeline Overview")

# [wiki](https://github.com/Louis-MG/META-DIFF/wiki) ! :books:

# Output

The output is divided in several key files:
 - kraken case/control taxonomic assignment output and report
 - case/control summary of the taxonomic assignment, with taxa (all levels) ordered by number of base assigned 

```
Unclassified    512640685
Bacteroides (taxid 816) 31310507
Prevotella copri (taxid 165179) 15327700
Phocaeicola plebeius (taxid 310297)     14988657
Eubacteriales (taxid 186802)    14963744
Enterobacteriaceae (taxid 543)  12643762
Bacteroidales (taxid 171549)    11334934
Klebsiella (taxid 570)  10345553
Faecalibacterium prausnitzii (taxid 853)        10234613
Bacteria (taxid 2)      10146249
```

 - case/control functional annotation in the form of a barplot, table and a heatmap of pathways detected:

![Heatmap](/figures/metabolic_summary__heatmap.png?raw=true "Example of a heatmap of pathways complete at 90%")

 - performance of a classification model based on glmnet and the kmer counts of the most significant unclassified sequences:

`best_model.txt`:
```
alpha	lambda	Accuracy	Kappa	AccuracySD	KappaSD
1	0.012233193439917463	0.8071428571428572	0.6136666666666667	0.1277013475448753	0.2566471854078626
```
![Heatmap](/figures/heatmap.png "Exemple of a classification heatmap with unclassified k-mers")

 - table of unitigs to functions by condition. Each unitig is linked to the genes it contains and their funciton, KO number.

| Gene ID     | Translated Gene seq      | Unitig ID | Unitig seq | Gene function | KO | CLade |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ----------- |
| Gene1 | ARDENE | Unitig1 | ACGTCGCT | Glucose transferase | K00001 | Bacteroides |
| Gene1 | WPH | Unitig2 | ACGTCGCT | Protease | K00004 | P. plebeius |
| Gene2 | IFPSY | Unitig1 | GTCGATCATG | Oxydase | K00761 | E. coli |

# Requirements 

Check the wiki first, section `Required files format`.
Memory (RAM) needed will depend on the size of your alignment database.
Disk space required mostly depends on the size of your dataset and databases. The number of kmers for 3To of CRC fasta files reached hundreds of millions, wich is about 500G of fasta files for the first step. Other steps will use less disk. The database of `MicrobeAnnotator` is about 690G.

# Installation

Clone the repository:
```bash
git clone https://github.com/Louis-MG/META-DIFF.git
```

Get your functional database ready by following instructions at [MicrobeAnnotator](https://github.com/cruizperez/MicrobeAnnotator). Don't worry, it's just a few lines that take a while.
Copy the path to the MicrobeAnnotator_DB in the `snakemake/config.yaml` file:
```
microbeannotator_db_path: "/path/to/MicrobeAnnotator_DB/"
```

Get your taxonomic database ready by looking at [MMseqs2 documentation](https://github.com/soedinglab/MMseqs2/wiki) (look at the module `createdb`). Again, just a few lines and fasta files.
Copy the path to your MMseqs2-formated taxonomic database in the the `snakemake/config.yaml` file:
```
taxonomic_db_path: "/path/to/mmseqs_DB/DB"
```

# Usage

Build a file-of-files yourself or using the provided script:
```bash
bash kmdiff_fof_prep.sh --help

This script generates the file of file (fof.txt) for kmdiff. Its arguments are:
	--cases -c <PATH> path to the directory of cases samples.
	--controls -C <PATH> path to the directory of control samples.
	--output -o <PATH> path to where the fof should be.
	--help -h displays this help message and exits.

Output is :
	- a fof.txt named after the output parameter. The file is tab separated, format:
		control1: /path/to/control1_read1.fastq ; /path/to/control1_read2.fastq
		control2: /path/to/control2_read1.fastq ; /path/to/control2_read2.fastq
		case1: /path/to/case1_read1.fastq ; /path/to/case1_read2.fastq
		case2: /path/to/case2_read1.fastq ; /path/to/case2_read2.fastq

WARNING: depending of the denomination of your files for paired ends (_R1 and _R2, _1 and _2 ...), you will have to modify lines 55-56 and 60-61. Yeah it's annoying. Add the single-end by hand.
```

Add the last paths to `./snakemake/config.yaml`:
```
# path to this repo, "META-DIFF/" included:
src_path: "/path/to/META-DIFF/"
#kraken db path:
kraken_database_path: "/path/to/db"
#microbeannotator db path:
microbeannotator_db_path: "/path/to/db"
# where your results will be
project_path: "/path/to/your/project/"
# path to your file of file:
fof: "/path/to/your/fof.txt"
```

Finally, ssssstart the pipeline :snake::
```bash
snakemake --cores X --use-conda
```

# Issues

If you have any issues, let me know in the Issues space, with an informative title and description.

# Citations 

Coming soon ! :mortar_board:

