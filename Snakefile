"""
Pipeline for META-DIFF
"""

configfile: "./config.yaml"
ruleorder: kmdiff_count > kmdiff_diff > bcalm > kraken_assign > annot_extract_candidates > kmindex_build > pval_agg > get_query > kmindex_query > prodigal > microbeannotator > summary_table > machine_learning


##########################################################
############            MAIN RULE            #############
##########################################################

rule all:
    input:
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.fasta", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/kmdiff_output/{condition}_kmers.unitigs.fa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_unitigs.filtered.fa", condition = config["condition"]),
        expand(config['project_path'] + "pipeline_output/functional_annotation/{condition}_protein_translation.faa", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_coords.gbk", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/biomarker/{condition}.aggregated.fa", condition = config["condition"]),
        config["project_path"] + "pipeline_output/biomarker/G/index.json",
        expand(config["project_path"] + "pipeline_output/functional_annotation/annotation_results/{condition}_protein_translation.faa.annot", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/annotation_results/{condition}_protein_translation.faa.ko", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/functional_annotation/{condition}_unitigs_to_clade_and_gene_functions.tsv", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/taxonomy/kraken_{condition}.output", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/taxonomy/kraken_{condition}.report", condition = config["condition"]),
        expand(config["project_path"] + "pipeline_output/taxonomy/{condition}_clades.tsv", condition = config["condition"]),
        config["project_path"] + "pipeline_output/biomarker/top_unitigs.fa",
        config["project_path"] + "pipeline_output/biomarker/output_query_unitigs/biomarkers.tsv",
        config["project_path"] + "pipeline_output/ML/" + "/histograms/allclasses.png",
        config["project_path"] + "pipeline_output/ML/" + "/ord/lda.png"

##########################################################
###########            OTHER RULES            ############
##########################################################

include: f"{config['src_path']}/snakemake/rules/kmdiff.snk"
include: f"{config['src_path']}/snakemake/rules/bcalm.snk"
include: f"{config['src_path']}/snakemake/rules/kraken2.snk"
include: f"{config['src_path']}/snakemake/rules/kmindex.snk"
include: f"{config['src_path']}/snakemake/rules/functional_annotation.snk"
include: f"{config['src_path']}/snakemake/rules/ml.snk"
