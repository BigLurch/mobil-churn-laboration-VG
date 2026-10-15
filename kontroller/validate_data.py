import sys 

import pandas as pd
import pandera.pandas as pa

from kontroller.schema import SCHEMA

def main(fil: str) -> int:
    df = pd.read_csv(fil)

    try:
        SCHEMA.validate(df, lazy=True)

    except pa.errors.SchemaErrors as fel:
        print(f"STOPP: {fil} klarar inte av validering!\n")

        print(fel.failure_cases.to_string(index=False))

        return 1

    print(f"OK: {fil} ({len(df)} rader)")
    print(
        f"Medel dataförbrukning: "
        f"{df['data_gb_per_manad'].mean():.1f} GB/mån"
    )

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
