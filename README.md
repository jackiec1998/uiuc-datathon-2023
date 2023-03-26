# True Positives Datathon Repository

_Authors:_ Jackie Chan, Sam Grayson, Sarah Simpson, Wenbo Fu.

To reproduce our results, you will need `main.py`, `survival_numerical_cat_macro.ipynb`, `environment.yml`, and the raw data.

The raw data should be placed without renaming into `data/` to reproduce our Notebook.

Once that is done, our Jupyter Notebook can be run with Conda.

```
conda env create --name datathon --file environment.yml
conda run --name datathon jupyter notebook survival_numerical_cat_macro.ipynb
```

