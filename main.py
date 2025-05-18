from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
import xml.etree.ElementTree as ET
from xml.dom.minidom import Document, parseString
import os
from db import get_db, init_db

app = FastAPI()
templates = Jinja2Templates(directory="templates")

init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/flights", response_class=HTMLResponse)
def list_flights(request: Request):
    db = get_db()
    flights = db.execute("SELECT * FROM flights").fetchall()
    db.close()
    return templates.TemplateResponse("flights.html", {"request": request, "flights": flights})


@app.get("/flights/create", response_class=HTMLResponse)
def create_flight_form(request: Request):
    return templates.TemplateResponse("create_flight.html", {"request": request})


@app.post("/flights/create")
def create_flight(
    flight_number: str = Form(...),
    departure: str = Form(...),
    arrival: str = Form(...),
    datetime: str = Form(...),
    aircraft_id: int = Form(...)
):
    db = get_db()
    exists = db.execute("SELECT * FROM aircraft WHERE id = ?", (aircraft_id,)).fetchone() is not None
    if not exists:
        return {"error": "No such id"}

    db.execute(
        "INSERT INTO flights (flight_number, departure, arrival, datetime, aircraft_id) VALUES (?, ?, ?, ?, ?)",
        (flight_number, departure, arrival, datetime, aircraft_id)
    )
    db.commit()
    db.close()
    return {"message": "Flight added successfully"}


@app.get("/aircraft/create", response_class=HTMLResponse)
def create_aircraft_form(request: Request):
    return templates.TemplateResponse("create_aircraft.html", {"request": request})

@app.get("/aircraft", response_class=HTMLResponse)
def list_aircraft(request: Request):
    db = get_db()
    aircraft = db.execute("SELECT * FROM aircraft").fetchall()
    db.close()
    return templates.TemplateResponse("aircraft.html", {"request": request, "aircraft": aircraft})

@app.post("/aircraft/create")
def create_aircraft(model: str = Form(...), capacity: int = Form(...)):
    db = get_db()
    db.execute("INSERT INTO aircraft (model, capacity) VALUES (?, ?)", (model, capacity))
    db.commit()
    db.close()
    return {"message": "Airplane has been created"}


@app.get("/passengers/create", response_class=HTMLResponse)
def create_passenger_form(request: Request):
    return templates.TemplateResponse("create_passenger.html", {"request": request})


@app.post("/passengers/create")
def create_passenger(name: str = Form(...), flight_id: int = Form(...)):
    db = get_db()
    exists = db.execute("SELECT * FROM flights WHERE id = ?", (flight_id,)).fetchone() is not None
    if not exists:
        return {"error": "No such id"}

    db.execute("INSERT INTO passengers (name, flight_id) VALUES (?, ?)", (name, flight_id))
    db.commit()
    db.close()
    return {"message": "Passanger has been created"}


@app.get("/passengers", response_class=HTMLResponse)
def list_passengers(request: Request):
    db = get_db()
    passengers = db.execute("SELECT * FROM passengers").fetchall()
    db.close()
    return templates.TemplateResponse("passengers.html", {"request": request, "passengers": passengers})


@app.get("/passengers/export")
async def export_passenger():
    db = get_db()
    passengers = db.execute("SELECT * FROM passengers").fetchall()
    db.close()
    
    doc = Document()
    root = doc.createElement('guests')
    doc.appendChild(root)
    
    for passenger in passengers:
        passanger_elem = doc.createElement('passenger')
        
        id_elem = doc.createElement('id')
        id_elem.appendChild(doc.createTextNode(str(passenger[0])))
        passanger_elem.appendChild(id_elem)
        
        name_elem = doc.createElement('name')
        name_elem.appendChild(doc.createTextNode(str(passenger[1])))
        passanger_elem.appendChild(name_elem)
        
        phone_elem = doc.createElement('flight_id')
        phone_elem.appendChild(doc.createTextNode(str(passenger[2])))
        passanger_elem.appendChild(phone_elem)
        
        root.appendChild(passanger_elem)
    
    xml_str = doc.toprettyxml(indent="  ")
    
    return Response(content=xml_str, media_type="application/xml")

@app.post("/passengers/import")
async def import_passengers(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        dom = parseString(contents.decode('utf-8'))
        passengers = dom.getElementsByTagName('passenger')

        imported_count = 0

        db = get_db()

        for guest_elem in passengers:
            name = guest_elem.getElementsByTagName('name')[0].firstChild.data
            flight_id = guest_elem.getElementsByTagName('flight_id')[0].firstChild.data

            db.execute("INSERT INTO passengers (name, flight_id) VALUES (?, ?)", (name, flight_id))
            imported_count += 1

        db.commit()
        db.close()
        return {"message": f"Successfully imported {imported_count} guests"}

    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}

