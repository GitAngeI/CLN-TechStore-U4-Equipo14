import csv
from decimal import Decimal
from cargar_csv import load_fixture
from app.specifications import ten_percent, five_percent
from app.domain import DomainException, OrderItem

def ejecutar_escenarios():
    print("=" * 70)
    print("     EJECUCIÓN Y VALIDACIÓN DE ESCENARIOS (E01 - E15)")
    print("=" * 70 + "\n")
    
    with open('datos/escenarios.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            caso_id = row.get('caso_id') or row.get('\ufeffcaso_id')
            pedido_id = row['pedido_id']
            accion = row['accion']
            objetivo = row['objetivo']
            pista = row['pista']
            
            # Cargar fixtures limpios para cada caso
            orders = load_fixture()
            order = orders.get(pedido_id)
            
            print(f"[{caso_id}] Pedido: {pedido_id} | Acción: {accion}")
            print(f"     Objetivo: {objetivo} ({pista})")
            
            resultado_real = ""
            
            try:
                if "evaluar_descuento" in accion:
                    aplica_10 = ten_percent.is_satisfied_by(order)
                    aplica_5 = five_percent.is_satisfied_by(order)
                    
                    if aplica_10:
                        desc = "10%"
                    elif aplica_5:
                        desc = "5%"
                    else:
                        desc = "0%"
                    resultado_real = f"Descuento calculado: {desc} (10%:{aplica_10}, 5%:{aplica_5})"
                
                elif accion == "confirmar":
                    order.confirm()
                    resultado_real = f"Éxito -> Estado: {order.status.value}, Eventos: {[e.name for e in order.events]}"
                    
                elif "agregar" in accion:
                    nuevo_item = OrderItem(sku="SKU003", quantity=2, unit_price=Money(Decimal("100.00")))
                    order.add_item(nuevo_item)
                    resultado_real = f"Ítem agregado. Unidades totales: {order.units}"
                    
                elif accion == "confirmar y enviar sin guia":
                    order.confirm()
                    order.ship("")
                    resultado_real = f"Estado: {order.status.value}"
                    
                elif accion == "confirmar dos veces":
                    order.confirm()
                    order.confirm()
                    resultado_real = f"Éxito inesperado (Estado: {order.status.value})"
                    
                elif accion == "confirmar, enviar y cancelar":
                    order.confirm()
                    order.ship("GUIA-TEST-01")
                    order.cancel("Prueba de cancelación")
                    resultado_real = f"Estado: {order.status.value}"
                    
                elif accion == "confirmar, enviar y devolver":
                    order.confirm()
                    order.ship("GUIA-TEST-02")
                    order.deliver()
                    order.return_order()
                    resultado_real = f"Estado final: {order.status.value}, Eventos: {[e.name for e in order.events]}"
                    
                elif accion == "confirmar, enviar y entregar":
                    order.confirm()
                    order.ship("GUIA-TEST-03")
                    order.deliver()
                    resultado_real = f"Estado final: {order.status.value}, Eventos: {[e.name for e in order.events]}"
                    
                else:
                    resultado_real = "Acción personalizada"
                    
                print(f"    -> Resultado Real: {resultado_real}")
                
            except DomainException as e:
                print(f"    -> Resultado Real (Rechazo esperado): {type(e).__name__} -> {str(e)}")
            except Exception as e:
                print(f"    -> Error: {type(e).__name__} -> {str(e)}")
                
            print("-" * 70)

if __name__ == "__main__":
    ejecutar_escenarios()