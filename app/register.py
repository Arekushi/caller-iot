import bluetooth
from machine import deepsleep, Timer

from app.utils.date_utils import get_current_datetime_iso
from app.utils.str_utils import clean_ble_message
from app.utils.http_utils import bearer_token_header
from app.http.httpclient import HttpClient
from app.ble.bluetooth import BLESimplePeripheral
from app.secrets import api_config


class Register():
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.p = BLESimplePeripheral(self.ble)
        self.students = dict()
        self.http = HttpClient()
        self.timer = Timer(-1)
        self.register_url = '{}/attendance/register'.format(api_config['url'])
        self.next_subject_url = '{}/subject/next-subject'.format(api_config['url'])

    def checkup(self):
        response = self.http.get(
            self.next_subject_url,
            headers=bearer_token_header()
        ).json()

        time_ms_next = response['time_ms_next_subject']
        time_ms_end = response['time_ms_end_class']

        if time_ms_next > 0:
            self.sleep(time_ms_next)
        else:
            self.startup(time_ms_end)

    def startup(self, time_ms_end):
        print('Iniciando o registro de ocorrências de presença...')
        self.p.advertise()
        self.p.on_write(self.register_occurrence_attendance)
        self.timer.init(
            period=time_ms_end,
            mode=Timer.ONE_SHOT,
            callback=lambda timer: self.send_to_api()
        )

    @staticmethod
    def sleep(time_ms):
        print('Aguardando por {} ms até a próxima aula...'.format(time_ms))
        deepsleep(time_ms)

    def send_to_api(self):
        print('Aula acabou, enviando informações para a API...')

        self.http.post(
            self.register_url,
            json=self.generate_body(),
            headers=bearer_token_header()
        )

        self.reset()
        self.checkup()

    def reset(self):
        self.p.stop_advertise()
        self.students.clear()
        self.timer = Timer(-1)

    def generate_body(self):
        return [{
            'ra': int(ra),
            'attendances': data['attendances']
        } for ra, data in self.students.items()]

    def register_occurrence_attendance(self, value):
        ra = clean_ble_message(value)

        attendance = {
            'created_at': get_current_datetime_iso()
        }

        if ra in self.students:
            self.students[ra]['attendances'].append(attendance)
        else:
            self.students[ra] = {
                'attendances': [attendance]
            }

        print(self.students)
