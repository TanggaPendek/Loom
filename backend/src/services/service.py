from models.model import ActionRequest

async def handle_action(req: ActionRequest):
    action = req.action.lower()
    payload = req.payload

    # You can branch based on action type
    if action == "init":
        return {"message": "Project initialized.", "projectId": req.projectId}

    elif action == "save":
        project = payload.get("project")
        if not project:
            raise Exception("Missing project data in payload.")
        # TODO: actual save logic here
        return {"message": "Project saved successfully.", "projectId": req.projectId}

    elif action == "load":
        # TODO: load from disk or DB
        return {"message": "Project loaded.", "projectId": req.projectId}

    elif action == "run":
        # TODO: start execution or computation
        return {"message": "Run command executed.", "projectId": req.projectId}

    elif action == "stop":
        # TODO: stop process logic
        return {"message": "Stop command executed.", "projectId": req.projectId}

    elif action == "delete":
        # TODO: delete project logic
        return {"message": "Project deleted.", "projectId": req.projectId}

    else:
        raise Exception(f"Unknown action: {req.action}")
