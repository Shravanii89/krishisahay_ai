import unittest
from app import create_app
from app.models import db, User, Scheme
from app.services.eligibility import calculate_eligibility, get_recommendations

class TestEligibilityEngine(unittest.TestCase):
    
    def setUp(self):
        # Create Flask app and configure test mode
        self.app = create_app()
        self.app.config['TESTING'] = True
        # In-memory database for speed and isolation
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Build tables
        db.create_all()
        
        # Insert mock schemes
        self.scheme_pankisan = Scheme(
            name="PM-KISAN",
            description="Income support.",
            category="Financial",
            state_specific="All",
            min_age=18,
            max_land_size=2.0,
            max_income=None,
            required_crops=None,
            benefits="₹6,000 yearly",
            required_documents="Aadhaar",
            application_steps="Step 1",
            official_link="http://example.com"
        )
        self.scheme_cropins = Scheme(
            name="PMFBY",
            description="Crop insurance.",
            category="Insurance",
            state_specific="All",
            min_age=18,
            max_land_size=None,
            max_income=None,
            required_crops="Wheat, Rice",
            benefits="Subsidized premium",
            required_documents="Aadhaar",
            application_steps="Step 1",
            official_link="http://example.com"
        )
        self.scheme_state = Scheme(
            name="State Scheme",
            description="Maharashtra only.",
            category="Financial",
            state_specific="Maharashtra",
            min_age=18,
            max_land_size=1.0,
            max_income=100000.0,
            required_crops=None,
            benefits="₹10,000",
            required_documents="7/12",
            application_steps="Step 1",
            official_link="http://example.com"
        )
        
        db.session.add(self.scheme_pankisan)
        db.session.add(self.scheme_cropins)
        db.session.add(self.scheme_state)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_eligible_farmer_pm_kisan(self):
        # Farmer fits all criteria: age >= 18, land_size <= 2.0
        farmer = User(
            username="1111111111",
            full_name="Valid Farmer",
            age=30,
            mobile_number="1111111111",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=1.5,
            crop_type="Wheat",
            annual_income=80000.0
        )
        
        result = calculate_eligibility(farmer, self.scheme_pankisan)
        self.assertTrue(result['is_eligible'])
        self.assertEqual(result['score'], 100)
        self.assertEqual(len(result['gaps']), 0)

    def test_ineligible_land_size_pm_kisan(self):
        # Farmer exceeds land limit of 2.0 hectares
        farmer = User(
            username="2222222222",
            full_name="Rich Farmer",
            age=35,
            mobile_number="2222222222",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=3.5,
            crop_type="Wheat",
            annual_income=250000.0
        )
        
        result = calculate_eligibility(farmer, self.scheme_pankisan)
        self.assertFalse(result['is_eligible'])
        self.assertIn("land size less than or equal to 2.0 hectares", result['gaps'][0].lower())

    def test_crop_matching_pmfby(self):
        # Farmer growing Cotton - not in required crops (Wheat, Rice)
        farmer_cotton = User(
            username="3333333333",
            full_name="Cotton Farmer",
            age=40,
            mobile_number="3333333333",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=1.5,
            crop_type="Cotton",
            annual_income=80000.0
        )
        
        result = calculate_eligibility(farmer_cotton, self.scheme_cropins)
        self.assertFalse(result['is_eligible'])
        self.assertIn("grow: cotton", result['gaps'][0].lower())

        # Farmer growing Rice - matches
        farmer_rice = User(
            username="4444444444",
            full_name="Rice Farmer",
            age=40,
            mobile_number="4444444444",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=1.5,
            crop_type="Rice, Sugar cane",
            annual_income=80000.0
        )
        result_rice = calculate_eligibility(farmer_rice, self.scheme_cropins)
        self.assertTrue(result_rice['is_eligible'])

    def test_state_specific_and_income_matching(self):
        # Farmer not in Maharashtra
        farmer_up = User(
            username="5555555555",
            full_name="UP Farmer",
            age=25,
            mobile_number="5555555555",
            state="Uttar Pradesh",
            district="Varanasi",
            village="Sarnath",
            land_size=0.5,
            crop_type="Wheat",
            annual_income=50000.0
        )
        
        result = calculate_eligibility(farmer_up, self.scheme_state)
        self.assertFalse(result['is_eligible'])
        self.assertIn("only for farmers in maharashtra", result['gaps'][0].lower())

        # Farmer in Maharashtra but income too high (120,000 > 100,000)
        farmer_high_income = User(
            username="6666666666",
            full_name="Rich MH Farmer",
            age=25,
            mobile_number="6666666666",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=0.5,
            crop_type="Wheat",
            annual_income=120000.0
        )
        result_income = calculate_eligibility(farmer_high_income, self.scheme_state)
        self.assertFalse(result_income['is_eligible'])
        self.assertIn("annual income less than or equal to", result_income['gaps'][0].lower())

if __name__ == '__main__':
    unittest.main()
