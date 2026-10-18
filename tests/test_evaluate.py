"""Tests for the model quality gate."""

import json

from churn.evaluate import main


def test_roc_auc_above_one_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("MIN_ROC_AUC", "0.70") # set the limit only for the test

    metrics_path = tmp_path / "matvarden.json" # store in a temporary file 
    metrics = {"roc_auc": 1.20}
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    result = main([str(metrics_path)])

    assert result == 1
