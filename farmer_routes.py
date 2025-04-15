from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import PelletListing, Offer, Order, User, CompanyProfile, Requirement
from forms import PelletListingForm, OfferForm, OrderForm
from datetime import datetime
from sqlalchemy import and_, desc

farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')


@farmer_bp.before_request
def check_farmer():
    if not current_user.is_authenticated or not current_user.is_farmer():
        flash('Access denied. Farmer account required.', 'danger')
        return redirect(url_for('auth.login'))


@farmer_bp.route('/dashboard')
@login_required
def dashboard():
    # Get farmer's active listings
    active_listings = PelletListing.query.filter_by(
        seller_id=current_user.id, 
        is_available=True
    ).order_by(desc(PelletListing.created_at)).all()
    
    # Get pending offers for the farmer
    pending_offers = Offer.query.filter(
        Offer.seller_id == current_user.id,
        Offer.status == 'pending'
    ).order_by(desc(Offer.created_at)).all()
    
    # Get company requirements
    company_requirements = Requirement.query.filter_by(
        is_active=True
    ).order_by(desc(Requirement.created_at)).limit(5).all()
    
    # Get active orders
    active_orders = Order.query.filter(
        Order.seller_id == current_user.id,
        Order.status.in_(['processing', 'shipped'])
    ).order_by(desc(Order.created_at)).all()

    return render_template(
        'farmer/dashboard.html',
        active_listings=active_listings,
        pending_offers=pending_offers,
        company_requirements=company_requirements,
        active_orders=active_orders
    )


@farmer_bp.route('/sell_pellets', methods=['GET', 'POST'])
@login_required
def sell_pellets():
    form = PelletListingForm()
    
    if form.validate_on_submit():
        listing = PelletListing(
            seller_id=current_user.id,
            title=form.title.data,
            biomass_type=form.biomass_type.data,
            quantity=form.quantity.data,
            price_per_ton=form.price_per_ton.data,
            description=form.description.data,
            availability_date=form.availability_date.data,
            location=form.location.data,
            is_available=True
        )
        
        db.session.add(listing)
        db.session.commit()
        
        flash('Your pellet listing has been created successfully!', 'success')
        return redirect(url_for('farmer.dashboard'))
    
    return render_template('farmer/sell_pellets.html', form=form)


@farmer_bp.route('/view_offers')
@login_required
def view_offers():
    # Get all offers for the farmer's listings
    offers = Offer.query.join(PelletListing).filter(
        PelletListing.seller_id == current_user.id
    ).order_by(desc(Offer.created_at)).all()
    
    return render_template('farmer/view_offers.html', offers=offers)


