from fastapi.testclient import TestClient
from app.api import app
from cargar_csv import load_fixture

# Inicializamos el cliente de pruebas para nuestra API de FastAPI
client = TestClient(app)


def test_read_root():
    """Prueba que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API REST de TechStore activa"}


def test_get_order():
    """Prueba la obtención de detalles de un pedido por ID."""
    order_id = 1
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["status"] == "DRAFT"


def test_confirm_order():
    """Prueba la transición de confirmación de un pedido."""
    order_id = 1
    response = client.post(f"/orders/{order_id}/confirm")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CONFIRMED"


def test_ship_order():
    """Prueba la transición de envío de un pedido."""
    order_id = 1
    response = client.post(f"/orders/{order_id}/ship")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SHIPPED"


from app.api import orders_db # Asegúrate de importar orders_db si está ahí, o inicialízalo

def test_cancel_order():
    """Prueba la cancelación asegurando que el pedido exista en la BD de la API."""
    # Inyectamos o aseguramos el pedido en el diccionario de la API para que no dé 404
    orders_db["0001"] = load_fixture()["O001"]
    
    order_id = 1
    response = client.post(f"/orders/{order_id}/cancel")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANCELLED"