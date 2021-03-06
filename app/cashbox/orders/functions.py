from copy import deepcopy
from app.kkt_device.decorators import validate_kkt_state, kkt_comport_activation, \
    check_for_opened_shift_in_fiscal
from app import KKTDevice
from app.cashbox.main_cashbox.models import Cashbox, System
from app.exceptions import CashboxException
from app.enums import DocumentTypes, PaymentChoices, PaygateURLs, \
    get_fiscal_tax_from_cashbox_tax
from app.helpers import generate_internal_order_id, get_cheque_number, \
    round_half_down, round_half_up, make_request, request_to_paygate
from .schemas import PaygateOrderSchema, ConvertToResponseCreateOrder, OrderSchema
from .models import Order
from config import CASH_SETTINGS as CS
from app.logging import logging_decorator
from pprint import pprint as pp


@logging_decorator('order_logs.log', 'order_logger', 'CREATE ORDER')
@kkt_comport_activation()
@validate_kkt_state()
@check_for_opened_shift_in_fiscal()
async def create_order(*args, **kwargs):
    cashbox = Cashbox.box()
    # raise CashboxException(data='Holy Shield')
    if not cashbox.cash_character:
        msg = 'Символ кассы отсутствует. Зарегистрируйте'
        raise CashboxException(data=msg)

    req_data, kkt_info = kwargs['valid_schema_data'], kwargs['opened_port_info']
    cashier_name = req_data['cashier_name']
    cashier_id = req_data['cashier_id']
    payment_type = req_data['payment_type']
    document_type = DocumentTypes.PAYMENT.value
    amount_entered = req_data['amount_entered']
    wares = req_data['wares']
    character = cashbox.cash_character
    real_money = False
    order_prefix = f'{character}-'
    order_number = cashbox.get_shift_order_number()

    if payment_type == PaymentChoices.CASH:
        wares = find_and_modify_one_ware_with_discount(wares)
        real_money = True
    elif payment_type == PaymentChoices.NON_CASH:
        amount_entered = 0

    wares = _build_wares(wares)

    kkt_kwargs = {
        'cashier_name': cashier_name,
        'payment_type': payment_type,
        'document_type': document_type,
        'order_prefix': order_prefix,
        'order_number': order_number,
        'amount_entered': amount_entered,
        'wares': wares
    }
    created_order = KKTDevice.handle_order(**kkt_kwargs)

    cashbox.modify_shift_order_number()
    data_to_db = {
        'cashier_name': created_order['cashier_name'],
        'cashier_id': cashier_id,
        'clientOrderID': generate_internal_order_id(),
        'amount': created_order['total_without_discount'],
        'amount_with_discount': created_order['transaction_sum'],
        'creation_date': created_order['datetime'],
        'cashID': cashbox.cash_id,
        'checkNumber': get_cheque_number(created_order['check_number']),
        'order_number': created_order['order_num'],
        'doc_number': created_order['doc_number'],
        'cardHolder': created_order.get('cardholder_name', ''),
        'pan': created_order.get('pan_card', ''),
        'payLink': created_order.get('rrn', ''),
        'payType': payment_type,
        'paid': 1,
    }

    if real_money:
        cashbox.update_shift_money_counter(DocumentTypes.PAYMENT, created_order['transaction_sum'])

    # data_to_db.update({'wares': _build_wares(wares)})
    order, errs = OrderSchema().load({**kkt_kwargs, **data_to_db})
    pp(errs)
    to_paygate, _errs = PaygateOrderSchema().dump(order)
    to_paygate.update({'amount': data_to_db['amount_with_discount']})
    to_paygate.update({'proj': cashbox.project_number})
    to_paygate.update({'url': PaygateURLs.new_order})

    pp('to paygate')
    pp(to_paygate)
    cashbox.add_order(order)
    cashbox.save_paygate_data_for_send(to_paygate)

    to_print = {
        'pref': order_prefix,
        'num': data_to_db['order_number'],
        'wares': wares
    }
    await print_to_secondary_printer(to_print)

    to_response, errs = ConvertToResponseCreateOrder().load(
        {'device_id': System.get_sys_id(), **kkt_kwargs, **data_to_db}
    )
    return to_response