@farmer_bp.route('/respond_to_offer/<int:offer_id>/<string:action>')
@login_required
def respond_to_offer(offer_id, action):
    offer = Offer.query.get_or_404(offer_id)
    
    # Verify the offer belongs to the farmer
    if offer.seller_id != current_user.id:
        flash('You do not have permission to respond to this offer.', 'danger')
        return redirect(url_for('farmer.view_offers'))
    
    if action == 'accept':
        offer.status = 'accepted'
        # Create an order automatically
        order = Order(
            listing_id=offer.listing_id,
            buyer_id=offer.buyer_id,
            seller_id=current_user.id,
            quantity=offer.quantity,
            total_price=offer.quantity * offer.price_per_ton,
            delivery_address="To be confirmed",
            status='processing'
        )
        db.session.add(order)
        
        # Update the listing quantity if needed
        listing = offer.listing
        if listing.quantity <= offer.quantity:
            listing.is_available = False
        else:
            listing.quantity -= offer.quantity
        
        flash('Offer accepted and order created.', 'success')
    
    elif action == 'reject':
        offer.status = 'rejected'
        flash('Offer rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('farmer.view_offers'))


@farmer_bp.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    # Verify the listing belongs to the farmer
    if listing.seller_id != current_user.id:
        flash('You do not have permission to edit this listing.', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    form = PelletListingForm()
    
    if request.method == 'GET':
        form.title.data = listing.title
        form.biomass_type.data = listing.biomass_type
        form.quantity.data = listing.quantity
        form.price_per_ton.data = listing.price_per_ton
        form.description.data = listing.description
        form.availability_date.data = listing.availability_date
        form.location.data = listing.location
    
    if form.validate_on_submit():
        listing.title = form.title.data
        listing.biomass_type = form.biomass_type.data
        listing.quantity = form.quantity.data
        listing.price_per_ton = form.price_per_ton.data
        listing.description = form.description.data
        listing.availability_date = form.availability_date.data
        listing.location = form.location.data
        
        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('farmer.dashboard'))
    
    return render_template('farmer/sell_pellets.html', form=form, editing=True)


@farmer_bp.route('/delete_listing/<int:listing_id>')
@login_required
def delete_listing(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    # Verify the listing belongs to the farmer
    if listing.seller_id != current_user.id:
        flash('You do not have permission to delete this listing.', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    # Check if there are active orders
    active_orders = Order.query.filter(
        Order.listing_id == listing.id,
        Order.status.in_(['processing', 'shipped'])
    ).first()
    
    if active_orders:
        flash('Cannot delete listing with active orders.', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    db.session.delete(listing)
    db.session.commit()
    
    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('farmer.dashboard'))


@farmer_bp.route('/view_companies')
@login_required
def view_companies():
    # Get all companies
    companies = User.query.filter_by(role='company').join(CompanyProfile).all()
    return render_template('farmer/view_companies.html', companies=companies)


@farmer_bp.route('/view_requirements')
@login_required
def view_requirements():
    # Get all active requirements
    requirements = Requirement.query.filter_by(is_active=True).order_by(desc(Requirement.created_at)).all()
    return render_template('farmer/view_requirements.html', requirements=requirements)


@farmer_bp.route('/orders')
@login_required
def orders():
    # Get all orders where the farmer is the seller
    orders_as_seller = Order.query.filter_by(seller_id=current_user.id).order_by(desc(Order.created_at)).all()
    # Get all orders where the farmer is the buyer
    orders_as_buyer = Order.query.filter_by(buyer_id=current_user.id).order_by(desc(Order.created_at)).all()
    
    return render_template(
        'farmer/orders.html',
        orders_as_seller=orders_as_seller,
        orders_as_buyer=orders_as_buyer
    )


@farmer_bp.route('/update_order_status/<int:order_id>/<string:status>')
@login_required
def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    
    # Verify the order belongs to the farmer as seller
    if order.seller_id != current_user.id:
        flash('You do not have permission to update this order.', 'danger')
        return redirect(url_for('farmer.orders'))
    
    valid_statuses = ['processing', 'shipped', 'delivered', 'cancelled']
    if status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('farmer.orders'))
    
    order.status = status
    db.session.commit()
    
    flash(f'Order status updated to {status}.', 'success')
    return redirect(url_for('farmer.orders'))


@farmer_bp.route('/buy_pellets')
@login_required
def buy_pellets():
    # Get all available pellet listings from other farmers
    available_pellets = PelletListing.query.filter(
        PelletListing.seller_id != current_user.id,
        PelletListing.is_available == True
    ).order_by(desc(PelletListing.created_at)).all()
    
    return render_template('farmer/buy_pellets.html', listings=available_pellets)


@farmer_bp.route('/make_offer/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def make_offer(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    # Prevent offering on own listings
    if listing.seller_id == current_user.id:
        flash('You cannot make an offer on your own listing.', 'danger')
        return redirect(url_for('farmer.buy_pellets'))
    
    form = OfferForm()
    
    # Pre-populate form with listing price
    if request.method == 'GET':
        form.price_per_ton.data = listing.price_per_ton
    
    if form.validate_on_submit():
        # Validate quantity
        if form.quantity.data > listing.quantity:
            flash('Your requested quantity exceeds the available amount.', 'danger')
            return render_template('farmer/make_offer.html', form=form, listing=listing)
        
        offer = Offer(
            listing_id=listing.id,
            buyer_id=current_user.id,
            seller_id=listing.seller_id,
            quantity=form.quantity.data,
            price_per_ton=form.price_per_ton.data,
            message=form.message.data,
            status='pending'
        )
        
        db.session.add(offer)
        db.session.commit()
        
        flash('Your offer has been submitted!', 'success')
        return redirect(url_for('farmer.buy_pellets'))
    
    return render_template('farmer/make_offer.html', form=form, listing=listing)


@farmer_bp.route('/place_order/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def place_order(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    # Prevent ordering from own listings
    if listing.seller_id == current_user.id:
        flash('You cannot place an order on your own listing.', 'danger')
        return redirect(url_for('farmer.buy_pellets'))
    
    form = OrderForm()
    
    if form.validate_on_submit():
        # Validate quantity
        if form.quantity.data > listing.quantity:
            flash('Your requested quantity exceeds the available amount.', 'danger')
            return render_template('farmer/place_order.html', form=form, listing=listing)
        
        # Calculate total price
        total_price = form.quantity.data * listing.price_per_ton
        
        order = Order(
            listing_id=listing.id,
            buyer_id=current_user.id,
            seller_id=listing.seller_id,
            quantity=form.quantity.data,
            total_price=total_price,
            delivery_address=form.delivery_address.data,
            delivery_date=form.delivery_date.data,
            status='processing'
        )
        
        # Update the listing quantity
        if listing.quantity <= form.quantity.data:
            listing.is_available = False
        else:
            listing.quantity -= form.quantity.data
        
        db.session.add(order)
        db.session.commit()
        
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('farmer.dashboard'))
    
    return render_template('farmer/place_order.html', form=form, listing=listing)
