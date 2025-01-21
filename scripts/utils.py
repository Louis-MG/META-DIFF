import torch
import numpy as np
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import torch.nn.functional as F
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler
from skopt import gp_minimize
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.model_selection import train_test_split
import os

from concurrent.futures import ThreadPoolExecutor

def augment_data(X_train, y_train, n_aug, p=0, g=0):
    torch.manual_seed(42)
    X_train2 = X_train.copy()
    y_train2 = y_train.copy()
    colnames = X_train.columns
    # y_train2 = np.array([])
    # X_train2 = np.array([])

    if n_aug > 0:
        for _ in range(n_aug):
            y_train2 = np.concatenate([y_train2, y_train])
            tmp = X_train.copy() + g * np.random.normal(0, 1, X_train.shape)
            tmp = tmp.astype(np.float64)

            arr = torch.from_numpy(np.array(tmp).copy())
            tmp = F.dropout(arr, p).detach().cpu().numpy()
            if len(X_train2) > 0:
                X_train2 = np.concatenate([X_train2, tmp], 0)
            else:
                X_train2 = tmp
    X_train2 = pd.DataFrame(X_train2, columns=colnames)
    return X_train2, y_train2

def get_scaler(scaler):
    if scaler == 'robust':
        return RobustScaler
    elif scaler == 'none' or scaler is None or scaler == 'binary':
        return None
    elif scaler == 'standard':
        return StandardScaler
    elif scaler == 'minmax':
        return MinMaxScaler
    else:
        exit('Wrong scaler name')

def save_figures(df, output, experiment_name):
    # Flatten the matrix to a 1D array for distribution plots
    data = df.values.flatten()

    # Create the directory to save the histograms
    os.makedirs(f"{output}/{experiment_name}/histograms", exist_ok=True)

    # 1. Histogram
    plt.figure(figsize=(6, 4))
    plt.hist(data, bins=30, edgecolor='black', alpha=0.7)
    plt.title("Histogram of Matrix Values")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.savefig(f"{output}/{experiment_name}/histograms/allclasses.png")
    plt.close()

    # Make an histogram of the number of zeros per sample
    plt.hist(np.sum(df == 0, axis=1), bins=20)
    plt.xlabel('Number of zeros')
    plt.ylabel('Number of samples')
    plt.title('Histogram of the number of zeros per sample')
    plt.savefig(f"{output}/{experiment_name}/histograms/zeros_per_sample_allclasses.png")
    plt.close()

    plt.hist(np.sum(df == 0, axis=0), bins=20)
    plt.xlabel('Number of zeros')
    plt.ylabel('Number of features')
    plt.title('Histogram of the number of zeros per feature')
    plt.savefig(f"{output}/{experiment_name}/histograms/histogram_zeros_per_feature_allclasses.png")
    plt.close()


def get_clusters(X):
    # kmeans with 1 to 10 clusters
    from sklearn.cluster import KMeans
    inertia = []
    clusters = {}
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, n_init='auto', random_state=42)
        kmeans.fit(X)
        inertia.append(kmeans.inertia_)
        clusters[i] = kmeans.labels_
    plt.plot(range(1, 11), inertia)
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.title('Elbow method')
    plt.show()
    plt.close()

    return clusters

def get_ordinations(X, Y, exp_name, output) -> None:
    """
    Funtcion to create and save ordination plots for visualizing the data

    Args:
        X (_type_): _description_
        Y (_type_): _description_
        exp_name (_type_): _description_
    """
    os.makedirs(f"{output}/{exp_name}/ord", exist_ok=True)
    # Ordinations
    # PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=Y)
    plt.xlabel('PCA1')
    plt.ylabel('PCA2')
    plt.title('PCA')
    plt.savefig(f"{output}/{exp_name}/ord/pca.png")
    plt.close()

    # UMAP
    from umap import UMAP
    umap = UMAP(n_components=2)
    X_umap = umap.fit_transform(X)
    plt.scatter(X_umap[:, 0], X_umap[:, 1], c=Y)
    plt.xlabel('UMAP1')
    plt.ylabel('UMAP2')
    plt.title('UMAP')
    plt.savefig(f"{output}/{exp_name}/ord/umap.png")
    plt.close()

    # NMDS
    from sklearn.manifold import MDS
    mds = MDS(n_components=2)
    X_mds = mds.fit_transform(X)
    plt.scatter(X_mds[:, 0], X_mds[:, 1], c=Y)
    plt.xlabel('MDS1')
    plt.ylabel('MDS2')
    plt.title('MDS')
    plt.savefig(f"{output}/{exp_name}/ord/mds.png")
    plt.close()

    # USE LDA after splitting the data
    lda = LinearDiscriminantAnalysis(n_components=1)
    # train test split
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    X_lda = lda.fit_transform(X_train, y_train)
    plt.scatter(X_lda, np.zeros(X_lda.shape), c=y_train)
    plt.xlabel('LDA')
    plt.title('LDA')
    plt.savefig(f"{output}/{exp_name}/ord/lda.png")
    plt.close()

    # Test scores with LDA
    valid_LDA = lda.transform(X_test)
    test_score = lda.score(X_test, y_test)
    # MCC
    test_mcc = metrics.matthews_corrcoef(y_test, lda.predict(X_test))
    train_mcc = metrics.matthews_corrcoef(y_train, lda.predict(X_train))
    print('Test score with LDA:', test_mcc)
    print('Train score with LDA:', train_mcc)
    plt.scatter(valid_LDA, np.zeros(valid_LDA.shape), c=y_test)
    plt.xlabel('LDA')
    plt.title('LDA')
    plt.savefig(f"{output}/{exp_name}/ord/lda_test.png")
    plt.close()

    # Test scores with QDA
    qda = QuadraticDiscriminantAnalysis()
    qda.fit(X_train, y_train)
    train_score = qda.score(X_train, y_train)
    test_score = qda.score(X_test, y_test)
    # valid_QDA = qda.transform(X_test)
    # MCC
    test_mcc = metrics.matthews_corrcoef(y_test, qda.predict(X_test))
    train_mcc = metrics.matthews_corrcoef(y_train, qda.predict(X_train))
    print('Test score with QDA:', test_mcc)
    print('Train score with QDA:', train_mcc)
    # plt.scatter(valid_QDA, np.zeros(valid_LDA.shape), c=y_test)
