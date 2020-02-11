from typing import Union, List
from datetime import datetime
from pydantic import Field, BaseModel, validator, ValidationError
from app.enums import PaymentChoices, DocumentTypes, FiscalTaxesNumbers, ReturnDocumentType
from app.schemas import DefaultSuccessResponse, CashierData
from .models import Ware, Order
from marshmallow_mongoengine import ModelSchema, fields


class RequestWares(BaseModel):
    name: str = Field(..., title='Название товара', min_length=3)
    barcode: str = Field(..., title='Баркод товара', min_length=4)
    code: str = Field(..., title='Локальный код товара', min_length=4)
    quantity: int = Field(..., title='Количество', ge=1)
    price: float = Field(..., title='Цена товара', ge=0.5)
    tax_number: FiscalTaxesNumbers = Field(..., title='Номер налога (настоящий номер налога в фискальном регистраторе)')


class ResponseWares:
    pass


class RequestCreateOrder(CashierData):
    payment_type: PaymentChoices = Field(..., title='Тип оплаты (наличный/безналичный)')
    amount_entered: float = Field(0, title='Если наличный расчет, то это поле показывает сколько денег дал клиент')
    wares: List[RequestWares] = Field(..., title='Список позиций в покупке', min_items=1)

    @validator('amount_entered', always=True)
    def nonzero_amount_entered(cls, v, values, **kwargs):
        if values['payment_type'] == PaymentChoices.CASH:
            if v <= 0 or isinstance(v, type(None)):
                raise ValueError(f'amount_entered must be greater than zero, '
                                 f'if it is payment with real money')
        return v


class ResponseCreateOrder(DefaultSuccessResponse, CashierData):
    internal_order_uuid: str = Field(..., title='Уникальный идентификатор заказа в кассе', min_length=9)
    cheque_number: int = Field(..., title='Номер созданного чека', gt=0)
    payment_type: PaymentChoices = Field(..., title='Тип оплаты (наличный/безналичный)')
    document_type: int = Field(DocumentTypes.PAYMENT, title='Тип документа (оплата)')
    payment_link: str = Field("", title='Ссылка платежа (пустая, если наличный расчет)')
    order_time: datetime = Field(..., title='Время заказа (из фискального регистратора). Пример: "2020-01-28 09:00:27"')
    cash_character: str = Field(..., title='Символ кассы. Необходим для совершения заказа/оплаты', min_length=1)
    device_id: str = Field(..., title='Идентификатор устройства (кассы)', min_length=4)


class RequestReturnOrder(CashierData):
    internal_order_uuid: str = Field(..., title='Уникальный идентификатор заказа в кассе', min_length=9)
    payment_link: str = Field("", title='Ссылка платежа (пустая, если возврат по наличному платежу)')


class ResponseReturnOrder(DefaultSuccessResponse):
    msg: str = Field('Заказ отменен', title='Сообщение об успешной отмене')


class PaygateWareSchema(ModelSchema):
    class Meta:
        model = Ware


class PaygateOrderSchema(ModelSchema):
    wares = fields.Nested(PaygateWareSchema, many=True)

    class Meta:
        model = Order
