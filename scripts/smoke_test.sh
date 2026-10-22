#!/usr/bin/env bash

set -euo pipefail

IMAGE="${1:-churn-docker:dev}"

echo "=================================="
echo " Starting Docker smoke-test"
echo " Image: $IMAGE"
echo "=================================="

echo "[1/2] Testing model and call list..."

docker run --rm "$IMAGE" python -c '
import csv
import math
import subprocess
from pathlib import Path

output = Path("outputs/ringlista.csv")
output.unlink(missing_ok=True)

subprocess.run(
    ["python", "-m", "churn.score"],
    check=True
)

assert output.is_file(), "Ringlista saknas!"

with output.open(newline="") as file:
    reader = csv.DictReader(file)
    assert reader.fieldnames == ["kund_id", "risk"], \
        f"Fel kolumner: {reader.fieldnames}"
    rows = list(reader)

assert len(rows) == 100, \
    f"Förväntade 100 kunder, fick {len(rows)}"

ids = [row["kund_id"] for row in rows]
assert all(ids), "Tomma kund-ID hittades"
assert len(ids) == len(set(ids)), \
    "Dubbla kund-ID hittades"

risker = [float(row["risk"]) for row in rows]

assert all(
    math.isfinite(risk) and 0 <= risk <= 1
    for risk in risker
), "Ogiltiga riskvärden hittades"

assert risker == sorted(risker, reverse=True), \
    "Ringlistan är inte sorterad efter risk"

print("PASS: 100 giltiga kunder i ringlistan")
'

echo "[2/2] Testing missing model handling..."

if output=$(docker run --rm "$IMAGE" \
    python -m churn.score outputs/missing-model.joblib 2>&1)
then
    echo "FAIL: Missing model was accepted"
    exit 1
fi

if [[ "$output" == *"FEL: hittar inte outputs/missing-model.joblib"* ]]; then
    echo "PASS: Missing model correctly rejected"
else
    echo "FAIL: Unexpected error from container"
    echo "$output"
    exit 1
fi

echo "=================================="
echo " ALL SMOKE TESTS PASSED"
echo "=================================="