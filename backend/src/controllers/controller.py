from fastapi import APIRouter, HTTPException
from models.model import ActionRequest, ResponseModel  # ✅ fixed path
from services.service import handle_action 

router = APIRouter(prefix="/api", tags=["Core"])

@router.post("/command", response_model=ResponseModel)
async def command_controller(request: ActionRequest):
    try:
        result = await handle_action(request)

        return ResponseModel(
            status="success",
            action=request.action,
            message=f"Action '{request.action}' processed successfully.",
            data=result,
        )

    except Exception as e:
        # log or print error in real scenario
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
