"""
RUN ALL TESTS - UFC Project
Copy this entire code into a file called "run_all_tests.py" and run it.
No pytest installation required - uses Python's built-in unittest!
"""

import pandas as pd
import numpy as np
from scipy import stats
import unittest
from pathlib import Path

# ============================================================
# CONFIGURATION - Change this if your Excel file is elsewhere
# ============================================================
DATA_PATH = Path(__file__).parent / "UFC_FINAL_DATASET.xlsx"
# If the above doesn't work, uncomment and use full path:
# DATA_PATH = Path(r"C:\Users\YourName\UFC\UFC_FINAL_DATASET.xlsx")


# ============================================================
# TEST CLASS 1: DATA QUALITY TESTS
# ============================================================
class TestDataQuality(unittest.TestCase):
    """Test data quality and integrity"""
    
    @classmethod
    def setUpClass(cls):
        """Load data once before all tests"""
        if not DATA_PATH.exists():
            cls.skipTest(cls, f"File not found: {DATA_PATH}")
        cls.df = pd.read_excel(DATA_PATH)
    
    def test_1_file_exists(self):
        """File exists"""
        self.assertTrue(DATA_PATH.exists(), f"File not found: {DATA_PATH}")
    
    def test_2_no_empty_rows(self):
        """No completely empty rows"""
        self.assertFalse(self.df.isnull().all(axis=1).any(), "Found empty rows!")
    
    def test_3_no_null_in_critical_columns(self):
        """Critical columns have no nulls"""
        critical_cols = ['Fighter', 'Win Rate', 'Stance', 'Handedness']
        missing = self.df[critical_cols].isnull().sum()
        self.assertEqual(missing.sum(), 0, f"Nulls found in: {missing[missing > 0]}")
    
    def test_4_win_rate_range(self):
        """Win rate between 0 and 100"""
        win_rates = self.df['Win Rate'].dropna()
        self.assertTrue(win_rates.between(0, 100).all(), "Win rate outside 0-100%!")
    
    def test_5_valid_stance(self):
        """Stance must be Orthodox or Southpaw"""
        valid = ['Orthodox', 'Southpaw']
        invalid = self.df[~self.df['Stance'].isin(valid)]
        self.assertEqual(len(invalid), 0, f"Invalid stance: {invalid['Stance'].unique()}")
    
    def test_6_valid_handedness(self):
        """Handedness must be Right or Left"""
        valid = ['Right', 'Left']
        invalid = self.df[~self.df['Handedness'].isin(valid)]
        self.assertEqual(len(invalid), 0, f"Invalid handedness: {invalid['Handedness'].unique()}")
    
    def test_7_no_duplicate_fighters(self):
        """No duplicate fighter names"""
        dupes = self.df[self.df.duplicated(subset=['Fighter'], keep=False)]
        self.assertEqual(len(dupes), 0, f"Duplicate fighters: {dupes['Fighter'].tolist()}")
    
    def test_8_reach_positive(self):
        """Reach must be positive"""
        if 'Reach' in self.df.columns:
            self.assertTrue((self.df['Reach'].dropna() > 0).all(), "Reach <= 0 found!")
    
    def test_9_height_positive(self):
        """Height must be positive"""
        if 'Height' in self.df.columns:
            self.assertTrue((self.df['Height'].dropna() > 0).all(), "Height <= 0 found!")
    
    def test_10_win_rate_numeric(self):
        """Win Rate must be numeric"""
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['Win Rate']), "Win Rate not numeric!")


