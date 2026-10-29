from decimal import Decimal

class Specification:
    """Clase base para todas las especificaciones de negocio."""
    def is_satisfied_by(self, order) -> bool:
        raise NotImplementedError

    def __and__(self, other):
        return AndSpec(self, other)

    def __or__(self, other):
        return OrSpec(self, other)

    def __invert__(self):
        return NotSpec(self)


class AndSpec(Specification):
    """Combina dos especificaciones con una operación lógica AND."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order) -> bool:
        return (self.left.is_satisfied_by(order) 
                and self.right.is_satisfied_by(order))


class OrSpec(Specification):
    """Combina dos especificaciones con una operación lógica OR."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order) -> bool:
        return (self.left.is_satisfied_by(order) 
                or self.right.is_satisfied_by(order))


class NotSpec(Specification):
    """Niega una especificación con una operación lógica NOT."""
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied_by(self, order) -> bool:
        return not self.spec.is_satisfied_by(order)




class MinimumAmountSpec(Specification):
    """Valida que el monto total del pedido sea mayor estrictamente al umbral."""
    def __init__(self, threshold: Decimal):
        self.threshold = threshold

    def is_satisfied_by(self, order) -> bool:
        return order.total.amount > self.threshold


class VIPCustomerSpec(Specification):
    """valida que el cliente asociado al pedido sea VIP."""
    def is_satisfied_by(self, order) -> bool:
        return order.customer.is_vip


class MinimumUnitsSpec(Specification):
    """ valida que el pedido contenga al menos un numero minimo de unidades."""
    def __init__(self, min_units: int = 4):
        self.min_units = min_units

    def is_satisfied_by(self, order) -> bool:
        return order.units >= self.min_units


class ActivePromotionSpec(Specification):
    """valida si el pedido tiene una promocion activa aplicada."""
    def is_satisfied_by(self, order) -> bool:
        return order.has_promotion


# regla de descuento del 10%
ten_percent = (
    MinimumAmountSpec(Decimal("500"))
    & VIPCustomerSpec()
    & MinimumUnitsSpec(4)
    & ~ActivePromotionSpec()
)

# regla de descuento del 5% 
five_percent = (
    MinimumAmountSpec(Decimal("5000"))
    & ~ActivePromotionSpec()
)

# combinacion con OR ,si ambas se cumplen la logica prioriza el 10%
discount_rule = ten_percent | five_percent