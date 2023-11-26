from typing import Union
from fastapi import FastAPI, HTTPException, status
import uvicorn
from powerplan import PowerPlan
import os
import json
import glob

app = FastAPI()
HOST = "0.0.0.0"
PORT = 8888
EXAMPLE_FOLDER = "example_payloads"
RESULT_FOLDER = "results"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/productionplan")
def productionplan(request: dict):
    with open(f"{RESULT_FOLDER}/payload.json", 'w') as f:
        json.dump(request, f)
        f.close()

    powerplan = PowerPlan(request)
    powerplan._manage_date()
    result = powerplan._set_merit_order()

    with open(f"{RESULT_FOLDER}/response.json", "w") as r:
        json.dump(result, r)
        r.close()

    return result

@app.post("/productionplan/all")
def productionplanAll():
    files = os.listdir(EXAMPLE_FOLDER)
    list_files = list(filter(lambda k: 'payload' in k, files))
    list_responses = []

    for file in list_files:
        with open(f"{EXAMPLE_FOLDER}/{file}", 'r') as f:
            payload = json.load(f)
            powerplan = PowerPlan(payload)
            powerplan._manage_date()
            result = powerplan._set_merit_order()
            f.close()

        with open(f"{EXAMPLE_FOLDER}/responses/response_{file}", "w") as r:
            list_responses.append("response_" + file)
            json.dump(result, r)
            r.close()
        print(f"Report to the 'response_{file}' for the answer")
    return {"state": "success", "payloads": list_files, "responses": list_responses, "message": "All payloads have been submited, let's check the responses files"}

@app.post("/productionplan/{id}")
def productionplanById(id: int):
    files = os.listdir(EXAMPLE_FOLDER)
    list_files = list(filter(lambda k: f'payload{id}' in k, files))
    if len(list_files) > 0:
        file = list_files[0]
        with open(f"{EXAMPLE_FOLDER}/{file}", 'r') as f:
            payload = json.load(f)
            powerplan = PowerPlan(payload)
            powerplan._manage_date()
            result = powerplan._set_merit_order()
            f.close()

        with open(f"{EXAMPLE_FOLDER}/responses/response_{file}", "w") as r:
            json.dump(result, r)
            r.close()
        print(f"Report to the 'response_{file}' for the answer")
    else:
        result = { "message": "No payload file at this index"}
    return result

if __name__ == "__main__":
    try:
        uvicorn.run(app=app, port=PORT, host=HOST)
    except Exception as e:
        print(f"Error occured: {e}")