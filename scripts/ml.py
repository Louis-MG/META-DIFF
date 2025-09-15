import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from sklearn.feature_selection import mutual_info_classif
import argparse
import sys

np.random.seed(42)

from utils import get_clusters, save_figures, get_ordinations
from models_configs import import_models
from train import process_model

# main call
if __name__ == "__main__":
    print("Running GP-CV")
    parser = argparse.ArgumentParser(description="Run GP-CV")
    parser.add_argument(
        "--n_features",
        type=int,
        default=-1,
        help="Number of features, for debugging purpose. -1 for all features.",
    )
    parser.add_argument(
        "--experiment_name", type=str, default="", help="Experiment name"
    )
    parser.add_argument(
        "--nk_input_features",
        type=int,
        default=5,
        help="Number of thousands of features used.",
    )
    parser.add_argument("--use_mi", type=int, default=0, help="Use mutual information")
    parser.add_argument("--models_done", type=str, default="", help="")
    parser.add_argument("--n_calls", type=int, default=20, help="Number of calls")
    parser.add_argument("--n_splits", type=int, default=5, help="Number of splits")
    parser.add_argument("--log_neptune", type=int, default=0, help="Log to neptune")
    parser.add_argument("--log_shap", type=int, default=0, help="Log shap values")
    parser.add_argument("--input", type=str, default="", help="Input file")
    parser.add_argument("--output", type=str, default="", help="Output directory")

    args = parser.parse_args()

    models_done = args.models_done.split(",")
    df = pd.read_csv(f"{args.input}", sep="\t").transpose()

    experiment_name = f"{args.experiment_name}"
    os.makedirs(f"{args.output}/{experiment_name}/histograms", exist_ok=True)

    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    df = df.astype(float)

    # Keep only the 1000 for testing
    df = df.iloc[:, : args.n_features]

    if df.to_numpy().std() == 0:
        print(
            "Error: Unitigs have the same quantification in all samples.",
            file=sys.stderr,
        )
        exit(0)

    Y = np.array(df.index)
    # remove the dots and everything after control or case in Y
    Y = [y.split(".")[0] for y in Y]
    # onehot encoding
    df.index = Y
    # Make controls 0 and cases 1
    Y = pd.Series([0 if "control" in y else 1 for y in df.index])
    # Make Y onehot
    X = df
    # Counter(Y)
    # make a progress bar
    if args.use_mi == 1:
        mi = mutual_info_classif(X, Y)
        # Make plots of the mutual information
        # make a progress bar
        sns.histplot(mi, bins=50)
        plt.savefig(f"{args.output}/{experiment_name}/histograms/mutual_info_gain.png")
        plt.close()
    else:
        mi = np.ones(X.shape[1])
    # Sort the features by mutual information
    from operator import itemgetter

    sorted_mi = sorted(enumerate(mi), key=itemgetter(1))
    sorted_mi = [x[0] for x in sorted_mi]
    X_sorted = X.iloc[:, sorted_mi]

    save_figures(X_sorted, args.output, experiment_name)
    # get the clusters
    clusters = get_clusters(X_sorted)
    get_ordinations(X_sorted, Y, experiment_name, args.output)
    # get the models
    models, hparam_names, spaces = import_models(models_done)

    data = {
        "X": X_sorted.copy(),
        "y": Y.copy(),
        "group": pd.Series(list(X.index)),
        "clusters": clusters[3],
    }

    table = [["Model", "valid_MCC"]]
    for model, name in zip(models, list(spaces.keys())):
        display(Markdown(f"##{name}"))
        print(f"### Processing {name}")
        # n_splits=5 serait mieux mais coince
        table = process_model(
            model,
            data,
            mi,
            name,
            experiment_name,
            hparam_names[name],
            spaces[name],
            args,
        )


def log_shap(run, args_dict):
    # explain all the predictions in the test set
    # explainer = shap.KernelExplainer(svc_linear.predict_proba, X_train[:100])
    # Chemin de sortie SHAP harmonisé et créé si besoin
    exp_name = args_dict["exp_name"]
    base_output = args_dict.get("output", ".")
    shap_dir = os.path.join(base_output, "ML", exp_name, "shap")
    os.makedirs(shap_dir, exist_ok=True)

    for group in ["valid", "test"]:
        if group not in args_dict["inputs"]:
            continue
        # TODO Problem with not enough memory...
        try:
            run = log_explainer(run, group, args_dict)
        except Exception as e:
            print(f"Problem with logging {group}: {e}")
            continue
    return run