# ============================================================
# TEST CLASS 2: STATISTICS TESTS (matches README claims)
# ============================================================
class TestStatistics(unittest.TestCase):
    """Verify statistical results match README"""
    
    @classmethod
    def setUpClass(cls):
        if not DATA_PATH.exists():
            cls.skipTest(cls, f"File not found: {DATA_PATH}")
        cls.df = pd.read_excel(DATA_PATH)
    
    def test_11_southpaw_count(self):
        """Southpaw count = 24"""
        count = len(self.df[self.df['Stance'] == 'Southpaw'])
        self.assertEqual(count, 24, f"Southpaw: {count}, expected 24")
    
    def test_12_orthodox_count(self):
        """Orthodox count = 93"""
        count = len(self.df[self.df['Stance'] == 'Orthodox'])
        self.assertEqual(count, 93, f"Orthodox: {count}, expected 93")
    
    def test_13_total_fighters(self):
        """Total fighters = 117"""
        self.assertEqual(len(self.df), 117, f"Total: {len(self.df)}, expected 117")
    
    def test_14_southpaw_right_count(self):
        """Southpaw + Right-handed = 23"""
        count = len(self.df[(self.df['Stance'] == 'Southpaw') & (self.df['Handedness'] == 'Right')])
        self.assertEqual(count, 23, f"Southpaw+Right: {count}, expected 23")
    
    def test_15_southpaw_win_rate(self):
        """Southpaw mean win rate ~ 73.8%"""
        wr = self.df[self.df['Stance'] == 'Southpaw']['Win Rate'].mean()
        self.assertAlmostEqual(wr, 73.8, delta=0.5, msg=f"Southpaw WR: {wr:.1f}%, expected ~73.8%")
    
    def test_16_orthodox_win_rate(self):
        """Orthodox mean win rate ~ 72.1%"""
        wr = self.df[self.df['Stance'] == 'Orthodox']['Win Rate'].mean()
        self.assertAlmostEqual(wr, 72.1, delta=0.5, msg=f"Orthodox WR: {wr:.1f}%, expected ~72.1%")
    
    def test_17_southpaw_right_win_rate(self):
        """Southpaw+Right mean win rate ~ 74.3%"""
        group = self.df[(self.df['Stance'] == 'Southpaw') & (self.df['Handedness'] == 'Right')]
        wr = group['Win Rate'].mean()
        self.assertAlmostEqual(wr, 74.3, delta=1.0, msg=f"Southpaw+Right WR: {wr:.1f}%, expected ~74.3%")
    
    def test_18_t_test_p_value(self):
        """T-test p-value between Orthodox and Southpaw ~ 0.34"""
        orthodox = self.df[self.df['Stance'] == 'Orthodox']['Win Rate'].dropna()
        southpaw = self.df[self.df['Stance'] == 'Southpaw']['Win Rate'].dropna()
        t_stat, p_val = stats.ttest_ind(orthodox, southpaw)
        self.assertGreater(p_val, 0.30, f"p-value too low: {p_val:.3f}")
        self.assertLess(p_val, 0.40, f"p-value too high: {p_val:.3f}")
    
    def test_19_t_test_t_statistic(self):
        """T-statistic ~ 0.96"""
        orthodox = self.df[self.df['Stance'] == 'Orthodox']['Win Rate'].dropna()
        southpaw = self.df[self.df['Stance'] == 'Southpaw']['Win Rate'].dropna()
        t_stat, _ = stats.ttest_ind(orthodox, southpaw)
        self.assertGreater(t_stat, 0.90, f"T-stat too low: {t_stat:.3f}")
        self.assertLess(t_stat, 1.00, f"T-stat too high: {t_stat:.3f}")
    
    def test_20_cohens_d(self):
        """Cohen's d ~ 0.21 (small effect)"""
        orthodox = self.df[self.df['Stance'] == 'Orthodox']['Win Rate'].dropna()
        southpaw = self.df[self.df['Stance'] == 'Southpaw']['Win Rate'].dropna()
        
        n1, n2 = len(orthodox), len(southpaw)
        var1, var2 = orthodox.var(), southpaw.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        cohens_d = abs((orthodox.mean() - southpaw.mean()) / pooled_std)
        
        self.assertGreater(cohens_d, 0.15, f"Cohen's d too low: {cohens_d:.3f}")
        self.assertLess(cohens_d, 0.30, f"Cohen's d too high: {cohens_d:.3f}")


# ============================================================
# TEST CLASS 3: RECOMMENDER TESTS
# ============================================================
class TestRecommender(unittest.TestCase):
    """Test fighter recommender data requirements"""
    
    @classmethod
    def setUpClass(cls):
        if not DATA_PATH.exists():
            cls.skipTest(cls, f"File not found: {DATA_PATH}")
        cls.df = pd.read_excel(DATA_PATH)
    
    def test_21_required_columns_exist(self):
        """All required columns exist"""
        required = ['Fighter', 'Win Rate', 'Stance', 'Handedness']
        missing = [col for col in required if col not in self.df.columns]
        self.assertEqual(len(missing), 0, f"Missing columns: {missing}")
    
    def test_22_fighter_names_unique(self):
        """Fighter names are unique"""
        self.assertTrue(self.df['Fighter'].is_unique, "Duplicate fighter names!")
    
    def test_23_no_nan_fighter_names(self):
        """No NaN fighter names"""
        self.assertFalse(self.df['Fighter'].isna().any(), "NaN fighter names found!")


# ============================================================
# RUN ALL TESTS
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("UFC PROJECT - RUNNING ALL TESTS")
    print("="*60)
    print(f"Data file: {DATA_PATH}")
    print(f"File exists: {DATA_PATH.exists()}")
    print("="*60 + "\n")
    
    # Create test suite with all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommender))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED! Data is clean and matches README!")
    else:
        print("\n❌ SOME TESTS FAILED! Check the output above.")
    
    print("="*60)
