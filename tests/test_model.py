"""Testnivå 3: modell. Kontrakt och reproducerbarhet."""

import json
from pathlib import Path

import numpy as np
import pytest

from churn.data import FEATURES, dela_upp, las_data, skapa_features
from churn.model import trana_och_utvardera
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from churn.model import SEED


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
    modell, matvarden = resultat

    X, y = dela_upp(skapa_features(las_data()))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    dummy = DummyClassifier(strategy="prior") 
    dummy.fit(X_train, y_train)

    dummy_sannolikhet = dummy.predict_proba(X_test)[:, 1]
    dummy_auc = roc_auc_score(y_test, dummy_sannolikhet)

    assert matvarden["roc_auc"] > dummy_auc, (
        f"Modellen ROC AUC {matvarden['roc_auc']:.3f}. "
        f"Måste vara högre än DummyClassifier: {matvarden['roc_auc']:.3f} <= {dummy_auc:.3f}"
    )
