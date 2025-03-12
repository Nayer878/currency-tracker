import unittest
from unittest.mock import patch, MagicMock
from projet2 import setup_google_sheets, get_exchange_rates, update_sheet

class TestProjet2(unittest.TestCase):

    @patch('projet2.ServiceAccountCredentials.from_json_keyfile_name')
    @patch('projet2.gspread.authorize')
    def test_setup_google_sheets(self, mock_authorize, mock_creds):
        mock_creds.return_value = 'credentials'
        mock_authorize.return_value = 'client'
        
        client = setup_google_sheets()
        self.assertEqual(client, 'client')

    @patch('projet2.requests.get')
    def test_get_exchange_rates(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "rates": {"EUR": 0.85, "GBP": 0.75},
            "time_last_updated": 1234567890
        }
        mock_get.return_value = mock_response
        
        rates, timestamp = get_exchange_rates()
        self.assertEqual(rates, {"EUR": 0.85, "GBP": 0.75})
        self.assertEqual(timestamp, 1234567890)

    @patch('projet2.gspread.Worksheet')
    def test_update_sheet(self, mock_sheet):
        rates = {"EUR": 0.85, "GBP": 0.75}
        timestamp = 1234567890
        
        result = update_sheet(mock_sheet, rates, timestamp)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