@logging_decorator('order_logs.log', 'order_logger', 'RETURN ORDER')
@kkt_comport_activation()
@validate_kkt_state()
@check_for_opened_shift_in_fiscal()
async def return_order(*args, **kwargs):
    req_data, kkt_info = kwargs['valid_schema_data'], kwargs['opened_port_info']

    cashier_name = req_data['cashier_name']
    cashier_id = req_data['cashier_id']
    order_uuid = req_data['internal_order_uuid']
    doc_type = DocumentTypes.RETURN.value
    cashbox = Cashbox.box()
    order = Order.objects(clientOrderID=order_uuid).first()

    if not order:
        msg = 'Нет такого заказа'
        raise CashboxException(data=msg)

    if order.returned:
        msg = 'Этот заказ уже был возвращен'
        raise CashboxException(data=msg)

    order_dict = OrderSchema().dump(order).data
    kkt_kwargs = {
        'cashier_name': cashier_name,
        'document_type': doc_type,
        'payment_type': order_dict['payType'],
        'wares': order_dict['wares'],
        'amount_entered': order_dict['amount_with_discount'],
        'pay_link': order_dict['payLink'],
        'order_prefix': order_dict['order_prefix']
    }

    canceled_order = KKTDevice.handle_order(**kkt_kwargs)

    if PaymentChoices.CASH.value == kkt_kwargs['payment_type']:
        cashbox.update_shift_money_counter(DocumentTypes.RETURN, order_dict['amount_with_discount'])

    order.returned = True
    order.return_cashier_name = cashier_name
    order.return_cashier_id = cashier_id
    order.return_date = canceled_order['datetime']
    order.save().reload()

    to_paygate = PaygateOrderSchema(only=[
        'clientOrderID', 'cashID', 'checkNumber'
    ]).dump(order).data
    to_paygate.update({'creation_date': canceled_order['datetime']})
    to_paygate.update({'proj': cashbox.project_number})
    to_paygate.update({'url': PaygateURLs.cancel_order})
    cashbox.save_paygate_data_for_send(to_paygate)
    return {}


@logging_decorator('order_logs.log', 'order_logger', 'ROUND PRICE')
async def round_price(*args, **kwargs):
    req_data = kwargs['valid_schema_data']
    data = find_and_modify_one_ware_with_discount(req_data, True)
    return data


def find_and_modify_one_ware_with_discount(wares, get_only_one_discounted_product=False):
    _wares = deepcopy(wares)
    total_sum = 0
    for w in _wares:
        total_sum = w['price'] * w['quantity'] + total_sum

    total_sum = round_half_down(total_sum, 2)
    num_dec = round_half_down(float(str(total_sum - int(total_sum))[1:]), 2)

    item = max(_wares, key=lambda x: x['price'])

    if not num_dec:
        if get_only_one_discounted_product:
            return {'discountedPrice': 0, 'barcode': item['barcode'],
                    'discountedSum': 0, 'orderSum': total_sum,
                    'discountedOrderSum': total_sum}
        else:
            return wares

    disc_price = round_half_down(item['price'] - num_dec, 2)
    total_sum_with_discount = round_half_down(total_sum - num_dec, 2)

    if item['quantity'] == 1:
        item.update({'discountedPrice': disc_price})
        item.update({'discount': num_dec})
    if item['quantity'] > 1:
        new_ware = deepcopy(item)
        item.update({'quantity': item['quantity'] - 1})
        item.update({'discountedPrice': 0})
        new_ware.update({'discountedPrice': disc_price})
        new_ware.update({'discount': num_dec})
        new_ware.update({'quantity': 1})
        _wares.append(new_ware)

    if get_only_one_discounted_product:
        _item = max(_wares, key=lambda x: x.get('discountedPrice', 0))
        return {'barcode': _item['barcode'],
                'discountedPrice': _item['discountedPrice'],
                'discountedSum': num_dec,
                'orderSum': total_sum,
                'discountedOrderSum': total_sum_with_discount}

    return _wares


