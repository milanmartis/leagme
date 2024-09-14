from datetime import datetime
from . import db
from .models import User, Product, Role, ProductCategory
import uuid  # Import pre generovanie jedinečných identifikátorov


def initialize_database():
    # Skontrolujte, či existuje používateľ s id=1
    if not User.query.filter_by(id=1).first():
        new_user = User(
            id=1,
            email="user@example.com",
            first_name="Admin",
            fs_uniquifier=str(uuid.uuid4()),  # Generovanie jedinečného identifikátora
            active=True
        )
        db.session.add(new_user)
        db.session.commit()

    # Vytvorenie záznamov pre Role, ProductCategory a Product
    if not Role.query.filter_by(id=1).first():
        role1 = Role(id=1, name='Admin', description='', permissions='read,write,delete,manage_users')
        role2 = Role(id=2, name='Player', description='', permissions='read')
        role3 = Role(id=3, name='Manager', description='', permissions='read,write')
        db.session.add_all([role1, role2, role3])
        db.session.commit()

    if not ProductCategory.query.filter_by(id=1).first():
        category = ProductCategory(id=1, name='poplatky')
        db.session.add(category)
        db.session.commit()

    if not Product.query.filter_by(id=45).first():
        product1 = Product(
            id=45,
            title='Player',
            content='aaa',
            price=5.00,
            old_price=1.00,
            user_id=1,
            product_category_id=1,
            is_visible=True,
            stripe_link='',  # Pridajte prázdny reťazec pre stripe_link
            youtube_link=''  # Pridajte prázdny reťazec pre youtube_link
        )
        product2 = Product(
            id=46,
            title='Manager',
            content='aaa',
            price=5.00,
            old_price=1.00,
            user_id=1,
            product_category_id=1,
            is_visible=True,
            stripe_link='',  # Pridajte prázdny reťazec pre stripe_link
            youtube_link=''  # Pridajte prázdny reťazec pre youtube_link
        )
        db.session.add_all([product1, product2])
        db.session.commit()
