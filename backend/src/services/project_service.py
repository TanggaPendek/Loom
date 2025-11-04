# services/project_service.py
from models.model import ResponseModel

def save_project():
    return ResponseModel(status="success", action="save", message="(placeholder) Save project")

def load_project():
    return ResponseModel(status="success", action="load", message="(placeholder) Load project")

def delete_project():
    return ResponseModel(status="success", action="delete", message="(placeholder) Delete project")
