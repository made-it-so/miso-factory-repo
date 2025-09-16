import uuid
from fastapi import APIRouter, status, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import genesis_models, db_models
from .auth_router import get_db
from .. import orchestrator # Import the new orchestrator

router = APIRouter(
    prefix="/genesis",
    tags=["Genesis Pipeline"],
)

def run_genesis_pipeline_task(job_id: str, prompt: str):
    """
    The background task now calls the true orchestrator.
    """
    db = SessionLocal()
    try:
        job = db.query(db_models.GenesisJob).filter(db_models.GenesisJob.id == job_id).first()
        if not job:
            print(f"BACKGROUND_ERROR: Job {job_id} not found in DB.")
            return

        job.status = "in_progress"
        db.commit()

        # Call the real agent pipeline
        final_result = orchestrator.run_pipeline(job_id, prompt)
        
        job.status = "complete"
        job.result = final_result
        db.commit()

    finally:
        db.close()

@router.post("/create", status_code=status.HTTP_202_ACCEPTED, response_model=genesis_models.GenesisJob)
async def create_genesis_job(request: genesis_models.GenesisRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    new_job = db_models.GenesisJob(id=job_id, prompt=request.prompt, status="accepted")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    background_tasks.add_task(run_genesis_pipeline_task, new_job.id, new_job.prompt)
    
    return genesis_models.GenesisJob(
        job_id=new_job.id,
        status=new_job.status,
        message="Genesis Pipeline job has been accepted and is running in the background."
    )

@router.get("/status/{job_id}", response_model=genesis_models.GenesisJob)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(db_models.GenesisJob).filter(db_models.GenesisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return genesis_models.GenesisJob(
        job_id=job.id,
        status=job.status,
        message=job.result or "Pipeline is processing."
    )
