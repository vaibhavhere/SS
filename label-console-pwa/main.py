from fastapi import FastAPI
import subprocess
import sqlite3
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
BARTENDER_PATH = ""
TEMPLATE_PATH = ""
# import win32com.client as win32
# btApp = win32.Dispatch("BarTender.Application")
# btFormat = btApp.Formats.Open("C:\\Users\\SS Auto\\Desktop\\SS.btw", False, "")

# ✅ Serve index.html on home route
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

# ✅ SQLite Database Connection
def get_db_connection():
    conn = sqlite3.connect("ss.db")
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Fetch Folders from Database
@app.get("/api/folders")
async def list_folders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM folders order by name asc")
    folders = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content={"folders": folders})

# ✅ Fetch Files in a Folder from Database
@app.get("/api/folders/{id}")
async def list_sub_files(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE folder_id = ? order by name asc", (id,))
    files = [{"id": row["id"], "name": row["name"], 
    "vehicle": row["vehicle"],
    "description": row["description"],
    "price": row["price"]} for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content={"folders": files})

# ✅ Run a Command (Safeguarded)
class PrintCommand(BaseModel):
    vehicle: str
    description: str
    price: str
    count: str

@app.post("/api/run")
async def run_print_command(command: PrintCommand):
    btFormat.SetNamedSubStringValue("vehicle", command.vehicle)
    btFormat.SetNamedSubStringValue("description", command.description)
    btFormat.SetNamedSubStringValue("price", command.price)

    btFormat.IdenticalCopiesOfLabel = int(command.count)
    btFormat.PrintOut(False, False)
    return {}

class FileCreate(BaseModel):
    id: int
    # name: str
    vehicle: str
    description: str
    price: int


# ✅ API to Save a File
@app.post("/api/files")
async def save_file(file: FileCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO files (id, name, vehicle, description, price, folder_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE 
            SET 
                vehicle = excluded.vehicle, 
                description = excluded.description, 
                price = excluded.price
            """,
            (file.id, '', file.vehicle, file.description, file.price, 0)
        )
        conn.commit()
        return JSONResponse(content=file.dict())
    finally:
        conn.close()
