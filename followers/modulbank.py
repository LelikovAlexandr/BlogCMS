import base64
import hashlib


def get_raw_signature(params):
    chunks = []

    for key in sorted(params.keys()):
        if key == 'signature':
            continue

        value = params[key]

        if isinstance(value, str):
            value = value.encode('utf8')
        else:
            value = str(value).encode('utf-8')

        if not value:
            continue

        value_encoded = base64.b64encode(value)
        chunks.append('%s=%s' % (key, value_encoded.decode()))

    raw_signature = '&'.join(chunks)
    return raw_signature


'''Двойное шифрование sha1 на основе секретного ключа'''


def double_sha1(secret_key, data):
    sha1_hex = lambda s: hashlib.sha1(s.encode('utf-8')).hexdigest()
    digest = sha1_hex(secret_key + sha1_hex(secret_key + data))
    return digest


'''Вычисляем подпись (signature). Подпись считается на основе склеенной строки из отсортированного массива параметров, исключая из расчета пустые поля и элемент "signature" '''


def get_signature(secret_key: str, params: dict) -> str:
    return double_sha1(secret_key, get_raw_signature(params))


'''Определяем словарь с параметрами для расчета.
В этот массив должны войти все параметры, отправляемые в вашей форме (за исключением самого поля signature, значение которого вычисляем).
Получив вашу форму, система ИЭ аналогичным образом вычислит из ее параметров signature и сравнит значение с вычисленным на стороне вашего магазина. 
подставьте ваш секретный ключ вместо 00112233445566778899aabbccddeeff
'''
if __name__ == '__main__':
    items = {
        'transaction_id': 'jH47RKzgpGNtuG20bek3pX',
        'amount': '436.00',
        'original_amount': '436.00',
        'order_id': '46088093',
        'state': 'COMPLETE',
        'testing': '1',
        'pan_mask': '404730******7550',
        'client_email': 'ishchukin@example.com',
        'client_phone': '+7 760 668 6570',
        'client_name': 'Васильев Эрнст Якубович',
        'payment_method': 'card',
        'created_datetime': '2020-04-14 19:15:12',
        'currency': 'RUB',
        'meta': '{"example-property": 1234}',
        'merchant': 'd1ef3dd3-9535-4e80-a7ee-28887670b471',
        'salt': 'BFD2759553F48F90367A70E865FF80B7',
        'unix_timestamp': '1586891718',
    }
    print('dea2969264bebae7893e64ace5583515b5aae506' == get_signature(
        'ACEEBA48E2F4DFE28E72478DFF53ABCB', items))
