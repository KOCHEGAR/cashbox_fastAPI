from pprint import pprint as pp
# from comtypes import *
# from comtypes.client import CreateObject, GetModule
# from comtypes.gen._445B09C3_EF00_47B4_9DB0_68DDD7AA9FF1_0_1_0 import FPSpark, IFPSpark
# from comtypes.gen._CF921C08_02B9_415D_84C9_BA2ACE7C20AF_0_1_0 import \
#     SAPacketObj, ISAPacketObj, PCPOSTConnectorObj, IPCPOSTConnectorObj

# import arcus2
#
#
import cashbox as c

print_strings = "\n\n\n--------------------------------------------\n" \
              "(font-style=BIG_BOLD)НОМЕР ЗАКАЗА: \n(font-style=BIG_BOLD)999\n" \
              "--------------------------------------------\n\n"

wares = [
    {'name': 'test!',
     'barcode': '123456',
     'quantity': 1,
     'price': 10.99,
     'tax_number': 0,
     'discount': 0},
{'name': 'test!!',
     'barcode': '123456',
     'quantity': 1,
     'price': 10.89,
     'tax_number': 0,
     'discount': 0}
]

c.open_port('COM3', 57600)

res = c.new_transaction('test', 0, 3, wares)
pp(res)

c.close_port()

exit()

# info = arcus2.purchase(123)
# pp(dir(arcus2))


# pp(arcus2.cancel_last())
# pp(arcus2.cancel_by_link(123, '23117317'))
# pp(arcus2.cancel_by_link(123, '23117317'))
# pp(arcus2.close_shift())
# arcus = cdll.LoadLibrary(r"C:\Arcus2\DLL\arccom.dll")

obj = CreateObject(FPSpark, None, None, IFPSpark)
# obj = CreateObject(dll.FPSpark, None, None, dll.IFPSpark)
#
# pp(dir(obj))
# exit()



# pp(arcus.CreateITPos)
# sap = CreateObject(SAPacketObj, None, None, ISAPacketObj)
# pos = CreateObject(PCPOSTConnectorObj)


# pos_obj = arcus.CreateITPos()
# s = c_char_p(b'678')
#
#
# arcus.ITPosSet(pos_obj, 'currency', byref(s), -1)
# arcus.ITPosSet(pos_obj, 'amount', byref(s), -1)
# #
# a = arcus.ITPosRun(pos_obj, 1)
#
# arcus.ITPosClear(pos_obj)
# arcus.DeleteITPos(pos_obj)
#
# pp('run command')
# pp(a)

print('error code InitDevice -> ', obj.InitDevice())
print('extended code InitDevice -> ', obj.GetExtendedErrorCode())

# pp(obj.OpenShift2(67, '12345', 'Mesto reschetov 4'))
# pp(obj.OpenShift(67, '12345'))
# print('extended code OpenShift -> ', obj.GetExtendedErrorCode())



# pp(obj.Item2(6, 1234, 'Baltika 2077', 18, 8, 1))
# pp(obj.GetExtendedErrorCode())

# print('header ', obj.SetOrderHeader(6, 'Hello', 4))
# pp(obj.Item2(6, 1234, 'Baltika 2077', 1, 8, 8))

# info = arcus2.purchase(123)
# info = arcus2.cancel_by_link(123, '23117552')
# pp(info)
# obj.RegCashier('12345')
# print('extended code RegCashier -> ', obj.GetExtendedErrorCode())
# pp(obj.StartFreeDoc())
# for i in info['cheque'].split('\r'):
#     obj.PrintText(0, i)
# pp(obj.EndFreeDoc())

print('error code CloseShift ->', obj.CloseShift())
print('extended code CloseShift -> ', obj.GetExtendedErrorCode())

print('error code SetCashier -> ', obj.SetCashier('16', '99988', 'Mr.Printer'))
print('extended code SetCashier -> ', obj.GetExtendedErrorCode())


print('error code OpenShift -> ', obj.OpenShift(43, '99988'))
print('extended code OpenShift -> ', obj.GetExtendedErrorCode())

print('error code RegCashier -> ', obj.RegCashier('99988'))
print('extended code RegCashier -> ', obj.GetExtendedErrorCode())


print('error code CashIn -> ', obj.CashIn(8, '1234'))
print('extended code CashIn -> ', obj.GetExtendedErrorCode())


print('error code DeinitDevice -> ', obj.DeinitDevice())
print('extended code DeinitDevice -> ', obj.GetExtendedErrorCode())

############
############
exit()
############
############

# obj.StartFreeDoc()
# print('extended code StartFreeDoc -> ', obj.GetExtendedErrorCode())
#
obj.RegCashier('12345')
print('extended code RegCashier -> ', obj.GetExtendedErrorCode())

obj.StartDocSB(1)
print('extended code StartDocSB -> ', obj.GetExtendedErrorCode())
# obj.PrintText(1, '==============')
obj.Item(2000, 134, 'Baltika 2077', 2)
print('extended code Item -> ', obj.GetExtendedErrorCode())

obj.AddPay(8, str(999))
print('extended code AddPay -> ', obj.GetExtendedErrorCode())

# obj.Item2(6, 1234, 'Baltika 2077', 18, 8, 2)
# print('extended code Item2 -> ', obj.GetExtendedErrorCode())
for i in range(0, 49):
    print(i, '-> ', obj.GetTextDeviceInfo(i))
obj.EndDocSB()
print('extend ed code EndDocSB -> ', obj.GetExtendedErrorCode())

# print('_'*33)
# print(obj.GetTextDeviceInfo(4),
# obj.GetTextDeviceInfo(6),
# obj.GetTextDeviceInfo(5),
# obj.GetTextDeviceInfo(7),
# obj.GetTextDeviceInfo(8),
# obj.GetTextDeviceInfo(11),
# obj.GetTextDeviceInfo(12),
# obj.GetTextDeviceInfo(14),
# obj.GetTextDeviceInfo(28))
# obj.EndFreeDoc()
# print('extended code EndFreeDoc -> ', obj.GetExtendedErrorCode())

# print(obj.DeinitDevice())
# print('extended code DeinitDevice -> ', obj.GetExtendedErrorCode())


"""
    Некоторые значения вызова функций
    
    obj.GetTextDeviceInfo(4) - дата и время вида '29-02-20 16:45:45'
    obj.GetTextDeviceInfo(6) - РН ККТ (регистрационный номер?)
    obj.GetTextDeviceInfo(5) - № фискалька (заводской номер?)
    obj.GetTextDeviceInfo(7) - ИНН
    obj.GetTextDeviceInfo(8) - Номер смены
    obj.GetTextDeviceInfo(11) - Время открытия смены
    obj.GetTextDeviceInfo(12) - Номер последнего документа
    obj.GetTextDeviceInfo(14) - Номер ФН
    
    obj.GetTextDeviceInfo(29) - Количество приходов в смене
    obj.GetTextDeviceInfo(30) - Сумма приходов в смене
    obj.GetTextDeviceInfo(31) - (Предположительно) Количество возвратов приходов в текущей смене
    obj.GetTextDeviceInfo(32) - (Предположительно) Сумма возвратов приходов в текущей смене
    obj.GetTextDeviceInfo(38) - Какая-то херня
    obj.GetTextDeviceInfo(39) - Какая-то херня
    
    
    obj.GetTextDeviceInfo(28) - Похоже на количество денег в ящике
"""
