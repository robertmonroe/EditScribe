
import unittest
from unittest.mock import MagicMock
from agents.acquisitions_editor import AcquisitionsEditor
from core.style_sheet import StyleSheet

class TestSynopsisCleaning(unittest.TestCase):
    def test_thinking_tag_removal(self):
        # Mock LLM Client
        mock_llm = MagicMock()
        
        # Simulate LLM output with thinking tags
        dirty_output = """<thinking>
I need to write a synopsis.
Here is my plan...
</thinking>
# PROFESSIONAL SYNOPSIS
## The Book
**Genre:** Thriller
---
### Overview
This is the actual content."""

        # Mock generate method to return dirty output
        # Note: We need to mock the generate method of the *instance* or the class
        # Since AcquisitionsEditor inherits from Agent, and Agent calls self.llm_client.generate
        # But AcquisitionsEditor.generate is likely a wrapper or inherited.
        # Let's look at AcquisitionsEditor code. It calls self.generate.
        # We can mock the generate method on the instance.
        
        editor = AcquisitionsEditor(mock_llm)
        editor.generate = MagicMock(return_value=dirty_output)
        
        # Dummy data
        style_sheet = StyleSheet(manuscript_id="test_id", title="Test Book", genre="Thriller", word_count=50000)
        text = "Some manuscript text..."
        
        # Run the method
        clean_synopsis = editor._generate_professional_synopsis(text, style_sheet)
        
        # Verify
        print(f"Original: {dirty_output[:50]}...")
        print(f"Cleaned:  {clean_synopsis[:50]}...")
        
        self.assertNotIn("<thinking>", clean_synopsis)
        self.assertNotIn("</thinking>", clean_synopsis)
        self.assertIn("# PROFESSIONAL SYNOPSIS", clean_synopsis)
        self.assertTrue(clean_synopsis.startswith("# PROFESSIONAL SYNOPSIS"))

    def test_truncated_thinking_tag_removal(self):
        # Mock LLM Client
        mock_llm = MagicMock()
        
        # Simulate LLM output with TRUNCATED thinking tags (no closing tag)
        # This happens if the model runs out of tokens while "thinking"
        # But wait, if it runs out of tokens while thinking, we get NO synopsis.
        # So the regex mainly helps if it finishes thinking but leaves the tag?
        # Or if it outputs <thinking>... content ... (and maybe no closing tag if it's weird)
        # Actually, if it truncates inside thinking, we get nothing useful.
        # But let's test the regex robustness anyway.
        
        dirty_output = """<thinking>
I am thinking forever...
"""
        editor = AcquisitionsEditor(mock_llm)
        editor.generate = MagicMock(return_value=dirty_output)
        
        style_sheet = StyleSheet(manuscript_id="test_id", title="Test Book", genre="Thriller", word_count=50000)
        text = "Some manuscript text..."
        
        clean_synopsis = editor._generate_professional_synopsis(text, style_sheet)
        
        print(f"Truncated Input: {dirty_output}")
        print(f"Cleaned Output: '{clean_synopsis}'")
        
        self.assertEqual(clean_synopsis, "")

if __name__ == '__main__':
    unittest.main()