@logging_decorator('order_logs.log', 'order_logger', 'PARTIAL RETURN ORDER')
@kkt_comport_activation()
@validate_kkt_state()
@check_for_opened_shift_in_fiscal()
async def partial_return(*args, **kwargs):
    cashbox = Cashbox.box()
    kkt_info = kwargs['opened_port_info']
    data = kwargs['valid_schema_data']
    order_id = data['internal_order_uuid']
    doc_type = DocumentTypes.RETURN.value
    data_for_checkstatus = {'proj': cashbox.project_number, 'clientOrderID': order_id}
    checkstatus_url = CS['paygateAddress'] + PaygateURLs.check_order_status
    return_part_url = CS['paygateAddress'] + PaygateURLs.refund_part
    checkstatus = await request_to_paygate(checkstatus_url, 'POST', data_for_checkstatus)

    # print('| chekstatus response -> ', checkstatus)

    if checkstatus['orderStatus'] == 'cancelled':
        msg = 'Этот заказ уже был отменён'
        to_log = msg + f'\nОтвет с платежного шлюза: {checkstatus}'
        raise CashboxException(data=msg, to_logging=to_log)

    valid_sum = checkstatus['confirmedSum']

    _wares = []
    total_wares_sum = 0

    for ware in data['wares']:
        total_wares_sum += ware['priceDiscount'] * ware['quantity']
        _wares.append({
            'name': ware['name'],
            'price': ware['priceDiscount'],
            'priceDiscount': ware['priceDiscount'],
            'barcode': ware['barcode'],
            'tax_number': ware['tax_number'],
            'quantity': ware['quantity'],
            'discount': 0,
            'posNumber': ware['posNumber']
        })
    total_wares_sum = round_half_down(total_wares_sum, 2)

    # print('total wares sum ', total_wares_sum, 'valid sum ', valid_sum)
    if total_wares_sum > valid_sum:
        msg = 'Сумма переданых товаров превышает оставшуюся сумму заказа!'
        to_log = msg + f'\nСумма товаров: {total_wares_sum} \nСумма заказа в paygate: {valid_sum}'
        raise CashboxException(data=msg, to_logging=to_log)

    to_kkt = {
        'total_wares_sum': total_wares_sum,
        'cashier_name': data['cashier_name'],
        'payment_type': data['payment_type'],
        'document_type': doc_type,
        'amount_entered': data['total_price_with_discount'],
        'pay_link': data['payment_link'],
        'wares': _wares
    }

    result = KKTDevice.handle_order(**to_kkt)

    # pp('formatted info!!!')
    # pp(result)

    to_paygate = {
        'clientOrderID': order_id,
        'proj': cashbox.project_number,
        'wares': _wares,
        'checkNumber': int(result['check_number']),
        'cashID': kkt_info['fn_number'],
        'refundAmount': result['transaction_sum']
    }

    try:
        content = await request_to_paygate(return_part_url, 'POST', to_paygate)
    except CashboxException as exc:
        to_kkt['document_type'] = DocumentTypes.PAYMENT.value
        # TODO: Что-нибудь придумать с этим кейсом. Пока что это не работает должным образом
        KKTDevice.handle_order(**to_kkt)
        raise CashboxException(data=exc.data['errors'], to_logging=exc.data)

    # print('| refund_part response -> ', content)

    return {'actual_order_price': content.get('confirmedSum', 0)}


def _build_wares(wares):
    _wares = []
    copied_wares = deepcopy(wares)
    for pos, ware in enumerate(copied_wares, 1):
        # tax_rate = get_cashbox_tax_from_fiscal_tax(int(ware['tax_number']))
        tax_rate = int(ware['tax_rate'])
        divi = float(f'{1}.{tax_rate // 10}')
        multi = tax_rate / 100
        price = ware.get('discountedPrice') or ware['price']
        price_for_all = round_half_down(price * ware['quantity'], 2)

        tax_sum = round_half_up(price_for_all / divi * multi, 2)

        ware.update({
            'posNumber': pos,
            'priceDiscount': price,
            'taxRate': tax_rate,
            'taxSum': tax_sum,
            'tax_number': get_fiscal_tax_from_cashbox_tax(tax_rate),
            'amount': price_for_all,
            'department': CS['department']
        })
        _wares.append(ware)

    return _wares


async def print_to_secondary_printer(data):
    if not bool(CS['printerForOrder']):
        return

    strs = []
    str1 = f'Заказ: {data["pref"]}{data["num"]}'
    strs.append(str1)

    for ware in data['wares']:
        _str = f'{ware["name"]}. Кол-во: {ware["quantity"]}'
        strs.append(_str)
    await make_request(CS['printerForOrder'], 'POST', {'data': strs}, do_raise=False)
