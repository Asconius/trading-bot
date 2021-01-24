import io
from unittest import TestCase

from parameterized import parameterized

from src import main, db
from src.bo.configuration_bo import ConfigurationBO


class MainTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()
        ConfigurationBO.init()

    @parameterized.expand([
        ('/', 200),
        ('/stock', 200),
        ('/stock/intraday/symbol', 200),
        ('/intraday', 200),
        ('/evaluation', 200),
        ('/forward', 200),
        ('/process', 200),
        ('/process/start/process_name', 200),
        ('/process/stop/process_name', 200),
        ('/import', 200),
        ('/export', 200),
        ('/export/intraday', 200),
        ('/configuration', 200),
        ('/invalid', 404),
    ])
    def test_get(self, path, code):
        main.app.testing = True
        client = main.app.test_client()
        response = client.get(path, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assertEqual(response.status_code, code)

    def test_post_import_intraday(self):
        main.app.testing = True
        client = main.app.test_client()
        data = {'file': (io.BytesIO(b'{}'), 'intraday.json')}
        response = client.post('/import/intraday', environ_base={'REMOTE_ADDR': '127.0.0.1'}, data=data,
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_post_configuration(self):
        main.app.testing = True
        client = main.app.test_client()
        data = {'form_list-0-identifier': 'FORWARD_CASH',
                'form_list-0-description': 'Forward Cash',
                'form_list-0-value': '10000.00',
                'submit': 'Submit'}
        response = client.post('/configuration', environ_base={'REMOTE_ADDR': '127.0.0.1'}, data=data,
                               content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
