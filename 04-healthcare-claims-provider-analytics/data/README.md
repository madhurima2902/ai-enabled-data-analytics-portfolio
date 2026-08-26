# Data

The project does not commit real healthcare data.

Run:

```bash
python ../scripts/generate_synthetic_data.py
```

to create the local CSV files:

- `patients.csv`
- `providers.csv`
- `claims.csv`

All records are synthetic and de-identified. The generator intentionally avoids names, exact dates of birth, street addresses, member numbers, medical record numbers, and other direct identifiers.

The generated claim data includes a few controlled data-quality exceptions for profiling practice. These should be identified before KPI calculations.
