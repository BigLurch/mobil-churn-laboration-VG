"""Tests for the model quality gate."""

import json
import pytest

from churn.evaluate import main

@pytest.mark.parametrize("roc_auc", [1.20, -0.10, float("nan")])
def test_invalid_roc_auc_is_rejected(tmp_path, monkeypatch, roc_auc):
    monkeypatch.setenv("MIN_ROC_AUC", "0.70")

    metrics_path = tmp_path / "matvarden.json"
    metrics = {"roc_auc": roc_auc}
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    result = main([str(metrics_path)])

    assert result == 1

@pytest.mark.parametrize(
    "roc_auc, expected_result",
    [
        (0.69, 1),
        (0.70, 0),
        (0.80, 0),
        (1.00, 0),
    ],
)
def test_quality_threshold(tmp_path, monkeypatch, roc_auc, expected_result):
    monkeypatch.setenv("MIN_ROC_AUC", "0.70")

    metrics_path = tmp_path / "matvarden.json"
    metrics = {"roc_auc": roc_auc}
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    result = main([str(metrics_path)])

    assert result == expected_result

def test_nan_threshold_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("MIN_ROC_AUC", "nan")

    metrics_path = tmp_path / "matvarden.json"
    metrics = {"roc_auc": 0.80}
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    result = main([str(metrics_path)])

    assert result == 1