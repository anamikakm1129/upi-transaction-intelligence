from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import Response, FileResponse
import os
from typing import Optional
from ...services.export_service import ExportService
from ...services.data_quality_service import DataQualityService
from ...models.schemas import ProcessingRunResponse
from ...utils.logging_config import logger

router = APIRouter(tags=["Reports & Processing"])

@router.post("/processing/run", response_model=ProcessingRunResponse)
def reprocess_existing_dataset():
    """Trigger the processing pipeline on the currently uploaded raw dataset."""
    try:
        return DataQualityService.reprocess_current_dataset()
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Failed to process dataset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dataset: {str(e)}"
        )

@router.get("/reports/export")
def export_report(
    report_type: str = Query("daily", description="Report type: daily, customers, merchants, hourly, anomalies, data_quality, transactions"),
    format: str = Query("csv", description="Format: csv, parquet")
):
    """
    Download dashboard-ready reports in CSV or Parquet format.
    Derived strictly from user-uploaded transaction records.
    """
    fmt = format.lower().strip()
    if fmt == "parquet":
        parquet_path = ExportService.get_parquet_path()
        if not parquet_path or not os.path.exists(parquet_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parquet processed dataset not found. Please upload a transaction CSV first."
            )
        return FileResponse(
            path=parquet_path,
            filename="cleaned_transactions.parquet",
            media_type="application/octet-stream"
        )
    elif fmt == "csv":
        try:
            csv_content, filename = ExportService.generate_report_csv(report_type)
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate CSV report.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format. Choose 'csv' or 'parquet'.")
