from pathlib import Path

from fastapi import APIRouter
from samples_api import router as samples
from reference_api import router as reference
from spectra_api import router as spectra
from custody_api import router as custody
from match_experiment import KIND, mark_failed, run_job

router = APIRouter(prefix="/api")
router.include_router(samples)
router.include_router(reference)
router.include_router(spectra)
router.include_router(custody)


def seed(connection):
    connection.execute(Path(__file__).with_name("demo.sql").read_text())
