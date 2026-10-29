import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.domain import (
    Money, 
    OrderItem, 
    InvalidOrderData, 
    InvalidOrderTransition, 
    OrderItemLimitExceeded
)
from app.specifications import ten_percent, ActivePromotionSpec
from app.api import app
from cargar_csv import load_fixture

# Cliente para las pruebas de API
client = TestClient(app)

def test_money_negativo():
    """Valida que no se permitan montos de dinero negativos."""
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))

def test_pedido_o001_inicia_draft():
    """Valida la carga inicial del pedido O001."""
    orders = load_fixture()
    assert orders["O001"].status.value == "DRAFT"
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")

def test_21_unidades_excede_limite():
    """Prueba de 21 unidades: exceder el límite de 20 unidades lanza excepción."""
    orders = load_fixture()
    order = orders["O008"]  
    nuevo_item = OrderItem(sku="SKU999", quantity=21, unit_price=Money(Decimal("100.00")))
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(nuevo_item)

def test_cliente_inactivo():
    """Prueba cliente inactivo: confirmar un pedido con cliente inactivo lanza error."""
    orders = load_fixture()
    order = orders["O003"]  
    with pytest.raises(InvalidOrderData):
        order.confirm()

def test_pedido_vacio():
    """Prueba pedido vacío: confirmar un pedido sin artículos lanza error."""
    orders = load_fixture()
    order = orders["O007"]  
    with pytest.raises(InvalidOrderData):
        order.confirm()

def test_descuento_vip():
    """Prueba descuento VIP: evalúa que la especificación de 10% aplique correctamente."""
    orders = load_fixture()
    order = orders["O001"]  
    assert ten_percent.is_satisfied_by(order) is True

def test_promocion_activa():
    """Prueba promoción activa: verifica que se detecte la promoción en el pedido."""
    orders = load_fixture()
    order = orders["O005"]  
    # Usando la especificación o la propiedad directa del pedido
    promo_spec = ActivePromotionSpec()
    assert promo_spec.is_satisfied_by(order) is True
    assert order.has_promotion is True

def test_envio_sin_guia():
    """Prueba envío sin guía: intentar enviar un pedido confirmado con guía vacía falla."""
    orders = load_fixture()
    order = orders["O012"]
    order.confirm()
    with pytest.raises(InvalidOrderData):
        order.ship("")

def test_confirmacion_doble():
    """Prueba confirmación doble: re-confirmar un pedido ya confirmado lanza error de transición."""
    orders = load_fixture()
    order = orders["O013"]
    order.confirm()
    with pytest.raises(InvalidOrderTransition):
        order.confirm()

def test_cancelacion_desde_shipped():
    """Prueba cancelación desde SHIPPED: no se permite cancelar un pedido ya enviado."""
    orders = load_fixture()
    order = orders["O014"]
    order.confirm()
    order.ship("GUIA-TEST-123")
    with pytest.raises(InvalidOrderTransition):
        order.cancel("Intento de cancelación tardía")

def test_http_404_not_found():
    """Prueba respuesta HTTP 404: consultar un pedido inexistente en la API devuelve error 404."""
    response = client.get("/orders/99999")
    assert response.status_code == 404