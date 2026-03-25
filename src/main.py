from fastapi import FastAPI
app=FastAPI()# first create an object
# define Endpoints
@app.get("/")# this is the root endpoint
def hello():
    return {"message":"Hello World"}# this is the response that will be sent to the client

@app.get("/about")
def about():
    return {"message":"This is the about page"} 