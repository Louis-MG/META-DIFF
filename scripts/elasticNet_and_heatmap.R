#!/usr/bin/env Rscript


########################################################
#
#	LIBRARY
#
########################################################

suppressWarnings(suppressPackageStartupMessages({
	library(pheatmap)
	source("scripts/pheatmap.2.R")
	library("tidyverse")
	library(RColorBrewer)
	library(ggplot2)
	library(glmnet)
	library("caret")
	theme_set(theme_bw())
	getPalette = colorRampPalette(brewer.pal(12, "Set3"))
	library("optparse")
	library(parallel)
	library(compositions)
}))


########################################################
#
#	ARGS
#
########################################################


option_list = list(
  make_option(c("-i", "--input"), type="character", default=NULL,
              help="kmer count matrix file", metavar="character"),
  make_option(c("-o", "--output"), type="character", default=NULL,
              help="output directory for elasticnet signature  table, matrix, heatmap, accuracy and best model ", metavar="character"),
  make_option(c("--case"), type="numeric", default=NULL,
              help="Number of cases", metavar="number"),
  make_option(c("--control"), type="numeric", default=NULL,
              help="Number of controls", metavar="number"),
  make_option(c("-y", "--split"), type="numeric", default=0.75,
              help="proportion to split test and train datasets , default = 0.75", metavar="number"),
  make_option(c("-t", "--threads"), type="numeric", default=1,
              help="threads ", metavar="number")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$input)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
}
if (is.null(opt$output)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (output directory file).n", call.=FALSE)
}
if (is.null(opt$control)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (int).n", call.=FALSE)
}
if (is.null(opt$case)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (int).n", call.=FALSE)
}

output = opt$output
split = as.numeric(opt$split)
thread = opt$threads
case = opt$case
control = opt$control 
kmer_matrix_file = opt$input

accuracy = paste(output, "accuracy.txt", sep = '/')
elasticnet_best_model = paste(output, "best_model.txt", sep = '/')
split = 0.75
thread = 30
outmat <- paste(output, "matrix.tsv", sep = '/')
outheat <- paste(output, "heatmap.pdf", sep = '/')


######################################################################
#
#	IMPORT AND FORMAT DATA
#
######################################################################


df = read.table(kmer_matrix_file, header = F, sep = " ")
df <- column_to_rownames(df, "V1") # etait mat2
kmers <- rownames(df)

df_T <- t(df)
df.clr <- clr(df_T) %>% as.data.frame()
colnames(df.clr) <- kmers

group = c(rep("control", control), rep("case", case))
group <- as.data.frame(group)
formated_df <- cbind(df.clr, group)

######################################################################
#
#	ELASTIC NET
#
######################################################################

default_index = createDataPartition(formated_df$group, p = split, list = FALSE)
default_train = formated_df[default_index, ]
default_test = formated_df[-default_index, ]
cv_10 = trainControl(method = "cv", number = 10)

def_elnet = train(
  group ~ ., data = default_train,
  method = "glmnet",
  trControl = cv_10
)


get_best_result = function(caret_fit) {
  best = which(rownames(caret_fit$results) == rownames(caret_fit$bestTune))
  best_result = caret_fit$results[best, ]
  rownames(best_result) = NULL
  best_result
}

best_model = get_best_result(def_elnet)
write_tsv(best_model, elasticnet_best_model)

calc_acc = function(actual, predicted) {
  mean(actual == predicted)
}

acc_val = "NA"
if (split < 1){
  acc_val = calc_acc(actual = default_test$group,
           predicted = predict(def_elnet, newdata = default_test))
}
writeLines(as.character(acc_val), accuracy)


#Here the coefficient of the new variable was turning to 0. You can extract the variable name retained by the model with:
var = tibble()
kmer_selected = vector() 
if (length(unique(formated_df$group))  == 2) {
  var <- data.frame(as.matrix(coef(def_elnet$finalModel, def_elnet$bestTune$lambda)))
  var <- rownames_to_column(var, "name") # var is a table of intercept values for each kmer for the best model
  kmer_selected <- var$name[var[1]!=0] 
  kmer_selected <- kmer_selected[kmer_selected != "(Intercept)" ]
  kmer_selected <- str_remove_all(kmer_selected, '"')
} else {
  list_var = coef(def_elnet$finalModel, def_elnet$bestTune$lambda)
  l2 = lapply(list_var, function(x) data.frame(as.matrix(x))%>% rownames_to_column("name") )
  var <- as.data.frame(do.call("rbind", l2))
  kmer_selected <- dplyr::filter(var, X1 != 0)$name %>% unique
  kmer_selected <- kmer_selected[kmer_selected != "(Intercept)" ]
  kmer_selected <- str_remove_all(kmer_selected, '"')
}

df_best_kmers = dplyr::filter(rownames_to_column(df, "name"), name %in% kmer_selected)
write_tsv(df_best_kmers, outmat)

##############################################################
#
#	HEATMAP
#
##############################################################

#Plot full heatmap clustered by rows and columns by euclidean distance

# create color palet
col.pal <- brewer.pal(9,"Blues")
# define metrics for clustering
drows1 <- "euclidean"
dcols1 <- "euclidean"

rownames(group) <- rownames(formated_df)
df_best_kmers_for_heatmap <- df_best_kmers %>% column_to_rownames("name")

hm.parameters <- list((df_best_kmers_for_heatmap), 
                      color = col.pal,
                      cellwidth = 15, cellheight = 12, scale = "none",
                      treeheight_row = 200,
                      kmeans_k = NA,
                      show_rownames = T, show_colnames = T,
                      main = "Full heatmap (Ward, Eucl, unsc)",
                      clustering_method = "ward.D2",
                      cluster_rows = TRUE, cluster_cols = FALSE,
                      clustering_distance_rows = drows1, 
                      clustering_distance_cols = dcols1,
                      nstart=1000, angle_col = "90", hjust_col = 1, annotation_col = group)

# To draw to file 
do.call("pheatmap.2", c(hm.parameters, filename=outheat))
