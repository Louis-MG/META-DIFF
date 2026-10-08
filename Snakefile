"""
Pipeline for META-DIFF
"""

configfile: "./config.yaml"

##########################################################
############            MAIN RULE            #############
##########################################################

rule all:
    input:
        expand(config["project_path"] + f"{config['experiment_name']}" + "/kmdiff_output/{condition}_kmers.fasta", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "k/mdiff_output/{condition}_kmers.unitigs.fa", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/functional_annotation/{condition}_unitigs.filtered.fa", condition = config["condition"]),
        expand(config['project_path'] + f"{config['experiment_name']}" + "/functional_annotation/bakta/{condition}.faa", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/biomarker/{condition}.aggregated.fa", condition = config["condition"]),
        config["project_path"] + f"{config['experiment_name']}" + "/biomarker/G/index.json",
        expand(config["project_path"] + f"{config['experiment_name']}" + "/functional_annotation/bakta/{condition}.tsv", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/functional_annotation/{condition}_unitigs_to_clade_and_gene_functions.tsv", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/taxonomy/kraken_{condition}.output", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/taxonomy/kraken_{condition}.report", condition = config["condition"]),
        expand(config["project_path"] + f"{config['experiment_name']}" + "/taxonomy/{condition}_clades.tsv", condition = config["condition"]),
        config["project_path"] + f"{config['experiment_name']}" + "/biomarker/top_unitigs.fa",
        config["project_path"] + f"{config['experiment_name']}" + "/biomarker/output_query_unitigs/biomarkers.tsv",
        config["project_path"] + f"{config['experiment_name']}" + "/ML/" + "/histograms/allclasses.png",
        config["project_path"] + f"{config['experiment_name']}" + "/ML/" + "/ord/lda.png"

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['src_path']}/snakemake/rules/kmdiff.snk"
include: f"{config['src_path']}/snakemake/rules/bcalm.snk"
include: f"{config['src_path']}/snakemake/rules/kraken2.snk"
include: f"{config['src_path']}/snakemake/rules/kmindex.snk"
include: f"{config['src_path']}/snakemake/rules/functional_annotation.snk"
include: f"{config['src_path']}/snakemake/rules/ml.snk"
