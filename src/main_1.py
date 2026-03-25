from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'  # FIX 1: was 'Normal'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):# we have kept all the filed optional because it is on the user which parameter he wants to update 
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]



def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)
        

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()

    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    data[patient.id] = patient.model_dump(exclude={'id'})  

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})
@app.put('/edit/{patient_id}')#we put patient_id in the path because we need to know which patient record do we want to update
def update_patient(patient_id:str,patient_update:PatientUpdate):#we recieve new data in the variable called patinet_id (type is pydantic model->PatientUpdate)
    # first we will load the data
    data=load_data()
    if patient_id not in data:
        return  HTTPException(status_code=404,detail="Patient_id not found")
    existing_patient_id=data[patient_id]#extract the data of the patient which we want to update
    # covert the pydantic model to dict 
    updated_patient_info=patient_update.model_dump(exclude_unset=True)#exclude_unset is used to exclude the field which are not provided by the user in the request body
    # we will now update the existing patient data with the new data provided to us by the user
    for key,value in updated_patient_info.items():
        existing_patient_id[key]=value
    #existing_patient_id->pydantic object->updated bmi+verdict->pydantic object->dict
    #1)create a new patient object with updated data
    #Note that the updated_patient_info does not contain id filed so we need to add it before creating the patient object
    existing_patient_id['id']=patient_id
    updated_patient_obj=Patient(**existing_patient_id).model_dump()# we did this to update the bmi and verdict field in the existing patient data beacuse thesw two fields are computed field and they will be updated onyl when we create a new pydantic object of the patient whose data is updated
    #2)create a dictionary with 
    existing_patient_id=updated_patient_obj.model_dump(exclude='id')# we will convert the pydantic object to dict so that we can put it back in the data dictionary 
    #3)now will put the updated data back in the data dictionary with same patient_id
    #put back the updated data
    data[patient_id]=existing_patient_id
    save_data(data)
    return JSONResponse(status_code=200,content={'message':"Patient record updated successfully"})


    


