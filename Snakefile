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
ruleorder: kmdiff_count > kmdiff_diff > kmdiff_dump > bcalm > mmseqs_bdd > mmseqs_search > mmseqs_convert > mmseqs_sep > mmseqs_sumup > annot_extract_candidates > prodigal > glmnet_extract > glmnet_pval_agg > glmnet_matrix > glmnet_class


##########################################################
############            MAIN RULE            #############
##########################################################

# revoir syntax
rule all:
    input:
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.fasta", condition = config["condition"]),
        config["project_path"] + "pipeline_output/kmdiff_output/significant_kmers_matrix.txt",
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.unitigs.fa", condition = config["condition"]),
        expand(config['project_path'] + "pipeline_output/RESULTS_DB/{condition}_results.m8", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/taxonomy/{condition}_alignment_summary.txt", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_unitigs.1000.fa", condition = config["condition"]),
        expand(config['project_path'] + "pipeline_output/functional_annotation/{condition}_protein_translation.faa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/glmnet/{condition}_unclassified.fa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/glmnet/{condition}_unclassified.aggregated.fa", condition = config["condition"]),
        config["project_path"] + "pipeline_output/functional_annotation/metabolic_summary__heatmap.pdf",
        config['project_path'] + "pipeline_output/glmnet/top_kmers.tsv",
        config["project_path"] + "pipeline_output/glmnet/best_model.txt"

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['src_path']}/snakemake/rules/kmdiff.snk"
include: f"{config['src_path']}/snakemake/rules/bcalm.snk"
include: f"{config['src_path']}/snakemake/rules/mmseqs.snk"
include: f"{config['src_path']}/snakemake/rules/functional_annotation.snk"
include: f"{config['src_path']}/snakemake/rules/glmnet.snk"
