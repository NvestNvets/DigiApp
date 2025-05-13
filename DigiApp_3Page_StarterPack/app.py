from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import csv
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import openai
from twilio.rest import Client
from twilio_helpers import (
    send_sms, send_buyer_confirmation, send_seller_notification,
    send_affiliate_reminder, send_from_scratch_flow, send_tier_confirmation,
    handle_incoming_sms, log_affiliate_click, send_message
)
from gpt_helpers import (
    generate_titles, write_product_description, suggest_pricing,
    generate_affiliate_email, create_submission_summary, generate_landing_page,
    enhance_invoice_message, create_marketplace_listing, generate_social_captions,
    get_help_response, generate_content, generate_affiliate_code
)
from landing_generator import LandingPageGenerator
from config import Config

# Load environment variables
load_dotenv()
openai.api_key = Config.OPENAI_API_KEY

# Initialize Twilio client
twilio_client = Client(
    Config.TWILIO_ACCOUNT_SID,
    Config.TWILIO_AUTH_TOKEN
)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = Config.SECRET_KEY

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
INVOICE_FOLDER = 'invoices'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER

# Ensure required directories exist
for folder in [UPLOAD_FOLDER, DATA_FOLDER, INVOICE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize submissions.csv if it doesn't exist
submissions_path = os.path.join(DATA_FOLDER, 'submissions.csv')
if not os.path.exists(submissions_path):
    with open(submissions_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'name', 'phone', 'tier', 'payment_link', 'affiliate_code', 'file_path'])

# Initialize landing page generator
landing_generator = LandingPageGenerator()

# Validate required environment variables
Config.validate_required_vars()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_digi_email(to_email, subject, message_text):
    """Send email using SendGrid."""
    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        message = Mail(
            from_email=Config.SENDER_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message_text
        )
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_affiliate_link(code):
    """Generate a personalized referral link."""
    return f"https://yourdomain.com/?ref={code}"

def is_valid_link(link):
    """Validate PayPal.me or Gumroad payment link."""
    return link.startswith("https://paypal.me/") or "gumroad.com" in link

def add_to_marketplace(name, product, link, language):
    """Add product to marketplace.json."""
    data = []
    marketplace_path = os.path.join(DATA_FOLDER, 'marketplace.json')
    if os.path.exists(marketplace_path):
        with open(marketplace_path) as f:
            data = json.load(f)
    data.append({
        "name": name,
        "product": product,
        "link": link,
        "date_added": datetime.now().isoformat(),
        "language": language
    })
    with open(marketplace_path, "w") as f:
        json.dump(data, f, indent=2)

def create_invoice(name, product, price, affiliate_code=None, language='EN'):
    """Create invoice file with affiliate link."""
    os.makedirs(INVOICE_FOLDER, exist_ok=True)
    invoice_path = os.path.join(INVOICE_FOLDER, f"{name}_invoice.txt")
    
    affiliate_link = f"https://digiapp.com/?ref={affiliate_code}" if affiliate_code else None
    
    invoice_content = f"""
Invoice for {name}
Date: {datetime.now().strftime('%Y-%m-%d')}
Product: {product}
Amount: ${price}

Thank you for supporting veteran-owned businesses!

{f'Share your story and earn: {affiliate_link}' if affiliate_link else ''}
    """
    with open(invoice_path, "w") as f:
        f.write(invoice_content)

