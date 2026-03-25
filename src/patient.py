import json
from fastapi import FastAPI,Path,HTTPException,Query
#path enhances the readability of the code and makes iteasier to understand the purpose of the parameter

app=FastAPI()

def load_data():
    with open("patients.json") as f:
        data=json.load(f)
    return data
@app.get("/")# this is the root endpoint
def hello():
    return {"message":"Hello World"}
@app.get("/about")
def about():
    return {"message":"This is the about page"} 
@app.get("/view")
def view_patients():
   data=load_data()
   return data
@app.get("/patient/{patient_id}")
def view_patient(patient_id:str=Path(...,description="The ID of the patient to view",example="P001"))  :
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404,detail="Patient not found")
@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort by height, BMI, weight"),
    order: str = Query("asc", description="Order: asc or desc")
):
    valid_fields = ["height", "BMI", "weight"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    data = load_data()

    reverse = True if order == "desc" else False

    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by),
        reverse=reverse
    )

    return sorted_data
    





    