"""Download and verify the public REES46 source archive."""

import hashlib
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://data.rees46.com/datasets/electronics-events/electronics-events.csv.gz"
DESTINATION = PROJECT_ROOT / "data" / "raw" / "electronics-events.csv.gz"
EXPECTED_SHA256 = "cbcbedc28c39a6b2add493bbbd9f71c061ad9d84087b85e64c442e4d47f418e7"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists() and sha256(DESTINATION) == EXPECTED_SHA256:
        print(f"Verified existing archive: {DESTINATION}")
        return

    partial = DESTINATION.with_suffix(".gz.part")
    urllib.request.urlretrieve(SOURCE_URL, partial)
    actual_checksum = sha256(partial)
    if actual_checksum != EXPECTED_SHA256:
        partial.unlink(missing_ok=True)
        raise ValueError(
            f"Checksum mismatch: expected {EXPECTED_SHA256}, received {actual_checksum}"
        )
    partial.replace(DESTINATION)
    print(f"Downloaded and verified: {DESTINATION}")


if __name__ == "__main__":
    main()
