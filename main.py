try:
    import ray
    ray.init(runtime_env={"env_vars": {"__MODIN_AUTOIMPORT_PANDAS__": "1"}})
    import modin.pandas as pandas
except ImportError:
    import pandas
import functools

# import charmonium.cache
# charmonium.cache.freeze_config.ignore_all_classes = True
# charmonium.cache.freeze_config.ignore_functions.add(("modin.pandas.io", "read_csv"))
# group = charmonium.cache.MemoizedGroup(size="20GiB")
# @charmonium.cache.memoize(group=group)

hidden_cols = [
    "closed",
    "active",
    "charge_off",
    "charge_off_aged",
    "charge_off_bk",
    "fee_chg_off_reversal_amt",
    "aged_writeoff_amt",
    "bankruptcy_writeoff_amt",
    "fc_reversals",
    "fee_reversals",
    "other_writeoff_amt",
    "writeoff_type_bko",
    "writeoff_type_fraud_kiting",
    "writeoff_type_fraud_synthetic",
    "writeoff_type_deceased",
    "writeoff_type_other",
    "writeoff_type_aged",
    "writeoff_type_settlement",
    "writeoff_type_repo",
    "writeoff_type_null",
    # "mth_code",
    # "snapshot",
]
dtypes = {
    "financial_active": bool,
    "net_payment_behaviour_tripd": "category",
    "promotion_flag": bool,
    "variable_rate_index": bool,
    "account_status_code": "category",
    "active_12_mths": bool,
    "bank_fico_buckets_20": "category",
    "charge_off_reason_code": "category",
    "mob": int,
    "open_closed_flag": "category",
    "ever_delinquent_flg": bool,
    "nbr_mths_due": int,
    "variable_rate_margin": float,
    "stmt_balance": float,
    "prev_balance": float,
    "net_sales": float,
    "net_payments": float,
    "purchase_active": bool,
    "credit_limit_amt": float,
    "credit_limit_pa": float,
    "closed": bool,
    "active": bool,
    "charge_off": bool,
    "charge_off_aged": bool,
    "charge_off_bk": bool,
    "principal_amt": float,
    "principal_amt_chrg_off": float,
    "total_writeoff_amt": float,
    "fee_chg_off_reversal_amt": float,
    "net_finance_charge": float,
    "non_principal_amount_gross": float,
    "non_principal_amount_net": float,
    "non_principal_amount_stmt": float,
    "aged_writeoff_amt": float,
    "bankruptcy_writeoff_amt": float,
    "fc_reversals": float,
    "fee_reversals": float,
    "fraud_writeoff_amt": float,
    "other_writeoff_amt": float,
    "promo_bal_amt": float,
    "recovery_amt": float,
    "writeoff_type_bko": bool,
    "writeoff_type_fraud_kiting": bool,
    "writeoff_type_fraud_synthetic": bool,
    "writeoff_type_deceased": bool,
    "writeoff_type_other": bool,
    "writeoff_type_aged": bool,
    "writeoff_type_settlement": bool,
    "writeoff_type_fraud_other": bool,
    "writeoff_type_repo": bool,
    "writeoff_type_null": bool,
    "writeoff_date": str,
    "due_account_2": bool,
    "due_account_3": bool,
    "due_account_4": bool,
    "due_account_5": bool,
    "due_account_6": bool,
    "due_account_7": bool,
    "due_account_8": bool,
    "due_balance_2": float,
    "due_balance_3": float,
    "due_balance_4": float,
    "due_balance_5": float,
    "due_balance_6": float,
    "due_balance_7": float,
    "due_balance_8": float,
    "snapshot": str,
    "mth_code": str,
    "industry": "category",
}

@functools.lru_cache()
def load_data(train):
    return pandas.read_csv(
        "data/training_data.csv" if train else "data/forecast_starting_data.csv",
        dtype=dtypes,
    ).assign(**{
        "writeoff_date": lambda df: pandas.to_datetime(df["writeoff_date"], format="%Y-%m-%d"),
        "snapshot"     : lambda df: pandas.to_datetime(df["snapshot"     ], format="%Y%m"),
        "mth_code"     : lambda df: pandas.to_datetime(df["mth_code"     ], format="%Y%m"),
    }).drop(columns=[] if train else hidden_cols)

def evaluate(estimator, scoring="f1"):
    import sklearn.model_selection
    import sklearn.base
    training_data = load_data(train=True)
    cross_validator = sklearn.model_selection.StratifiedShuffleSplit(
        n_splits=5,
        test_size=None,
        train_size=None,
        random_state=0,
    )
    training_cols = [
        col
        for col in training_data.columns
        if col not in hidden_cols
    ]
    scores = sklearn.model_selection.cross_val_score(
        estimator,
        training_data[training_cols],
        training_data["charge_off"],
        scoring=scoring,
        cv=cross_validator,
        n_jobs=-1,
    )
    print(scores.mean(), scores.stdev())
    estimator = sklearn.base.clone(estimator)
    estimator.fit(training_data[training_cols], training_data["charge_off"])
    forecast_data = load_data(train=False)
    estimator.predict(forecast_data)


def evaluate_survival(survival_estimator):
    training_data = load_data(train=True)
    survival_estimator.train(training_data)
    forecast_data = load_data(train=False)
    forecast_index = pandas.Index([datetime.datetime(2020, i, 1) for i in range(2, 13)] + [datetime.datetime(2021, 1, 1)])
    lifetimes = survival_estimator.predict_survival_function(forecast_data, (forecast_index - forecast_index.min()) / pandas.Timedelta(days=30))
    print(lifetimes.shape, (len(forecast_data), len(forecast_index)))
    lifetimes.sum(axis=1) * forecast_data.size()


if __name__ == "__main__":
    training_data = load_data(train=True)
    forecast_data = load_data(train=False)
    print(pandas.isna(training_data).sum().to_string())
