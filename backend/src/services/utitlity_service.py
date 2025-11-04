# services/utility_service.py
from models.model import ResponseModel

def ping():
    return ResponseModel(status="success", action="ping", message="Server is alive")