def save_submission(data, file_path=None):
    """Save form submission to CSV."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submission = {
        'timestamp': timestamp,
        'name': data.get('name', ''),
        'phone': data.get('phone', ''),
        'tier': data.get('tier', ''),
        'payment_link': data.get('payment_link', ''),
        'affiliate_code': data.get('affiliate_code', ''),
        'file_path': file_path if file_path else ''
    }
    
    with open(submissions_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=submission.keys())
        writer.writerow(submission)
    
    return submission

def update_affiliate_tracking(affiliate_code):
    """Update affiliate tracking data."""
    json_path = os.path.join(DATA_FOLDER, 'affiliates.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            affiliates = json.load(f)
    else:
        affiliates = {}
    
    if affiliate_code in affiliates:
        affiliates[affiliate_code]['referrals'] += 1
    else:
        affiliates[affiliate_code] = {
            'referrals': 1,
            'created_at': datetime.now().isoformat()
        }
    
    with open(json_path, 'w') as f:
        json.dump(affiliates, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html', 
                         paypal_link=Config.PAYPAL_ME_LINK,
                         base_url=Config.BASE_URL)

@app.route('/landing')
def landing():
    return render_template('landing.html',
                         paypal_link=Config.PAYPAL_ME_LINK,
                         stripe_tier1=Config.STRIPE_TIER1_LINK,
                         stripe_tier2=Config.STRIPE_TIER2_LINK,
                         stripe_tier3=Config.STRIPE_TIER3_LINK,
                         base_url=Config.BASE_URL)

@app.route('/submit', methods=['POST'])
def submit():
    # Validate payment link
    payment_link = request.form.get('payment_link')
    if not is_valid_link(payment_link):
        flash('Invalid payment link. Please use PayPal.me or Gumroad.')
        return redirect(url_for('landing'))

    # Handle file upload
    file_path = None
    if 'product_file' in request.files:
        file = request.files['product_file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

    # Get user preferences and language
    preferred_channel = 'sms'  # Default to SMS
    language = 'EN'  # Default to English
    phone = request.form.get('phone')
    
    if phone:
        pending_path = os.path.join(DATA_FOLDER, 'pending_creators.json')
        if os.path.exists(pending_path):
            with open(pending_path, 'r') as f:
                pending = json.load(f)
            if phone in pending:
                preferred_channel = pending[phone].get('preferred_channel', 'sms')
                language = pending[phone].get('language', 'EN')

    # Check if user can update product based on tier
    tier = request.form.get('tier')
    if not landing_generator.can_update_product(phone, tier):
        flash('You have reached your product update limit for this year. Please upgrade your tier for more updates.')
        return redirect(url_for('landing'))

    # Generate product data
    product_data = {
        'name': request.form.get('product_name', 'Digital Product'),
        'description': request.form.get('description', ''),
        'price': request.form.get('price', '0'),
        'payment_link': payment_link,
        'image_url': f"/uploads/{filename}" if file_path else '/static/default-product.jpg'
    }

    # Get creator data
    creator_data = {
        'phone': phone,
        'name': request.form.get('name', ''),
        'affiliate_code': generate_affiliate_code(phone),
        'rank': get_military_rank(get_profile(phone)) if get_profile(phone) else 'Veteran'
    }

    # Generate landing page
    landing_result = landing_generator.generate_landing_page(creator_data, product_data)

    # Save submission data
    submission = save_submission(request.form, file_path)
    submission['landing_url'] = landing_result['landing_url']

    # Send notifications using configured channels
    if Config.ENABLE_WHATSAPP:
        send_message(phone, landing_msg, preferred_channel='whatsapp')
    else:
        send_message(phone, landing_msg)

    # Handle "From Scratch" flow
    if request.form.get('from_scratch') == 'true':
        send_from_scratch_flow(phone, submission['name'], preferred_channel)

    # Create admin summary
    admin_summary = create_submission_summary(submission)
    with open(os.path.join(DATA_FOLDER, 'admin_summaries.txt'), 'a') as f:
        f.write(f"\n=== {datetime.now()} ===\n{admin_summary}\n")

    # Redirect to thank you page
    return redirect(url_for('thankyou', 
        submission=submission,
        landing_url=landing_result['landing_url']
    ))

@app.route('/thankyou')
def thankyou():
    submission = request.args.get('submission', {})
    affiliate_link = f"https://digiapp.com/?ref={submission.get('affiliate_code', '')}" if submission.get('affiliate_code') else None
    return render_template('thankyou.html', submission=submission, affiliate_link=affiliate_link)

@app.route('/view/<filename>')
def view_file(filename):
    """Serve PDF viewer for purchased content."""
    return render_template('viewer.html',
        pdf_url=url_for('uploaded_file', filename=filename),
        download_url=url_for('uploaded_file', filename=filename)
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generate-titles', methods=['POST'])
def generate_product_titles():
    product_summary = request.json.get('summary', '')
    titles = generate_titles(product_summary)
    return jsonify({'titles': titles})

@app.route('/generate-description', methods=['POST'])
def generate_description():
    product_details = request.json.get('details', '')
    description = write_product_description(product_details)
    return jsonify({'description': description})

@app.route('/suggest-price', methods=['POST'])
def suggest_price():
    product_type = request.json.get('type', '')
    details = request.json.get('details', '')
    price_range = suggest_pricing(product_type, details)
    return jsonify({'price_range': price_range})

@app.route('/generate-affiliate-email', methods=['POST'])
def generate_affiliate_email_route():
    data = request.json
    email_content = generate_affiliate_email(
        data.get('name', ''),
        data.get('product', ''),
        data.get('ref_link', '')
    )
    return jsonify({'email_content': email_content})

@app.route('/help', methods=['POST'])
def help_route():
    question = request.json.get('question', '')
    response = get_help_response(question)
    return jsonify({'response': response})

@app.route('/track/<affiliate_code>')
def track_affiliate(affiliate_code):
    """Track affiliate link clicks."""
    referrer = request.headers.get('Referer', 'direct')
    log_affiliate_click(affiliate_code, referrer)
    return redirect(url_for('index'))

@app.route('/sms', methods=['POST'])
def handle_sms():
    """Handle incoming SMS/WhatsApp/iMessage messages."""
    from_number = request.values.get('From', '')
    message = request.values.get('Body', '')
    
    # Detect message source
    is_whatsapp = from_number.startswith('whatsapp:')
    is_imessage = 'imessage' in request.values.get('MessageSid', '').lower()
    
    if is_whatsapp:
        from_number = from_number.replace('whatsapp:', '')
    
    # Get user preferences
    pending_path = os.path.join(DATA_FOLDER, 'pending_creators.json')
    preferred_channel = 'whatsapp' if is_whatsapp else 'imessage' if is_imessage else 'sms'
    language = 'EN'
    
    if os.path.exists(pending_path):
        with open(pending_path, 'r') as f:
            pending = json.load(f)
        if from_number in pending:
            pending[from_number]['preferred_channel'] = preferred_channel
            with open(pending_path, 'w') as f:
                json.dump(pending, f, indent=2)
    
    # Handle the message
    response = handle_incoming_sms(from_number, message)
    
    return str(response)

if __name__ == '__main__':
    app.run(debug=True) 