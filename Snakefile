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

configfile: "/snakemake/config.yaml"
ruleorder: kmdiff > bcalm > mmseqs_bdd > mmseqs_search > mmseqs_convert > mmseqs_sep > mmseqs_sumup > annot_extract_candidates > prodigal > microbannotator > glmnet_extract > glmnet_pval_agg > glmnet_matrix > glmnet_class


##########################################################
############            MAIN RULE            #############
##########################################################

# revoir syntax
wildcard_constraints:
        wildcard = "[case|control]"

rule all:
    input:
        expand(config["project_path"] + "/pipeline_output/kmdiff_output/{wildcard}_kmers.fasta", wildcard = ["case","control"])
	expand(config["project_path"] + "/pipeline_output/kmdiff_output/{wildcard}_kmers.unitigs.fa", wildcard = ["case","control"])
	expand(config["project_path"] + "/pipeline_output/taxonomy/{wildcard}_alignment_summary.txt", wildcard = ["case","control"]) 
	expand(config["project_path"] + "/pipeline_output/functional_annotation/{wildcard}_.unitigs.1000.fa", wildcard = ["case","control"])

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['project_path']}/gitlab/snakemake/rules/kmdiff.snk"
include: f"{config['project_path']}/gitlab/snakemake/rules/bcalm.snk"
include: f"{config['project_path']}/gitlab/snakemake/rules/mmseqs.snk"
include : f"{config['project_path']}/gitlab/snakemake/rules/funcitonal_annotation.snk"
include : f"{config['project_path']}/gitlab/snakemake/rules/glmnet.snk"
