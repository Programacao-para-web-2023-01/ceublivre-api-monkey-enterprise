from fastapi import FastAPI
import mysql.connector

app = FastAPI()

conn = mysql.connector.connect(
    user='admin',
    password='admin',
    host='localhost',
    database='monkeyFlip'
)
cur = conn.cursor()
cur.execute("")
rows = cur.fetchall()

@app.get("/")
async def read_root():
    return {"name" : "first data"}
if __name__== "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000)

cur.close()
conn.close()