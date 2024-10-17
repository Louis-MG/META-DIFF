"""
Pipeline for META-DIFF
"""
from sympy.strategies import condition, expand

configfile: "./config.yaml"
ruleorder: kmdiff_count > kmdiff_diff > bcalm > kraken_assign > annot_extract_candidates > kmindex_build > pval_agg > get_query > kmindex_query > classification > prodigal > microbeannotator > summary_table


##########################################################
############            MAIN RULE            #############
##########################################################

rule all:
    input:
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.fasta", condition = ["case", "control"]),
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.unitigs.fa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_unitigs.filtered.fa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/glmnet/{condition}_unassigned.unitigs.fa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/glmnet/{condition}_unassigned.aggregated.fa", condition = config["condition"]),
        expand(config['project_path'] + "pipeline_output/functional_annotation/{condition}_protein_translation.faa", condition = config["condition"]),
        config["project_path"] + "pipeline_output/functional_annotation/metabolic_summary__heatmap.pdf",
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_unitigs_to_clade_and_gene_functions.tsv", condition = ['case', 'control']),
        expand(config["project_path"] + "pipeline_output/taxonomy/kraken_{condition}.output", condition = ['case', 'control']),
        expand(config["project_path"] + "pipeline_output/taxonomy/kraken_{condition}.report", condition = ['case', 'control']),
        expand(config["project_path"] + "pipeline_output/taxonomy/{condition}_clades.tsv", condition = ['case', 'control']),
        config["project_path"] + "pipeline_output/biomarker/top_unitigs.fa",
        expand(config["project_path"] + "pipeline_output/biomarker/output_query_unitigs/index.tsv", condition = ['case', 'control'])

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['src_path']}/snakemake/rules/kmdiff.snk"
include: f"{config['src_path']}/snakemake/rules/bcalm.snk"
include: f"{config['src_path']}/snakemake/rules/kraken2.snk"
include: f"{config['src_path']}/snakemake/rules/kmindex.snk"
include: f"{config['src_path']}/snakemake/rules/functional_annotation.snk"
