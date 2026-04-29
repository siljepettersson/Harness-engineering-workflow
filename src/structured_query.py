import json
from dataclasses import dataclass
from pathlib import Path

from .config import config


OSLO_RENT_09895_SAMPLE_PATH = (
    config.paths.structured_data_dir
    / "oslo-rent"
    / "oslo-rent-2025-two-room-area-sample.json"
)


@dataclass(frozen=True)
class StructuredRentResult:
    source_table: str
    source_url: str
    retrieval_date: str
    year: str
    number_of_rooms: str
    area_label: str
    average_monthly_rent_nok: int
    average_annual_rent_per_sqm_nok: int


def load_structured_json(path: Path) -> dict:
    """Load a small structured JSON extract from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


def get_oslo_rent_09895_sample(path: Path = OSLO_RENT_09895_SAMPLE_PATH) -> dict:
    """Return the first narrow 09895 seed extract used for structured queries."""
    return load_structured_json(path)


def find_rent_row_by_area(
    area_label: str,
    path: Path = OSLO_RENT_09895_SAMPLE_PATH,
) -> StructuredRentResult:
    """Return the exact published row for a given SSB area label."""
    sample = get_oslo_rent_09895_sample(path)

    for row in sample["rows"]:
        if row["area_label"] == area_label:
            return StructuredRentResult(
                source_table=sample["source_table"],
                source_url=sample["source_url"],
                retrieval_date=sample["retrieval_date"],
                year=sample["year"],
                number_of_rooms=sample["filters"]["number_of_rooms"],
                area_label=row["area_label"],
                average_monthly_rent_nok=row["average_monthly_rent_nok"],
                average_annual_rent_per_sqm_nok=row["average_annual_rent_per_sqm_nok"],
            )

    raise LookupError(
        f"Area label not found in 09895 sample: {area_label}. "
        "Use the exact SSB published area label."
    )
