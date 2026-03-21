from fastapi import APIRouter, HTTPException, Response
from core.dependencies import camera_service

router = APIRouter()


@router.post("/enable")
def enable():

    try:
        camera_service.enable()
        return {"status": "enabled"}

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/disable")
def disable():

    camera_service.disable()
    return {"status": "disabled"}


@router.get("/frame")
def frame():

    try:
        img = camera_service.get_frame()

        return Response(
            content=img,
            media_type="image/jpeg"
        )

    except Exception as e:
        raise HTTPException(500, str(e))