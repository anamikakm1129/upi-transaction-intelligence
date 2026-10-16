from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
import io
import pandas as pd
from typing import Dict, Any, Optional
from ...services.data_quality_service import DataQualityService
from ...models.schemas import DataQualitySummaryResponse, ProcessingRunResponse
from ...utils.logging_config import logger

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # 25 MB

@router.get("/summary", response_model=DataQualitySummaryResponse)
def get_data_quality_summary():
    """Retrieve latest data quality inspection and validation health report."""
    return DataQualityService.get_latest_summary()

@router.get("/quarantined")
def get_quarantined_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit")
):
    """Retrieve segregated quarantined records (duplicates, invalid amounts, unparseable dates)."""
    return DataQualityService.get_quarantined_records(page=page, page_size=page_size)

@router.post("/validate-upload")
async def validate_csv_upload(file: UploadFile = File(...)):
    """
    Step 1 of Upload Workflow:
    Validates CSV file schema and checks columns without storing yet.
    Allows user to review data quality indicators before confirming ingestion.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a valid .csv file."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        logger.error(f"Failed to parse CSV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(e)}"
        )

    try:
        return DataQualityService.validate_uploaded_csv(df, filename=file.filename)
    except Exception as e:
        logger.error(f"Validation inspection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed: {str(e)}"
        )

@router.post("/upload", response_model=ProcessingRunResponse)
async def upload_csv_dataset(file: UploadFile = File(...)):
    """
    Step 2 of Upload Workflow (Ingest & Process):
    Ingests, cleans, quarantines invalid rows, detects anomalies, and generates SQL reporting tables.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a valid .csv file."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        logger.error(f"Failed to parse CSV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(e)}"
        )

    try:
        result = DataQualityService.process_uploaded_csv(df, filename=file.filename)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected processing error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while processing transaction dataset."
        )
