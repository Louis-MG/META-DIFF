# META-DIFF

This is the repository of the pipeline META-KMER, which detects sequences in differential abundance between two conditions, and annotates them taxonomicaly and functionaly.

# Motivation

Metagenomics becomes increasingly important in building our kmowledge about microbes. Links between microbiomes perturbations and diseases are regularily uncovered. Using kmer-based methods, this pipeline allows its user to quickly find microbial DNA sequences in differential abundances between two conditions (e.g. healthy and not healthy), and annotate them taxonomicaly and functionaly. The pipline also isolates unclassified sequences and build apredictive model based on the most significant unitigs' kmers abundances. 

# Workflow

The workflow is described by the following figure :

![Schematic of the META-DIFF pipeline](/figures/pipelinev3.png?raw=true "Pipeline Overview")

# Output

The output is divided in several key files:
 - case/control alignement summaries.
 - case/control funcitonal annotation in the form of a barplot, table and a heatmap of pathways detected.
 - performance of a classification model based on glmnet and the kmer counts of the most significant unclassified sequences. 

![Barplot](/figures/metabolic_summary__barplot.pdf "Example of a barplot of pathways complete at 90%") ![Heatmap](/figures/metabolic_summary__heatmap.pdf "Example of a heatmap of pathways complete at 90%")

# Installation

Clone the repository:
```bash
git clone https://github.com/Louis-MG/META-DIFF.git
```

Get your functional database ready by following instructions at (MicrobeAnnotator)[https://github.com/cruizperez/MicrobeAnnotator]. Dont worry, it's jusst a few lines that take a while.
Copy the path to the MicrobeAnnotator_DB in the `snakemake/config` file:
```text
microbeannotator_db_path: /path/to/MicrobeAnnotator_DB
```

Get your taxonomic database ready by looking at (mmseqs documentation)[https://github.com/soedinglab/MMseqs2/wiki] (look at the module `createdb`). Again, just a few lines and fasta files.
Copy the path to your mmseqs-formated taxonomic database in the the `snakemake/config` file:
```text
taxonomic_db_path: /path/to/mmseqs_DB
```

# Usage

Build a file-of-files yourself or using the provided script:
```bash
bash kmdiff_fof_prep.sh --help
```

Provide the fof.txt to the snakemake pipeline:
```bash

```


# Issues

If you have any issues, let me know in the Issues space, with an informative title and description.

# Citations

