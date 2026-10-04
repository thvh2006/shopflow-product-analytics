# Data

## Observational event source

**REES46 electronics-store behaviour events**

- Retrieval date: 2026-10-04.
- Official catalogue: https://rees46.com/en/datasets
- Direct archive: https://data.rees46.com/datasets/electronics-events/electronics-events.csv.gz
- Published scope: anonymised e-commerce behaviour events from September 2020 through February 2021.
- Event types: `view`, `cart`, `purchase`.
- Fields: timestamp, event type, product, category, brand, price, user, and source session.

The local raw archive is ignored by Git. To rebuild:

```bash
python -m src.ingestion.download_data
python -m src.ingestion.build_event_database
```

The downloader verifies SHA-256 checksum `cbcbedc28c39a6b2add493bbbd9f71c061ad9d84087b85e64c442e4d47f418e7` before the archive enters the pipeline.

## Experiment data policy

The observational source has no treatment assignment. Experiment datasets are therefore synthetic and generated from versioned code. Their baseline rates are calibrated from this event stream, but remain clearly separated from the public observations.

No synthetic row will be described as a real customer or real experiment participant.
