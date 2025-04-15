from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'farmer' or 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    farmer_profile = db.relationship('FarmerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    pellets = db.relationship('PelletListing', backref='seller', lazy=True, cascade='all, delete-orphan')
    requirements = db.relationship('Requirement', backref='company', lazy=True, cascade='all, delete-orphan')
    offers_made = db.relationship('Offer', backref='buyer', foreign_keys='Offer.buyer_id', lazy=True)
    offers_received = db.relationship('Offer', backref='seller', foreign_keys='Offer.seller_id', lazy=True)
    orders_placed = db.relationship('Order', backref='buyer', foreign_keys='Order.buyer_id', lazy=True)
    orders_received = db.relationship('Order', backref='seller', foreign_keys='Order.seller_id', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_farmer(self):
        return self.role == 'farmer'

    def is_company(self):
        return self.role == 'company'


class FarmerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    farm_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)


class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry_type = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    description = db.Column(db.Text)


class PelletListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    biomass_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in tons
    price_per_ton = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    availability_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    offers = db.relationship('Offer', backref='listing', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='listing', lazy=True)


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    biomass_type = db.Column(db.String(50), nullable=False)
    quantity_needed = db.Column(db.Float, nullable=False)  # in tons
    price_per_ton = db.Column(db.Float)  # Optional, if company wants to specify a price
    description = db.Column(db.Text)
    needed_by_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('pellet_listing.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in tons
    price_per_ton = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('pellet_listing.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in tons
    total_price = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='processing')  # processing, shipped, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
