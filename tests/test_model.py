"""Testnivå 3: modell. Kontrakt och reproducerbarhet."""

import hashlib
import json

import joblib
import numpy as np
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from churn.data import (
    DATAKATALOG,
    FEATURES,
    dela_upp,
    las_data,
    skapa_features,
)
from churn.model import DATAFIL, SEED, main, trana_och_utvardera


@pytest.fixture(scope="module")
def resultat():
    return trana_och_utvardera()


def test_modellkontrakt(resultat):
    modell, _ = resultat
    X, _ = dela_upp(skapa_features(las_data().head(5)))

    assert list(X.columns) == FEATURES

    sannolikhet = modell.predict_proba(X)

    assert sannolikhet.shape == (5, 2)
    assert np.all((sannolikhet >= 0) & (sannolikhet <= 1))


def test_reproducerbar(resultat):
    _, matvarden = resultat
    _, igen = trana_och_utvardera()

    assert igen == matvarden


def test_roc_auc_minst_070(resultat):
    _, matvarden = resultat

    assert matvarden["roc_auc"] >= 0.70, (
        f"ROC AUC för låg: {matvarden['roc_auc']:.3f}."
    )


def test_modell_slar_dummy(resultat):
    _, matvarden = resultat

    X, y = dela_upp(skapa_features(las_data()))

    # Use the same split settings as the trained model
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=SEED, stratify=y
    )

    dummy = DummyClassifier(strategy="prior")
    dummy.fit(X_train, y_train)

    dummy_sannolikhet = dummy.predict_proba(X_test)[:, 1]
    dummy_auc = roc_auc_score(y_test, dummy_sannolikhet)

    assert matvarden["roc_auc"] > dummy_auc, (
        f"Model ROC AUC {matvarden['roc_auc']:.3f} "
        f"must exceed DummyClassifier ROC AUC {dummy_auc:.3f}."
    )


def test_saved_model_and_metadata(tmp_path, monkeypatch):
    # Simulate the commit in GitHub Actions
    commit_sha = "a" * 40
    monkeypatch.setenv("GITHUB_SHA", commit_sha)

    main(utkatalog=tmp_path)

    model_path = tmp_path / "modell.joblib"
    metrics_path = tmp_path / "matvarden.json"

    assert model_path.is_file()
    assert metrics_path.is_file()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    # Calculate the dataset's file in bytes.
    expected_data_hash = hashlib.sha256(
        (DATAKATALOG / DATAFIL).read_bytes()
    ).hexdigest()

    assert metrics["commit"] == commit_sha
    assert metrics["datafil"] == DATAFIL
    assert metrics["data_sha256"] == expected_data_hash
    assert 0 <= metrics["roc_auc"] <= 1
    assert 0 <= metrics["accuracy"] <= 1

    # Verify that the saved model can be loaded and used for prediction
    saved_model = joblib.load(model_path)
    X, _ = dela_upp(skapa_features(las_data().head(5)))
    probabilities = saved_model.predict_proba(X)

    assert probabilities.shape == (5, 2)
    assert np.all((probabilities >= 0) & (probabilities <= 1))