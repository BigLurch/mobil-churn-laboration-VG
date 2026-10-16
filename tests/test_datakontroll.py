import pandas as pd
import pytest
import pandera.pandas as pa

from kontroller.schema import SCHEMA

def test_orginal_data_passes():
    df = pd.read_csv("data/kundbas.csv")

    SCHEMA.validate(df, lazy=True)

def test_new_delivery_fails():
    df = pd.read_csv("data/kundbas_ny_leverans.csv")

    with pytest.raises(pa.errors.SchemaErrors):
        SCHEMA.validate(df, lazy=True)


@pytest.mark.parametrize("alder", [18, 100])
def test_age_boundaries_pass(alder):
    df = pd.read_csv("data/kundbas.csv").head(1).copy()
    df["alder"] = alder

    SCHEMA.validate(df, lazy=True)


@pytest.mark.parametrize("alder", [17, 101])
def test_age_outside_boundaries_fails(alder):
    df = pd.read_csv("data/kundbas.csv").head(1).copy()
    df["alder"] = alder

    with pytest.raises(pa.errors.SchemaErrors):
        SCHEMA.validate(df, lazy=True)
