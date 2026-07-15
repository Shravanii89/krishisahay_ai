from run import app
from app.models import db, CustomScheme

docs = """Aadhaar Card
7/12 Land Record
Bank Passbook
Passport Size Photo
Mobile Number
Caste Certificate (if applicable)
"""

process = """1. Register on MahaDBT Portal
2. Fill the application form
3. Upload required documents
4. Submit application
5. Verification by Agriculture Department
6. Subsidy released after approval
"""

official = "https://mahadbt.maharashtra.gov.in"

with app.app_context():

    schemes = CustomScheme.query.all()

    for scheme in schemes:
        scheme.required_documents = docs
        scheme.application_process = process
        scheme.official_link = official

    db.session.commit()

print("✅ All schemes updated successfully!")