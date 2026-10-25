"""Update local artifact path in a extracted mlflow archive"""

import argparse
import shutil
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("folder", type=Path, help="folder contaning mlflow.db and mlruns")
args = parser.parse_args()
folder = args.folder.resolve()
database = folder / "mlflow.db"
artifacts = folder / "mlruns"

if not database.is_file() or not artifacts.is_dir():
    raise SystemExit("Error: the folder must contain mlflow.db and mlrund")

# Keep the original downloaded db before updating its path
backup = folder / "mlflow.db.backup"
if not backup.exists():
    shutil.copy2(database, backup)

connection = sqlite3.connect(database)
with connection:
    experiments = connection.execute(
        "SELECT experiment_id FROM experiments"
    ).fetchall()
    for (experiment_id,) in experiments:
        location = (artifacts / str(experiment_id)).as_uri()
        connection.execute(
            "UPDATE experiments SET artifact_location = ? WHERE experiment_id = ?",
            (location, experiment_id),
        )
    runs = connection.execute(
        "SELECT run_uuid , experiment_id FROM runs"
    ).fetchall()
    for run_id, experiment_id in runs:
        location = (artifacts / str(experiment_id) / run_id / "artifacts").as_uri()
        connection.execute(
            "UPDATE runs SET artifact_uri = ? WHERE run_uuid = ?",
            (location, run_id),
        )

connection.close()
print(f"MLflow artifact paths updated for: {folder}")
