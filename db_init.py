import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from app import create_app
from app.models import db, Scheme, User

def initialize_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if schemes already exist to prevent duplicates
        if Scheme.query.count() > 0:
            print("Database already seeded with schemes.")
            return
            
        print("Seeding government schemes...")
        
        schemes = [
            Scheme(
                name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                description="An initiative by the Government of India that provides minimum income support of up to ₹6,000 per year to all landholding farmer families across the country.",
                category="Financial Support",
                target_category="All",
                state_specific="All",
                min_age=18,
                max_land_size=2.0, # Targetted small/marginal land size limit representation
                max_income=None,
                required_crops=None,
                benefits="Direct cash transfer of ₹6,000 per year in three equal installments of ₹2,000 every four months directly into the bank accounts of the farmers.",
                required_documents="Aadhaar Card\nLand Ownership Records (Patta/Khata/7-12)\nBank Passbook / Account details\nActive Mobile Number (Aadhaar linked)",
                application_steps="1. Visit the official website: pmkisan.gov.in\n2. Click on 'New Farmer Registration' on the homepage.\n3. Enter your Aadhaar number, select your State, and submit the Captcha.\n4. Fill in personal details, land survey numbers, and coordinates.\n5. Upload land records PDF and bank details.\n6. Submit and track application status.",
                official_link="https://pmkisan.gov.in"
            ),
            Scheme(
                name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                description="A government-sponsored crop insurance scheme that integrates multiple stakeholders and provides insurance cover against crop failures due to natural calamities.",
                category="Crop Insurance",
                target_category="All",
                state_specific="All",
                min_age=18,
                max_land_size=None,
                max_income=None,
                required_crops="Rice, Wheat, Maize, Cotton, Bajra, Soyabean",
                benefits="Complete financial security for farmers from pre-sowing to post-harvest crop loss. Extremely low premium contributions: 2% for Kharif crops, 1.5% for Rabi, and 5% for commercial/horticultural crops.",
                required_documents="Aadhaar Card\nLand possession certificate / Patta\nSowing Certificate issued by local patwari\nCancelled cheque or Bank Passbook copy",
                application_steps="1. Log on to pmfby.gov.in or visit the nearest bank/common service center.\n2. Register as a farmer and select the insurance provider.\n3. Input crop sowing details, crop variety, and land area.\n4. Pay the required premium (1.5% - 5% of sum insured).\n5. Keep the policy document safe for claim processing.",
                official_link="https://pmfby.gov.in"
            ),
            Scheme(
                name="Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
                description="Focuses on creating micro-irrigation systems under the motto 'Per Drop More Crop' to maximize water efficiency on farms.",
                category="Irrigation",
                target_category="Small/Marginal",
                state_specific="All",
                min_age=18,
                max_land_size=None,
                max_income=None,
                required_crops=None,
                benefits="Financial assistance/subsidy up to 55% for small & marginal farmers, and 45% for other farmers for installing Drip & Sprinkler irrigation systems on their land.",
                required_documents="Aadhaar Card\nLand registry document (7/12 extract)\nElectricity Connection details (for water pump)\nQuotation of the micro-irrigation set from an approved manufacturer",
                application_steps="1. Register on your state's Horticulture/Agriculture DBT portal (e.g. MahaDBT, UP Agriculture).\n2. Apply for Drip Irrigation subsidy.\n3. Fill in water source details and pump specifications.\n4. Upload land records and copy of the dealer quotation.\n5. Upon verification, the department will issue pre-sanction.\n6. Complete installation and get verified for direct subsidy release.",
                official_link="https://pmksy.gov.in"
            ),
            Scheme(
                name="Kisan Credit Card (KCC) Scheme",
                description="Designed to provide farmers with timely access to credit for crop cultivation and meet other short-term agricultural expenses at subsidized rates.",
                category="Financial Support",
                target_category="All",
                state_specific="All",
                min_age=18,
                max_land_size=None,
                max_income=None,
                required_crops=None,
                benefits="Subsidized loans up to ₹3,00,000 at a baseline interest rate of 7%, further reduced to 4% per year upon prompt repayment. Includes free ATM-enabled KCC debit cards.",
                required_documents="Aadhaar Card\nLand details certified by Revenue Authorities (Patta)\nCropping pattern certificate\nDeclaration of no outstanding loans in other banks",
                application_steps="1. Visit the nearest public sector bank, regional rural bank, or cooperative bank.\n2. Ask for the Kisan Credit Card application form.\n3. Submit filled form with land ownership details.\n4. Bank officers will inspect the land coordinates.\n5. Loan limit will be set based on crops grown and scale.\n6. Debit card will be issued within 14 days.",
                official_link="https://www.sbi.co.in/web/personal-banking/loans/agriculture-banking/kisan-credit-card"
            ),
            Scheme(
                name="Maharashtra Baliraja Jal Sanjivani Yojana",
                description="A state-specific scheme in Maharashtra designed to complete stalled irrigation projects in drought-hit regions, helping marginal farmers get water security.",
                category="Irrigation",
                target_category="Small/Marginal",
                state_specific="Maharashtra",
                min_age=18,
                max_land_size=5.0,
                max_income=150000.0,
                required_crops=None,
                benefits="Complete financial grant for water storage structures, farm ponds, and dug-wells construction, prioritizing drought-prone talukas.",
                required_documents="Aadhaar Card\nResidential Proof of Maharashtra\n7/12 and 8A Land extracts\nIncome Certificate showing household annual income <= ₹1.5 Lakhs",
                application_steps="1. Log in to the MahaDBT Portal (mahadbt.maharashtra.gov.in).\n2. Select Agriculture/Irrigation schemes.\n3. Fill details for Farm Pond/Well under Baliraja Jal Sanjivani.\n4. Upload 7/12, Aadhaar, and Income certificate.\n5. Direct subsidy will be sent post physical validation of the constructed water resource.",
                official_link="https://mahadbt.maharashtra.gov.in"
            )
        ]
        
        for s in schemes:
            db.session.add(s)
            
        # Also create a default test farmer for ease of testing
        # Password: password123
        test_farmer = User(
            username="9876543210",
            full_name="Rajesh Kumar",
            farmer_id="FID-10023-R",
            age=45,
            mobile_number="9876543210",
            email="rajesh@example.com",
            state="Maharashtra",
            district="Nagpur",
            village="Ramtek",
            land_size=1.8,
            crop_type="Wheat, Rice, Cotton",
            annual_income=120000.0,
            category="OBC"
        )
        test_farmer.set_password("password123")
        db.session.add(test_farmer)
        
        try:
            db.session.commit()
            print("Database successfully seeded with 5 schemes and 1 test farmer.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding database: {str(e)}")

if __name__ == "__main__":
    initialize_database()
