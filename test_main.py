import unittest
from unittest.mock import patch, MagicMock
import time
import main
from main import get_greeting, respond_to_skin_tone, suggest_outfits_based_on_body_type, ask_about_body_detection
from voice_utils import speak, listen_for_command

class TestVoiceAssistant(unittest.TestCase):

    @patch('random.choice')
    def test_get_greeting(self, mock_choice):
        mock_choice.return_value = "Hello! Need some assistance getting ready?"
        result = get_greeting()
        self.assertEqual(result, "Hello! Need some assistance getting ready?")

    @patch('voice_utils.speak')
    @patch('time.sleep', return_value=None)  # Mocking time.sleep to avoid delays
    def test_respond_to_skin_tone(self, mock_sleep, mock_speak):
        # Test for Light skin tone
        respond_to_skin_tone("Light")
        mock_speak.assert_any_call("You have a lovely light skin tone.")
        mock_speak.assert_any_call("Soft pastels, cool blues, and pinks will look amazing on you!")

        # Test for Medium skin tone
        respond_to_skin_tone("Medium")
        mock_speak.assert_any_call("Your warm medium skin tone looks fantastic!")
        mock_speak.assert_any_call("Earthy tones like olive, mustard, and rust will complement you well.")

        # Test for Dark skin tone
        respond_to_skin_tone("Dark")
        mock_speak.assert_any_call("You have a beautiful dark skin tone.")
        mock_speak.assert_any_call("Bright colors like royal blue, yellow, and white will really stand out on you!")

        # Test for unknown skin tone
        respond_to_skin_tone("Unknown")
        mock_speak.assert_any_call("Couldn't determine your exact skin tone, but you're always glowing!")

    @patch('voice_utils.speak')
    @patch('time.sleep', return_value=None)
    def test_suggest_outfits_based_on_body_type(self, mock_sleep, mock_speak):
        # Test for Mesomorph body type
        suggest_outfits_based_on_body_type("Mesomorph")
        mock_speak.assert_any_call("Since you have an athletic build, fitted clothing and structured jackets will enhance your silhouette.")

        # Test for Endomorph body type
        suggest_outfits_based_on_body_type("Endomorph")
        mock_speak.assert_any_call("With your curvy build, high-waist pants and wrap dresses can look fabulous on you.")

        # Test for Ectomorph body type
        suggest_outfits_based_on_body_type("Ectomorph")
        mock_speak.assert_any_call("For your lean build, layered clothing and patterns can add volume and look great.")

        # Test for unknown body type
        suggest_outfits_based_on_body_type("Unknown")
        mock_speak.assert_any_call("Based on your structure, I suggest choosing well-fitted outfits that highlight your best features.")

    @patch('voice_utils.speak')
    @patch('voice_utils.listen_for_command')
    def test_ask_about_body_detection(self, mock_listen, mock_speak):
        # Test response for "Yes"
        mock_listen.return_value = "Yes"
        result = ask_about_body_detection()
        self.assertTrue(result)

        # Test response for "No"
        mock_listen.return_value = "No"
        result = ask_about_body_detection()
        self.assertFalse(result)

        # Test invalid responses
        mock_listen.return_value = "Maybe"
        result = ask_about_body_detection()
        self.assertFalse(result)

    @patch('voice_utils.speak')
    @patch('voice_utils.listen_for_command')
    @patch('actions.real_time_camera.start_real_time_analysis', return_value="Light")
    @patch('actions.body_structure_analysis.start_body_structure_detection', return_value="Mesomorph")
    @patch('actions.outfit_suggestion.suggest_outfit_based_on_body_and_skin_tone', return_value="A lovely blue jacket")
    def test_main_flow(self, mock_outfit, mock_body_structure, mock_camera, mock_listen, mock_speak):
        # Simulate user saying "Yes"
        mock_listen.return_value = "Yes"
        with patch('builtins.print') as mock_print:
            main.main()  # Call main.main() explicitly
            mock_speak.assert_any_call("Great! Let's get started.")
            mock_speak.assert_any_call("Opening camera for real-time analysis...")

        # Simulate user asking for camera analysis and body detection
        mock_listen.return_value = "Open the camera"
        mock_speak.assert_any_call("Opening camera for real-time analysis...")
        mock_speak.assert_any_call("Analyzing body structure...")

        # Simulate user selecting "Yes" for outfit selection
        mock_listen.return_value = "Yes"
        mock_outfit.assert_called_with("Mesomorph", "Light")
        mock_speak.assert_any_call("A lovely blue jacket")

    @patch('voice_utils.speak')
    @patch('voice_utils.listen_for_command')
    def test_invalid_user_responses_in_main(self, mock_listen, mock_speak):
        # Test for invalid "Yes"/"No" responses from the user
        mock_listen.return_value = "Maybe"
        with patch('builtins.print') as mock_print:
            main.main()
            mock_speak.assert_any_call("Please say 'Yes' or 'No'.")

        # Test for repeated invalid responses
        mock_listen.return_value = ""
        with patch('builtins.print') as mock_print:
            main.main()
            mock_speak.assert_any_call("Didn't catch that. Please speak clearly.")

if __name__ == '__main__':
    unittest.main()
