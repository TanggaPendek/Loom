# services/node_service.py
from models.model import ResponseModel

def create_node():
    return ResponseModel(status="success", action="create", message="(placeholder) Create node")

def delete_node():
    return ResponseModel(status="success", action="delete", message="(placeholder) Delete node")

def update_node():
    return ResponseModel(status="success", action="update", message="(placeholder) Update node")
