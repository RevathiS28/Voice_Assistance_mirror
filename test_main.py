import unittest
from unittest.mock import patch, MagicMock
import main

class TestMainAssistant(unittest.TestCase):

    @patch("main.sr.Recognizer.recognize_google")
    @patch("main.sr.AudioFile")
    def test_audio_to_text_success(self, mock_audiofile, mock_recognize):
        mock_recognize.return_value = "My name is Ankur and I live in Bangalore"
        mock_audiofile.return_value.__enter__.return_value = MagicMock()
        
        result = main.audio_to_text("dummy.wav")
        self.assertEqual(result, "My name is Ankur and I live in Bangalore")

    @patch("main.requests.get")
    def test_get_weather_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "weather": [{"main": "Clear"}],
            "main": {"temp": 28.5}
        }
        mock_get.return_value = mock_response

        weather = main.get_weather("Bangalore")
        self.assertEqual(weather["weather"], "clear")
        self.assertAlmostEqual(weather["temperature"], 28.5)

    def test_prompt_template_render(self):
        text = "My name is Ankur and I live in Bangalore"
        rendered = main.prompt_template.format(
            text=text
        )
        self.assertIn("My name is Ankur", rendered)

    @patch("main.audio_to_text", return_value="My name is Ankur and I live in Bangalore")
    @patch("main.get_weather", return_value={"weather": "clear", "temperature": 30})
    def test_run_assistant_mocked(self, mock_weather, mock_audio):
        result = main.run_assistant()
        self.assertIn("Ankur", result)
        self.assertIn("clear", result)
        self.assertIn("30", str(result))

if __name__ == '__main__':
    unittest.main()
