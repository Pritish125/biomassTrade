from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import PelletListing, Offer, Order, User, FarmerProfile, Requirement
from forms import RequirementForm, OfferForm, OrderForm
from datetime import datetime
from sqlalchemy import desc

company_bp = Blueprint('company', __name__, url_prefix='/company')


@company_bp.before_request
def check_company():
    if not current_user.is_authenticated or not current_user.is_company():
        flash('Access denied. Company account required.', 'danger')
        return redirect(url_for('auth.login'))


@company_bp.route('/dashboard')
@login_required
def dashboard():
    # Get available pellet listings
    available_pellets = PelletListing.query.filter_by(
        is_available=True
    ).order_by(desc(PelletListing.created_at)).limit(5).all()
    
    # Get company's active requirements
    active_requirements = Requirement.query.filter_by(
        company_id=current_user.id,
        is_active=True
    ).order_by(desc(Requirement.created_at)).all()
    
    # Get pending offers made by the company
    pending_offers = Offer.query.filter(
        Offer.buyer_id == current_user.id,
        Offer.status == 'pending'
    ).order_by(desc(Offer.created_at)).all()
    
    # Get active orders
    active_orders = Order.query.filter(
        Order.buyer_id == current_user.id,
        Order.status.in_(['processing', 'shipped'])
    ).order_by(desc(Order.created_at)).all()

    return render_template(
        'company/dashboard.html',
        available_pellets=available_pellets,
        active_requirements=active_requirements,
        pending_offers=pending_offers,
        active_orders=active_orders
    )


@company_bp.route('/available_pellets')
@login_required
def available_pellets():
    # Get all available pellet listings
    pellets = PelletListing.query.filter_by(
        is_available=True
    ).order_by(desc(PelletListing.created_at)).all()
    
    # Get biomass types for filtering
    biomass_types = db.session.query(PelletListing.biomass_type.distinct()).all()
    biomass_types = [t[0] for t in biomass_types]
    
    return render_template(
        'company/available_pellets.html', 
        pellets=pellets,
        biomass_types=biomass_types
    )


@company_bp.route('/post_requirements', methods=['GET', 'POST'])
@login_required
def post_requirements():
    form = RequirementForm()
    
    if form.validate_on_submit():
        requirement = Requirement(
            company_id=current_user.id,
            title=form.title.data,
            biomass_type=form.biomass_type.data,
            quantity_needed=form.quantity_needed.data,
            price_per_ton=form.price_per_ton.data,
            description=form.description.data,
            needed_by_date=form.needed_by_date.data,
            is_active=True
        )
        
        db.session.add(requirement)
        db.session.commit()
        
        flash('Your requirement has been posted successfully!', 'success')
        return redirect(url_for('company.dashboard'))
    
    return render_template('company/post_requirements.html', form=form)


@company_bp.route('/edit_requirement/<int:requirement_id>', methods=['GET', 'POST'])
@login_required
def edit_requirement(requirement_id):
    requirement = Requirement.query.get_or_404(requirement_id)
    
    # Verify the requirement belongs to the company
    if requirement.company_id != current_user.id:
        flash('You do not have permission to edit this requirement.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    form = RequirementForm()
    
    if request.method == 'GET':
        form.title.data = requirement.title
        form.biomass_type.data = requirement.biomass_type
        form.quantity_needed.data = requirement.quantity_needed
        form.price_per_ton.data = requirement.price_per_ton
        form.description.data = requirement.description
        form.needed_by_date.data = requirement.needed_by_date
    
    if form.validate_on_submit():
        requirement.title = form.title.data
        requirement.biomass_type = form.biomass_type.data
        requirement.quantity_needed = form.quantity_needed.data
        requirement.price_per_ton = form.price_per_ton.data
        requirement.description = form.description.data
        requirement.needed_by_date = form.needed_by_date.data
        
        db.session.commit()
        flash('Requirement updated successfully!', 'success')
        return redirect(url_for('company.dashboard'))
    
    return render_template('company/post_requirements.html', form=form, editing=True)


@company_bp.route('/delete_requirement/<int:requirement_id>')
@login_required
def delete_requirement(requirement_id):
    requirement = Requirement.query.get_or_404(requirement_id)
    
    # Verify the requirement belongs to the company
    if requirement.company_id != current_user.id:
        flash('You do not have permission to delete this requirement.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    db.session.delete(requirement)
    db.session.commit()
    
    flash('Requirement deleted successfully!', 'success')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/toggle_requirement/<int:requirement_id>')
@login_required
def toggle_requirement(requirement_id):
    requirement = Requirement.query.get_or_404(requirement_id)
    
    # Verify the requirement belongs to the company
    if requirement.company_id != current_user.id:
        flash('You do not have permission to update this requirement.', 'danger')
        return redirect(url_for('company.dashboard'))
    
    requirement.is_active = not requirement.is_active
    db.session.commit()
    
    status = "activated" if requirement.is_active else "deactivated"
    flash(f'Requirement {status} successfully!', 'success')
    return redirect(url_for('company.dashboard'))


@company_bp.route('/make_offer/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def make_offer(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    form = OfferForm()
    
    # Pre-populate form with listing price
    if request.method == 'GET':
        form.price_per_ton.data = listing.price_per_ton
    
    if form.validate_on_submit():
        # Validate quantity
        if form.quantity.data > listing.quantity:
            flash('Your requested quantity exceeds the available amount.', 'danger')
            return render_template('company/make_offer.html', form=form, listing=listing)
        
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
        return redirect(url_for('company.available_pellets'))
    
    return render_template('company/make_offer.html', form=form, listing=listing)


@company_bp.route('/view_offers')
@login_required
def view_offers():
    # Get all offers made by the company
    offers = Offer.query.filter_by(buyer_id=current_user.id).order_by(desc(Offer.created_at)).all()
    
    return render_template('company/view_offers.html', offers=offers)


@company_bp.route('/place_order/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def place_order(listing_id):
    listing = PelletListing.query.get_or_404(listing_id)
    
    form = OrderForm()
    
    if form.validate_on_submit():
        # Validate quantity
        if form.quantity.data > listing.quantity:
            flash('Your requested quantity exceeds the available amount.', 'danger')
            return render_template('company/place_order.html', form=form, listing=listing)
        
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
        return redirect(url_for('company.dashboard'))
    
    return render_template('company/place_order.html', form=form, listing=listing)


@company_bp.route('/orders')
@login_required
def orders():
    # Get all orders where the company is the buyer
    orders_as_buyer = Order.query.filter_by(buyer_id=current_user.id).order_by(desc(Order.created_at)).all()
    
    return render_template('company/orders.html', orders=orders_as_buyer)


@company_bp.route('/cancel_order/<int:order_id>')
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Verify the order belongs to the company as buyer
    if order.buyer_id != current_user.id:
        flash('You do not have permission to cancel this order.', 'danger')
        return redirect(url_for('company.orders'))
    
    # Only allow cancellation of processing orders
    if order.status != 'processing':
        flash('Can only cancel orders that are still processing.', 'danger')
        return redirect(url_for('company.orders'))
    
    order.status = 'cancelled'
    
    # Return the quantity to the listing
    listing = order.listing
    if not listing.is_available:
        listing.is_available = True
    listing.quantity += order.quantity
    
    db.session.commit()
    
    flash('Order cancelled successfully!', 'success')
    return redirect(url_for('company.orders'))


@company_bp.route('/view_farmers')
@login_required
def view_farmers():
    # Get all farmers
    farmers = User.query.filter_by(role='farmer').join(FarmerProfile).all()
    return render_template('company/view_farmers.html', farmers=farmers)
