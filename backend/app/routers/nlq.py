from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas import NLQueryRequest
from ..crud import create_nlq_history_entry 

from backend.app.database import get_db
from backend.app.services.db_executor_service import execute_validated_sql
from backend.app.services.nlq_service import generate_sql_from_nl
from backend.app.schemas import NLQHistory as NLQHistorySchema
from backend.app.models import NLQHistory


from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(prefix="/nlq", tags=["Natural Language Query"])

@router.post("/nlq/generate-sql")
def generate_sql(request: NLQueryRequest, db: Session = Depends(get_db)):
    try:
        generated_sql = generate_sql_from_nl(request.query, db)
        print("Generated SQL:", generated_sql)

        if not generated_sql or not generated_sql.strip():
            create_nlq_history_entry(
                db=db,
                user_input=request.query,
                generated_sql="",
                execution_status="Failed: Validation",
                result_summary="SQL generation returned empty."
            )
            raise HTTPException(status_code=400, detail="Generated SQL is empty.")

        try:
            results = execute_validated_sql(db, generated_sql)
            print("===========================================results====================================")
            print(results)
            print("=====================================================================================")
            summary = f"Returned {len(results)} rows." if isinstance(results, list) else "Executed."
            create_nlq_history_entry(
                db=db,
                user_input=request.query,
                generated_sql=generated_sql,
                execution_status="Success",
                result_summary=summary
            )
            return {
                "generated_sql": generated_sql,
                "results": results
            }

        except Exception as exec_error:
            create_nlq_history_entry(
                db=db,
                user_input=request.query,
                generated_sql=generated_sql,
                execution_status="Failed: Execution",
                result_summary=str(exec_error)
            )
            raise HTTPException(status_code=500, detail=f"Execution error: {str(exec_error)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query handling failed: {str(e)}")




#To show NLQ History in NLQ page
@router.get("/history", response_model=list[NLQHistorySchema])
def get_nlq_history(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(NLQHistory).order_by(NLQHistory.timestamp.desc()).limit(limit).all()




    



