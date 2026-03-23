import unittest
import pandas as pd
from src.data_loader import clean_text, load_and_preprocess_data

class TestDataLoader(unittest.TestCase):
    def test_clean_text(self):
        # Test 1: URL removal
        self.assertEqual(clean_text("Check http://google.com"), "check URL")
        
        # Test 2: User mention removal
        self.assertEqual(clean_text("Hello @suren"), "hello USER")
        
        # Test 3: Tamil preservation
        tamil_text = "நீ உயிரோட இருக்க கூடாது"
        # cleaning lowercases and strips, but should keep tamil chars
        self.assertEqual(clean_text(tamil_text), tamil_text) 
        
        # Test 4: Mixed
        mixed = "Super video da @bro http://link.com"
        self.assertEqual(clean_text(mixed), "super video da USER URL")

    def test_load_real_data(self):
        # This tests if we can actually read the files without encoding errors
        try:
            df = load_and_preprocess_data(".")
            print(f"\nLoaded {len(df)} rows.")
            self.assertGreater(len(df), 0)
            self.assertIn("cleaned_text", df.columns)
            self.assertIn("label", df.columns)
            
            # Check for non-null
            self.assertFalse(df["cleaned_text"].isnull().any())
            
            # Check if Tamil characters exist in the dataframe
            # A simple heuristic: check if any character in any string is in Tamil unicode block
            # Tamil block is roughly 0B80–0BFF
            has_tamil = False
            for text in df["cleaned_text"].head(100):
                if any('\u0B80' <= char <= '\u0BFF' for char in text):
                    has_tamil = True
                    break
            self.assertTrue(has_tamil, "No Tamil characters found in the first 100 rows!")
            
        except Exception as e:
            self.fail(f"Data loading failed: {e}")

if __name__ == '__main__':
    unittest.main()
