from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")

mydb = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)

mycursor = mydb.cursor()

@app.get("/")
async def root(request: Request):
    mycursor.execute("SELECT id FROM Bill order by id desc limit 1")
    bill = (mycursor.fetchone())[0]
    # print(bill)
    # Fetch data from the MySQL database (you can replace this with your actual data)
    mycursor.execute("SELECT * FROM OrderDetail where order_id = %s",(bill,))
    data = mycursor.fetchall()
    # return data
    # print(data)
    # print(type(data))
    summed_data = {}
    for item in data:
        ID, order_id, name, amount, price_per_amount, sum_price = item
        if name in summed_data:
            summed_data[name][3] += amount  # Accumulate the 'amount'
            summed_data[name][5] += sum_price  # Accumulate the 'sum_price'
        else:
            summed_data[name] = [ID, order_id, name, amount, price_per_amount, sum_price]

    list_data = [tuple(values) for values in summed_data.values()]

    # print(list_data)
    # Render the HTML template and pass the data
    return templates.TemplateResponse("web_01.html", {"request": request, "data": list_data})

@app.get("/bill")
async def bill(request: Request):
    mycursor.execute("SELECT * FROM Bill order by id desc limit 1")
    bill = (mycursor.fetchone())[0]

    # Fetch data from the MySQL database (you can replace this with your actual data)
    mycursor.execute("SELECT * FROM OrderDetail where order_id = %s",(bill,))
    data = mycursor.fetchall()

    summed_data = {}
    for item in data:
        ID, order_id, name, amount, price_per_amount, sum_price = item
        if name in summed_data:
            summed_data[name][3] += amount  # Accumulate the 'amount'
            summed_data[name][5] += sum_price  # Accumulate the 'sum_price'
        else:
            summed_data[name] = [ID, order_id, name, amount, price_per_amount, sum_price]

    list_data = [tuple(values) for values in summed_data.values()]

    # Fetch data from the MySQL database (you can replace this with your actual data)
    mycursor.execute("SELECT amount,price FROM OrderDetail where order_id = %s",(bill,))
    data = mycursor.fetchall()
    # return(bill,data)

    total_price=0
    for amount, price in data: 
        total_price+= amount* price
    # # return total_price
    mycursor.execute('UPDATE Bill SET total=%s where id=%s' ,(total_price,bill))
    mydb.commit()
    # # print(list_data)
    # # Render the HTML template and pass the data
    return templates.TemplateResponse("bill.html", {"request": request, "data": list_data})

@app.post("/add_data/{order_id}/{name}/{price}")
async def add_data(request: Request, order_id: int, name: str, price: float):
    sql = "INSERT INTO OrderDetail (id, order_id, product_name, amount, price, sum_price) VALUES (NULL,%s, %s, %s, %s, %s)"
    val = (order_id, name, 1, price, price)
    mycursor.execute(sql, val)
    mydb.commit()
    return {"status": "ok"}

@app.get("/db_now")
async def db_now(request: Request):
    mycursor.execute("SELECT * FROM Bill order by id desc limit 1")
    data = (mycursor.fetchone())[0]
    return data

@app.post("/create_bill")
async def cb(request: Request):
    mycursor.execute('INSERT INTO Bill (id, date, Total) VALUES (null, NOW(), 0)')
    mydb.commit()
    return {"status": "ok"}