"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from src.storage import DataStore

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize persistent data store
datastore = DataStore(data_file="data/activities.json")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return datastore.get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        datastore.add_participant(activity_name, email)
        return {"message": f"Signed up {email} for {activity_name}"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        datastore.remove_participant(activity_name, email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
