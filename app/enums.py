from enum import IntEnum, Enum
from config import temp_payment_service_url as payment_service


class PaygateURLs(Enum):
    new_order = payment_service + '/createorder'
    cancel_order = payment_service + '/cancelpay',
    open_shift = payment_service + '/openshift',
    close_shift = payment_service + '/closeshift',
    insert_cash = payment_service + '/cashin',
    remove_cash = payment_service + '/cashout'
    register_cash = payment_service + '/regcash'

    def __get__(self, instance, owner):
        return self.value


class FiscalTaxesNumbers(IntEnum):
    tax_10_percent = 1
    tax_20_percent = 0


class CashboxTaxesNumbers(IntEnum):
    tax_10_percent = 10
    tax_20_percent = 20


class CashPayment(IntEnum):
    """ Тип оплаты: Наличный расчет """
    CASH = 0


class NonCashPayment(IntEnum):
    """ Тип оплаты: Безналичный расчет """
    NON_CASH = 1


class PaymentChoices(IntEnum):
    CASH = CashPayment.CASH
    NON_CASH = NonCashPayment.NON_CASH


class PaymentDocumentType(IntEnum):
    """ Тип документа: Оплата """
    PAYMENT = 2


class ReturnDocumentType(IntEnum):
    """ Тип документа: Возврат """
    RETURN = 3


class InsertDocumentType(IntEnum):
    """ Тип документа: Внесение """
    INSERT = 4


class RemoveDocumentType(IntEnum):
    """ Тип документа: Изъятие """
    REMOVE = 5


class DocumentTypes(IntEnum):
    PAYMENT = PaymentDocumentType.PAYMENT
    RETURN = ReturnDocumentType.RETURN
    INSERT = InsertDocumentType.INSERT
    REMOVE = RemoveDocumentType.REMOVE