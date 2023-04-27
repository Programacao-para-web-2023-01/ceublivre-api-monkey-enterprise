from fastapi import FastAPI, Request, Response, status
import mysql.connector
from typing import Optional
from pydantic import BaseModel
#-----------------------------------------------------
from fastapi.responses import RedirectResponse
from google.oauth2 import client
import jwt
#-----------------------------------------------------
import requests
#-----------------------------------------------------
app = FastAPI()

users = {
    1: {
        "user": "admin",
        "password": "admin",
        "email": "admin@admin.com"
    }
}

conn = mysql.connector.connect(
    user='admin',
    password='admin',
    host='localhost',
    database='monkeyFlip'
)
cur = conn.cursor()
cur.execute("")
rows = cur.fetchall()

class User(BaseModel):
    user: str
    password: str
    email: str

class UpdateUser(BaseModel):
    user: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

@app.get("/")
async def read_root():
    return {"name" : "first data"}
if __name__== "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000)

@app.post("/create-user/{user_id}")
def create_user(user_id : int, user : User):
    if user_id in users:
        return {"Error": "User already exist"}

    users[user_id] = user
    return users[user_id]


@app.post("/update-user/{user_id}")
def update_user(user_id: int, user: UpdateUser):
    if user_id not in users:
        return {"Error": "User not registered"}

    if user.user != None:
        users[user_id].name = user.user

    if user.password != None:
        users[user_id].password = user.password

    if user.email != None:
        users[user_id].email = user.email

    return users[user_id]

#---------------------------------------------

@app.get("/login/google")
async def login_google(request: Request):
    flow = client.OAuth2WebServerFlow(
        client_id='',
        client_secret='',
        scope='openid email profile',
        redirect_uri='http://localhost:8000/callback/google'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)

@app.get("/callback/google")
async def callback_google(request: Request, response: Response, code: str):
    flow = client.OAuth2WebServerFlow(
        client_id='',
        client_secret='',
        scope='openid email profile',
        redirect_uri='http://localhost:8000/callback/google'
    )
    credentials = flow.step2_exchange(code)
    id_token = credentials.id_token['sub']
    email = credentials.id_token['email']
    # Gere um token de autenticação e retorne-o como resposta para o usuário
    access_token = generate_token(id_token, email)
    response.set_cookie(key="access_token", value=access_token)
    return RedirectResponse(url='/home', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/home")
async def home(request: Request):
    access_token = request.cookies.get("access_token")
    user = await get_user_from_token(access_token)
    if user:
        return {"message": f"Welcome, {user['email']}!"}
    else:
        return RedirectResponse(url='/login/google')

async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, '', algorithms=['HS256'])
        return {"user_id": payload['user_id'], "email": payload['email']}
    except jwt.exceptions.DecodeError:
        return None

def generate_token(user_id: str, email: str):
    payload = {"user_id": user_id, "email": email}
    token = jwt.encode(payload, '', algorithm='HS256')
    return token

#-----------------------------------------------------------------------

@app.get("/login/facebook")
async def login_facebook(request: Request):
    params = {
        'client_id': '',
        'redirect_uri': 'http://localhost:8000/callback/facebook',
        'scope': 'email',
        'response_type': 'code'
    }
    url = 'https://www.facebook.com/v12.0/dialog/oauth'
    return RedirectResponse(url=url, params=params)

@app.get("/callback/facebook")
async def callback_facebook(request: Request, response: Response, code: str):
    url = 'https://graph.facebook.com/v12.0/oauth/access_token'
    params = {
        'client_id': '',
        'client_secret': '',
        'redirect_uri': 'http://localhost:8000/callback/facebook',
        'code': code
    }
    res = requests.get(url, params=params)
    access_token = res.json()['access_token']
    url = 'https://graph.facebook.com/v12.0/me'
    params = {'access_token': access_token, 'fields': 'id,email'}
    res = requests.get(url, params=params)
    user_id = res.json()['id']
    email = res.json()['email']
    # Gere um token de autenticação e retorne-o como resposta para o usuário
    access_token = generate_token(user_id, email)
    response.set_cookie(key="access_token", value=access_token)
    return RedirectResponse(url='/home', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/home")
async def home(request: Request):
    access_token = request.cookies.get("access_token")
    user = await get_user_from_token(access_token)
    if user:
        return {"message": f"Welcome, {user['email']}!"}
    else:
        return RedirectResponse(url='/login/facebook')

async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, '', algorithms=['HS256'])
        return {"user_id": payload['user_id'], "email": payload['email']}
    except jwt.exceptions.DecodeError:
        return None

def generate_token(user_id: str, email: str):
    payload = {"user_id": user_id, "email": email}
    token = jwt.encode(payload, '', algorithm='HS256')
    return token

#-----------------------------------------------------

cur.close()
conn.close()