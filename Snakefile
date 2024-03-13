"""
Pipeline for META-DIFF
"""

from snakemake.utils import report
from snakemake.utils import R
from datetime import datetime
import os
import os.path
import subprocess
from subprocess import Popen, PIPE
import pandas as pd
from pathlib import Path

configfile: "snakemake/config.yaml"
ruleorder: kmdiff_count > kmdiff_diff > kmdiff_dump > bcalm > mmseqs_bdd > mmseqs_search > mmseqs_convert > mmseqs_sep > mmseqs_sumup > annot_extract_candidates > prodigal > microbeannotator > glmnet_extract > glmnet_pval_agg > glmnet_matrix > glmnet_class


##########################################################
############            MAIN RULE            #############
##########################################################

# revoir syntax
wildcard_constraints:
        wildcard = "[case|control]"

rule all:
    input:
        expand(config["project_path"] + "/pipeline_output/kmdiff_output/{wildcard}_kmers.fasta", wildcard = ["case","control"]),
	expand(config["project_path"] + "/pipeline_output/kmdiff_output/{wildcard}_kmers.unitigs.fa", wildcard = ["case","control"]),
	expand(config["project_path"] + "/pipeline_output/taxonomy/{wildcard}_alignment_summary.txt", wildcard = ["case","control"]),
	expand(config["project_path"] + "/pipeline_output/functional_annotation/{wildcard}_.unitigs.1000.fa", wildcard = ["case","control"]),
	expand(config['project_path'] + "/pipeline_output/functional_annotation/{wildcard}_protein_translation.faa", wildcard = ["case","control"]),
	expand(config["project_path"] + "/pipeline_output/glmnet/{wildcard}_unclassified.fa", wildcard = ["case","control"]),
	expand(config["project_path"] + "/pipeline_output/glmnet/{wildcard}_unclassified.aggregated.fa", wildcard = ["case","control"]),
	config['project_path'] + "/pipeline_output/functional_annotation/metabolic_summary__heatmap.pdf",
	config['project_path'] + "/pipeline_output/glmnet/top_kmers.tsv",
	config['project_path'] + "/pipeline_output/glmnet/best_model.txt"

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['project_path']}/gitlab/snakemake/rules/kmdiff.snk"
include: f"{config['project_path']}/gitlab/snakemake/rules/bcalm.snk"
include: f"{config['project_path']}/gitlab/snakemake/rules/mmseqs.snk"
include : f"{config['project_path']}/gitlab/snakemake/rules/functional_annotation.snk"
include : f"{config['project_path']}/gitlab/snakemake/rules/glmnet.snk"
