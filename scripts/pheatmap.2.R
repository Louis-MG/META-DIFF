pheatmap.2 <-function (mat, color = colorRampPalette(rev(brewer.pal(n = 7, 
                                                       name = "RdYlBu")))(100), kmeans_k = NA, breaks = NA, border_color = "grey60", 
          cellwidth = NA, cellheight = NA, scale = "none", cluster_rows = TRUE, 
          cluster_cols = TRUE, clustering_distance_rows = "euclidean", 
          clustering_distance_cols = "euclidean", clustering_method = "complete", 
          clustering_callback = identity2, cutree_rows = NA, cutree_cols = NA, 
          treeheight_row = ifelse((class(cluster_rows) == "hclust") || 
                                    cluster_rows, 50, 0), treeheight_col = ifelse((class(cluster_cols) == 
                                                                                     "hclust") || cluster_cols, 50, 0), legend = TRUE, legend_breaks = NA, 
          legend_labels = NA, annotation_row = NA, annotation_col = NA, 
          annotation = NA, annotation_colors = NA, annotation_legend = TRUE, 
          annotation_names_row = TRUE, annotation_names_col = TRUE,angle_col = NULL,hjust_col = NULL,vjust_col = NULL,
          drop_levels = TRUE, show_rownames = T, show_colnames = T, 
          main = NA, fontsize = 10, fontsize_row = fontsize, fontsize_col = fontsize, 
          display_numbers = F, number_format = "%.2f", number_color = "grey30", 
          fontsize_number = 0.8 * fontsize, gaps_row = NULL, gaps_col = NULL, 
          labels_row = NULL, labels_col = NULL, filename = NA, width = NA, 
          height = NA, silent = FALSE, na_col = "#DDDDDD", nstart=1,...) 
{
  if (is.null(labels_row)) {
    labels_row = rownames(mat)
  }
  if (is.null(angle_col)) {
    angle_col = "90"
  }
  if (is.null(hjust_col)) {
    hjust_col = "1"
  }
  if (is.null(vjust_col)) {
    vjust_col = "0"
  }
  if (is.null(labels_col)) {
    labels_col = colnames(mat)
  }
  mat = as.matrix(mat)
  if (scale != "none") {
    mat = scale_mat(mat, scale)
    if (is.na2(breaks)) {
      breaks = generate_breaks(mat, length(color), center = T)
    }
  }
  if (!is.na(kmeans_k)) {
    km = kmeans(mat, kmeans_k, iter.max = 100,nstart=nstart)
    mat = km$centers
    t = table(km$cluster)
    labels_row = sprintf("Cluster: %s Size: %d", names(t), 
                         t)
  }
  else {
    km = NA
  }
  if (is.matrix(display_numbers) | is.data.frame(display_numbers)) {
    if (nrow(display_numbers) != nrow(mat) | ncol(display_numbers) != 
        ncol(mat)) {
      stop("If display_numbers provided as matrix, its dimensions have to match with mat")
    }
    display_numbers = as.matrix(display_numbers)
    fmat = matrix(as.character(display_numbers), nrow = nrow(display_numbers), 
                  ncol = ncol(display_numbers))
    fmat_draw = TRUE
  }
  else {
    if (display_numbers) {
      fmat = matrix(sprintf(number_format, mat), nrow = nrow(mat), 
                    ncol = ncol(mat))
      fmat_draw = TRUE
    }
    else {
      fmat = matrix(NA, nrow = nrow(mat), ncol = ncol(mat))
      fmat_draw = FALSE
    }
  }
  if ((class(cluster_rows) == "hclust") || cluster_rows) {
    if (class(cluster_rows) == "hclust") {
      tree_row = cluster_rows
    }
    else {
      tree_row = cluster_mat(mat, distance = clustering_distance_rows, 
                             method = clustering_method)
      tree_row = clustering_callback(tree_row, mat)
    }
    mat = mat[tree_row$order, , drop = FALSE]
    fmat = fmat[tree_row$order, , drop = FALSE]
    labels_row = labels_row[tree_row$order]
    if (!is.na(cutree_rows)) {
      gaps_row = find_gaps(tree_row, cutree_rows)
    }
    else {
      gaps_row = NULL
    }
  }
  else {
    tree_row = NA
    treeheight_row = 0
  }
  if ((class(cluster_cols) == "hclust") || cluster_cols) {
    if (class(cluster_cols) == "hclust") {
      tree_col = cluster_cols
    }
    else {
      tree_col = cluster_mat(t(mat), distance = clustering_distance_cols, 
                             method = clustering_method)
      tree_col = clustering_callback(tree_col, t(mat))
    }
    mat = mat[, tree_col$order, drop = FALSE]
    fmat = fmat[, tree_col$order, drop = FALSE]
    labels_col = labels_col[tree_col$order]
    if (!is.na(cutree_cols)) {
      gaps_col = find_gaps(tree_col, cutree_cols)
    }
    else {
      gaps_col = NULL
    }
  }
  else {
    tree_col = NA
    treeheight_col = 0
  }
  attr(fmat, "draw") = fmat_draw
  if (!is.na2(legend_breaks) & !is.na2(legend_labels)) {
    if (length(legend_breaks) != length(legend_labels)) {
      stop("Lengths of legend_breaks and legend_labels must be the same")
    }
  }
  if (is.na2(breaks)) {
    breaks = generate_breaks(as.vector(mat), length(color))
  }
  if (legend & is.na2(legend_breaks)) {
    legend = grid.pretty(range(as.vector(breaks)))
    names(legend) = legend
  }
  else if (legend & !is.na2(legend_breaks)) {
    legend = legend_breaks[legend_breaks >= min(breaks) & 
                             legend_breaks <= max(breaks)]
    if (!is.na2(legend_labels)) {
      legend_labels = legend_labels[legend_breaks >= min(breaks) & 
                                      legend_breaks <= max(breaks)]
      names(legend) = legend_labels
    }
    else {
      names(legend) = legend
    }
  }
  else {
    legend = NA
  }
  mat = scale_colours(mat, col = color, breaks = breaks, na_col = na_col)
  if (is.na2(annotation_col) & !is.na2(annotation)) {
    annotation_col = annotation
  }
  if (!is.na2(annotation_col)) {
    annotation_col = annotation_col[colnames(mat), , drop = F]
  }
  if (!is.na2(annotation_row)) {
    annotation_row = annotation_row[rownames(mat), , drop = F]
  }
  annotation = c(annotation_row, annotation_col)
  annotation = annotation[unlist(lapply(annotation, function(x) !is.na2(x)))]
  if (length(annotation) != 0) {
    annotation_colors = generate_annotation_colours(annotation, 
                                                    annotation_colors, drop = drop_levels)
  }
  else {
    annotation_colors = NA
  }
  if (!show_rownames) {
    labels_row = NULL
  }
  if (!show_colnames) {
    labels_col = NULL
  }
  pdf(file = NULL)
  gt = heatmap_motor(mat, border_color = border_color, cellwidth = cellwidth, 
                     cellheight = cellheight, treeheight_col = treeheight_col, 
                     treeheight_row = treeheight_row, tree_col = tree_col, 
                     tree_row = tree_row, filename = filename, width = width, 
                     height = height, breaks = breaks, color = color, legend = legend, 
                     annotation_row = annotation_row, annotation_col = annotation_col,angle_col = angle_col,hjust_col = hjust_col,vjust_col = vjust_col, 
                     annotation_colors = annotation_colors, annotation_legend = annotation_legend, 
                     annotation_names_row = annotation_names_row, annotation_names_col = annotation_names_col, 
                     main = main, fontsize = fontsize, fontsize_row = fontsize_row, 
                     fontsize_col = fontsize_col, fmat = fmat, fontsize_number = fontsize_number, 
                     number_color = number_color, gaps_row = gaps_row, gaps_col = gaps_col, 
                     labels_row = labels_row, labels_col = labels_col, ...)
  dev.off()
  if (is.na(filename) & !silent) {
    grid.newpage()
    grid.draw(gt)
  }
  invisible(structure(list(tree_row = tree_row, tree_col = tree_col, 
                           kmeans = km, gtable = gt), class = "pheatmap"))
}

environment(pheatmap.2)<- environment(pheatmap)

  
