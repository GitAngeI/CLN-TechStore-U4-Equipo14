from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from cargar_csv import load_fixture

app = FastAPI()
client = TestClient(app)

orders_db = load_fixture()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API REST de TechStore activa"}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    key = f"O00{order_id}" if order_id < 10 else f"O0{order_id}"
    order = orders_db.get(key)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {
        "order_id": order_id,
        "status": order.status.value,
        "units": order.units
    }

@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    key = f"O00{order_id}" if order_id < 10 else f"O0{order_id}"
    order = orders_db.get(key)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status.value == "DRAFT":
        order.confirm()
    return {"status": order.status.value}

@app.post("/orders/{order_id}/ship")
def ship_order(order_id: int):
    key = f"O00{order_id}" if order_id < 10 else f"O0{order_id}"
    order = orders_db.get(key)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order.status.value == "DRAFT":
        order.confirm()
    order.ship("GUIA-API-01")
    return {"status": order.status.value}

@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    # Asegúrate de mapear el ID numérico al formato de tu fixture (ej. "O001")
    key = f"000{order_id}" if order_id < 10 else f"00{order_id}"
    order = orders_db.get(key)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    if order.status.value == "DRAFT":
        order.confirm()
        
    order.cancel("Cancelado por API")
    return {"status": order.status.value}