def log_explainer(run, group, args_dict):
    model = args_dict["model"]
    model_name = args_dict["model_name"]
    x_df = args_dict["inputs"][group]
    labels = args_dict["labels"][group]
    exp_name = args_dict["exp_name"]
    # Dossier de sortie harmonisé et créé si besoin
    output = f"{args_dict['output']}/ML/{exp_name}"
    os.makedirs(output, exist_ok=True)

    unique_classes = np.unique(labels)
    # The explainer doesn't like tensors, hence the f function
    f = lambda x: model.predict(x)
    X = x_df.to_numpy(dtype=np.float32)

    if model_name == "xgb":
        model = model.get_booster()
    if model_name in ["xgboost", "xgb", "lightgbm", "rfr", "rfc"]:
        explainer = shap.TreeExplainer(model)
    elif model_name in ["linreg", "logreg", "qda", "lda"]:
        explainer = shap.LinearExplainer(model, X)
    else:
        stratified_split = StratifiedShuffleSplit(
            n_splits=1, test_size=10, random_state=42
        )
        indices = stratified_split.split(x_df, labels).__next__()[1]
        x_df = x_df.iloc[indices]
        explainer = shap.KernelExplainer(f, x_df)
        X = x_df.to_numpy(dtype=np.float32)

    shap_values = explainer(X)
    if len(unique_classes) == 2:
        if hasattr(shap_values, "base_values") and hasattr(shap_values, "values"):
            if (
                np.ndim(shap_values.base_values) > 1
                and shap_values.base_values.shape[-1] == 2
            ):
                shap_values_df = pd.DataFrame(
                    np.c_[shap_values.base_values[:, 0], shap_values.values[:, :, 0]],
                    columns=["bv"] + list(x_df.columns),
                )
            else:
                shap_values_df = pd.DataFrame(
                    np.c_[shap_values.base_values, shap_values.values],
                    columns=["bv"] + list(x_df.columns),
                )
        else:
            # Sécurise le cas où l’API SHAP renverrait un array simple
            base_val = np.mean(shap_values) if np.ndim(shap_values) == 2 else 0.0
            shap_values_df = pd.DataFrame(
                np.c_[np.full((X.shape[0], 1), base_val), shap_values],
                columns=["bv"] + list(x_df.columns),
            )

        # Remove shap values that are 0
        shap_values_df = shap_values_df.loc[:, (shap_values_df != 0).any(axis=0)]
        # Save the shap values
        shap_values_df.to_csv(f"{output}/{group}_shap.csv", index=False)

        # Agrégation absolue normalisée
        shap_agg = shap_values_df.abs().sum(0)
        total = shap_agg.sum()
        if total == 0:
            return run
        shap_agg = shap_agg / total

        try:
            # Getting the base value
            bv = shap_agg["bv"]
            label = unique_classes[0]
            # Dropping the base value
            shap_agg = shap_agg.drop("bv")

            shap_agg.to_csv(f"{output}/{group}_linear_shap_{label}_abs.csv")
            if run is not None:
                run[f"shap/linear_{group}_{label}"].upload(
                    f"{output}/{group}_linear_shap_{label}_abs.csv"
                )

            shap_agg.transpose().hist(bins=100, figsize=(10, 10))
            plt.xlabel("SHAP value")
            plt.ylabel("Frequency")
            plt.title(f"base_value: {np.round(bv, 2)}")
            plt.savefig(f"{output}/{group}_linear_shap_{label}_hist_abs.png")
            plt.close()
            if run is not None:
                run[f"shap/linear_{group}_{label}_hist"].upload(
                    f"{output}/{group}_linear_shap_{label}_hist_abs.png"
                )

            # KDE
            shap_agg.abs().sort_values(ascending=False).plot(
                kind="kde", figsize=(10, 10)
            )
            plt.xlim(0, shap_agg.abs().max())
            plt.xlabel("Density")
            plt.ylabel("Frequency")
            plt.title(f"base_value: {np.round(bv, 2)}")
            plt.savefig(f"{output}/{group}_linear_shap_{label}_kde_abs.png")
            plt.close()
            if run is not None:
                run[f"shap/linear_{group}_{label}_kde"].upload(
                    f"{output}/{group}_linear_shap_{label}_kde_abs.png"
                )

            # Cumulée et survie
            values, base = np.histogram(shap_agg.abs(), bins=40)
            cumulative = np.cumsum(values)
            plt.figure(figsize=(12, 8))
            plt.plot(base[:-1], cumulative, c="blue", label="Cumulative")
            plt.plot(
                base[:-1], len(shap_agg.abs()) - cumulative, c="green", label="Survival"
            )
            plt.xlabel("SHAP value")
            plt.ylabel("Count")
            plt.title(
                f"Cumulative and survival functions - base_value: {np.round(bv, 2)}"
            )
            plt.legend()
            plt.savefig(f"{output}/{group}_linear_shap_{label}_cum_surv_abs.png")
            plt.close()
            if run is not None:
                run[f"shap/linear_{group}_{label}_cum_surv"].upload(
                    f"{output}/{group}_linear_shap_{label}_cum_surv_abs.png"
                )
        except Exception as e:
            print(f"Problem while summarizing SHAP values for group {group}: {e}")
    return run
