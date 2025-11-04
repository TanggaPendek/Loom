# services/connection_service.py
from models.model import ResponseModel

def create_connection():
    return ResponseModel(status="success", action="connect", message="(placeholder) Create connection")

def delete_connection():
    return ResponseModel(status="success", action="disconnect", message="(placeholder) Delete connection")
