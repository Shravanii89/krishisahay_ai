from app import create_app
from app.models import db, CustomScheme

app = create_app()

with app.app_context():

    db.session.query(CustomScheme).delete()

    schemes = [

        CustomScheme(
            name="Dairy Farming",
            category="Animal Husbandry",
            project_cost="₹6,00,000",
            subsidy="35% (General), 50% (SC/ST)",
            description="Purchase of 10 cows or buffaloes.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Goat Farming",
            category="Animal Husbandry",
            project_cost="₹4,50,000",
            subsidy="35% (General), 50% (SC/ST)",
            description="50 goats and 2 bucks.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Poultry Farming",
            category="Animal Husbandry",
            project_cost="₹8,00,000",
            subsidy="35% (General), 50% (SC/ST)",
            description="5000 birds.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Shade Net House",
            category="Horticulture",
            project_cost="₹3,50,000",
            subsidy="50%",
            description="10 Guntha Shade Net House.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Polyhouse",
            category="Horticulture",
            project_cost="₹11,00,000",
            subsidy="50%",
            description="10 Guntha Polyhouse.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Mini Dal Mill",
            category="Food Processing",
            project_cost="₹1,88,000",
            subsidy="50%",
            description="Mini Dal Mill setup.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Mini Oil Mill",
            category="Food Processing",
            project_cost="₹5,00,000",
            subsidy="50%",
            description="Mini Oil Mill.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Tractor Purchase",
            category="Farm Equipment",
            project_cost="Varies",
            subsidy="₹75,000 - ₹1,00,000",
            description="Purchase of tractor and implements.",
            eligibility="Depends on farmer category"
        ),

        CustomScheme(
            name="Power Tiller",
            category="Farm Equipment",
            project_cost="Varies",
            subsidy="40%-50%",
            description="Power tiller subsidy.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Rotavator",
            category="Farm Equipment",
            project_cost="Varies",
            subsidy="₹28,000 - ₹44,000",
            description="Rotavator subsidy.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Vermicompost Project",
            category="Organic Farming",
            project_cost="600 cubic feet",
            subsidy="₹50,000",
            description="Vermicompost production unit.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Fruit Processing Unit",
            category="Food Processing",
            project_cost="₹24,00,000",
            subsidy="40%",
            description="Fruit processing industry.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Cold Storage",
            category="Infrastructure",
            project_cost="5000 MT",
            subsidy="35%-50%",
            description="Cold storage construction.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Warehouse",
            category="Infrastructure",
            project_cost="₹35,00,000",
            subsidy="25%",
            description="Warehouse construction.",
            eligibility="All farmers"
        ),

        CustomScheme(
            name="Agri Tourism",
            category="Business",
            project_cost="₹10,00,000",
            subsidy="As per scheme",
            description="Agriculture tourism project.",
            eligibility="All farmers"
        )

    ]

    db.session.add_all(schemes)
    db.session.commit()

    print("✅ Custom schemes added successfully!")