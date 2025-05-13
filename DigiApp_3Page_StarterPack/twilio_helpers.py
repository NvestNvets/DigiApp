from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import openai
from config import Config

# Load environment variables
load_dotenv()

# Initialize Twilio client
twilio_client = Client(
    Config.TWILIO_ACCOUNT_SID,
    Config.TWILIO_AUTH_TOKEN
)

# Enhanced language support with flags and military terminology
SUPPORTED_LANGUAGES = {
    # North America
    'EN': {'name': 'English', 'flag': '🇺🇸', 'military': 'US Armed Forces'},
    'ES-MX': {'name': 'Spanish (Mexico)', 'flag': '🇲🇽', 'military': 'Fuerzas Armadas Mexicanas'},
    'FR-CA': {'name': 'French (Canada)', 'flag': '🇨🇦', 'military': 'Canadian Armed Forces'},
    
    # Europe
    'ES': {'name': 'Spanish', 'flag': '🇪🇸', 'military': 'Fuerzas Armadas Españolas'},
    'FR': {'name': 'French', 'flag': '🇫🇷', 'military': 'Forces Armées Françaises'},
    'DE': {'name': 'German', 'flag': '🇩🇪', 'military': 'Bundeswehr'},
    'IT': {'name': 'Italian', 'flag': '🇮🇹', 'military': 'Forze Armate Italiane'},
    'PT': {'name': 'Portuguese', 'flag': '🇵🇹', 'military': 'Forças Armadas Portuguesas'},
    'NL': {'name': 'Dutch', 'flag': '🇳🇱', 'military': 'Koninklijke Landmacht'},
    'PL': {'name': 'Polish', 'flag': '🇵🇱', 'military': 'Siły Zbrojne Rzeczypospolitej Polskiej'},
    'UK': {'name': 'British English', 'flag': '🇬🇧', 'military': 'British Armed Forces'},
    
    # Asia
    'CN': {'name': 'Chinese', 'flag': '🇨🇳', 'military': '中国人民解放军'},
    'JP': {'name': 'Japanese', 'flag': '🇯🇵', 'military': '自衛隊'},
    'KR': {'name': 'Korean', 'flag': '🇰🇷', 'military': '대한민국 국군'},
    'IN': {'name': 'Hindi', 'flag': '🇮🇳', 'military': 'भारतीय सशस्त्र सेनाएं'},
    'TH': {'name': 'Thai', 'flag': '🇹🇭', 'military': 'กองทัพไทย'},
    'VN': {'name': 'Vietnamese', 'flag': '🇻🇳', 'military': 'Quân đội Nhân dân Việt Nam'},
    
    # Middle East
    'AR': {'name': 'Arabic', 'flag': '🇸🇦', 'military': 'القوات المسلحة السعودية'},
    'HE': {'name': 'Hebrew', 'flag': '🇮🇱', 'military': 'צבא ההגנה לישראל'},
    'TR': {'name': 'Turkish', 'flag': '🇹🇷', 'military': 'Türk Silahlı Kuvvetleri'},
    
    # Oceania
    'AU': {'name': 'Australian English', 'flag': '🇦🇺', 'military': 'Australian Defence Force'},
    'NZ': {'name': 'New Zealand English', 'flag': '🇳🇿', 'military': 'New Zealand Defence Force'},
    
    # Africa
    'AF': {'name': 'Afrikaans', 'flag': '🇿🇦', 'military': 'South African National Defence Force'},
    'SW': {'name': 'Swahili', 'flag': '🇰🇪', 'military': 'Kenya Defence Forces'},
    
    # South America
    'ES-AR': {'name': 'Spanish (Argentina)', 'flag': '🇦🇷', 'military': 'Fuerzas Armadas Argentinas'},
    'PT-BR': {'name': 'Portuguese (Brazil)', 'flag': '🇧🇷', 'military': 'Forças Armadas Brasileiras'},
    'ES-CO': {'name': 'Spanish (Colombia)', 'flag': '🇨🇴', 'military': 'Fuerzas Militares de Colombia'}
}

def get_military_greeting(lang_code):
    """Get military-style greeting in user's language."""
    greetings = {
        # North America
        'EN': "At Ease, Veteran!",
        'ES-MX': "¡A sus órdenes, Veterano!",
        'FR-CA': "Repos, Vétéran!",
        
        # Europe
        'ES': "¡A sus órdenes, Veterano!",
        'FR': "Repos, Vétéran!",
        'DE': "Rührt euch, Veteran!",
        'IT': "Riposo, Veterano!",
        'PT': "À vontade, Veterano!",
        'NL': "Rust, Veteraan!",
        'PL': "Spocznij, Weteranie!",
        'UK': "At Ease, Veteran!",
        
        # Asia
        'CN': "稍息，老兵！",
        'JP': "休め、ベテラン！",
        'KR': "쉬어, 베테랑!",
        'IN': "विश्राम, अनुभवी!",
        'TH': "พัก, ทหารผ่านศึก!",
        'VN': "Nghỉ, Cựu chiến binh!",
        
        # Middle East
        'AR': "استرح، المحارب القديم!",
        'HE': "הרגע, ותיק!",
        'TR': "Rahat, Gaziler!",
        
        # Oceania
        'AU': "At Ease, Digger!",
        'NZ': "At Ease, Veteran!",
        
        # Africa
        'AF': "Rus, Veteraan!",
        'SW': "Pumzika, Mkongwe!",
        
        # South America
        'ES-AR': "¡A sus órdenes, Veterano!",
        'PT-BR': "À vontade, Veterano!",
        'ES-CO': "¡A sus órdenes, Veterano!"
    }
    return greetings.get(lang_code, greetings['EN'])

def get_military_rank_prefix(lang_code):
    """Get military rank prefix in user's language."""
    prefixes = {
        # North America
        'EN': "Rank:",
        'ES-MX': "Rango:",
        'FR-CA': "Grade:",
        
        # Europe
        'ES': "Rango:",
        'FR': "Grade:",
        'DE': "Dienstgrad:",
        'IT': "Grado:",
        'PT': "Posto:",
        'NL': "Rang:",
        'PL': "Stopień:",
        'UK': "Rank:",
        
        # Asia
        'CN': "军衔：",
        'JP': "階級：",
        'KR': "계급:",
        'IN': "रैंक:",
        'TH': "ยศ:",
        'VN': "Cấp bậc:",
        
        # Middle East
        'AR': "الرتبة:",
        'HE': "דרגה:",
        'TR': "Rütbe:",
        
        # Oceania
        'AU': "Rank:",
        'NZ': "Rank:",
        
        # Africa
        'AF': "Rang:",
        'SW': "Cheo:",
        
        # South America
        'ES-AR': "Rango:",
        'PT-BR': "Posto:",
        'ES-CO': "Rango:"
    }
    return prefixes.get(lang_code, prefixes['EN'])

def detect_language(text):
    """Detect language using OpenAI."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Detect the language of the following text. Return only the language code (EN, ES, FR)."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error detecting language: {e}")
        return 'EN'  # Default to English

def translate_text(text, target_lang):
    """Translate text using OpenAI."""
    if target_lang == 'EN':
        return text
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate the following text to {SUPPORTED_LANGUAGES[target_lang]['name']}. Maintain the same tone and formatting."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def send_message(to_number, message, preferred_channel='sms'):
    """Send message via SMS or WhatsApp."""
    try:
        if preferred_channel == 'whatsapp' and Config.ENABLE_WHATSAPP:
            from_number = f"whatsapp:{Config.TWILIO_PHONE_NUMBER}"
            to_number = f"whatsapp:{to_number}"
        else:
            from_number = Config.TWILIO_PHONE_NUMBER
            
        message = twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None

def send_buyer_confirmation(phone, product_name, price, affiliate_link=None):
    """Send confirmation to buyer."""
    message = f"""
🎖️ Thank you for supporting a veteran's digital product!

Product: {product_name}
Amount: ${price}

View your purchase: {Config.BASE_URL}/purchases
    """
    if affiliate_link:
        message += f"\nShare with friends: {affiliate_link}"
    
    return send_message(phone, message)

def send_seller_notification(phone, amount, affiliate_link):
    """Send notification to seller."""
    message = f"""
🎖️ New Sale Alert!

Amount: ${amount}
Affiliate Link: {affiliate_link}

View your dashboard: {Config.BASE_URL}/dashboard
    """
    return send_message(phone, message)

def send_affiliate_reminder(phone, affiliate_code, preferred_channel='sms'):
    """Send reminder to affiliate about their link."""
    message = f"""
🤝 Keep sharing your story!

Your affiliate link:
https://digiapp.com/?ref={affiliate_code}

Reply STATS to see your impact
    """
    return send_message(phone, message, preferred_channel)

def send_from_scratch_flow(phone, name, preferred_channel='sms'):
    """Send starter guide and instructions to new creator."""
    welcome_msg = f"""
👋 Welcome {name}!

I'm AI K9 Codee, here to help you launch your digital product.

First, let's get you started with our free guide:
https://digiapp.com/guides/starter

Reply READY when you've reviewed it
    """
    send_message(phone, welcome_msg, preferred_channel)
    
    # Store in pending_creators.json
    pending_path = 'data/pending_creators.json'
    if os.path.exists(pending_path):
        with open(pending_path, 'r') as f:
            pending = json.load(f)
    else:
        pending = {}
    
    pending[phone] = {
        'name': name,
        'joined': datetime.now().isoformat(),
        'status': 'pending_guide',
        'preferred_channel': preferred_channel
    }
    
    with open(pending_path, 'w') as f:
        json.dump(pending, f, indent=2)

def send_tier_confirmation(phone, tier, eta):
    """Send tier selection confirmation."""
    message = f"""
🎯 You're on your way!

Selected: {tier}
ETA: {eta}

Next steps:
1. Upload your product
2. Set your price
3. Share your story

Need help? Reply CODEE
    """
    return send_message(phone, message, 'sms')

def handle_incoming_sms(from_number, message):
    """Process incoming SMS commands."""
    message = message.upper().strip()
    
    # Get user preferences
    pending_path = 'data/pending_creators.json'
    preferred_channel = 'sms'
    language = 'EN'
    if os.path.exists(pending_path):
        with open(pending_path, 'r') as f:
            pending = json.load(f)
        if from_number in pending:
            preferred_channel = pending[from_number].get('preferred_channel', 'sms')
            language = pending[from_number].get('language', 'EN')
    
    # Handle channel switching
    if message == "WHATSAPP":
        return handle_channel_switch(from_number, 'whatsapp')
    elif message == "IMESSAGE":
        return handle_channel_switch(from_number, 'imessage')
    
    # Handle language selection
    if message in SUPPORTED_LANGUAGES:
        return handle_language_switch(from_number, message)
    
    # Handle commands
    if message == "HELP":
        response = f"""
🎖️ {get_military_greeting(language)}

📋 Available Commands:

• GUIDES - Access mission briefings
• STATUS - Check mission progress
• CODEE [question] - Request AI K9 backup
• STATS - View mission impact
• WHATSAPP - Switch to WhatsApp
• IMESSAGE - Switch to iMessage
• {format_language_options()}
        """
        return send_message(from_number, response, preferred_channel)
    
    elif message == "GUIDES":
        response = """
📚 Available Guides:

1. Digital Product Creation
2. Marketing Basics
3. Affiliate Success
4. Veteran Resources

Reply with the number you want
        """
        return send_message(from_number, response, preferred_channel)
    
    elif message == "STATUS":
        # Check status in pending_creators.json
        if os.path.exists(pending_path):
            with open(pending_path, 'r') as f:
                pending = json.load(f)
            status = pending.get(from_number, {}).get('status', 'not_found')
        else:
            status = 'not_found'
        
        response = f"""
Current Status: {status}

Need to update? Reply UPDATE
        """
        return send_message(from_number, response, preferred_channel)
    
    elif message.startswith("CODEE"):
        # Extract question and send to GPT
        question = message[6:].strip()
        # TODO: Integrate with GPT helper
        response = "AI K9 Codee is processing your question..."
        return send_message(from_number, response, preferred_channel)
    
    elif message == "STATS":
        # Get stats from affiliates.json
        stats_path = 'data/affiliates.json'
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as f:
                affiliates = json.load(f)
            # Find affiliate by phone
            for code, data in affiliates.items():
                if data.get('phone') == from_number:
                    response = f"""
Your Impact:
• Referrals: {data.get('referrals', 0)}
• Earnings: ${data.get('earnings', 0)}
• Active Links: {data.get('active_links', 0)}
                    """
                    return send_message(from_number, response, preferred_channel)
        
        response = "No stats found. Start sharing your story!"
        return send_message(from_number, response, preferred_channel)

def log_affiliate_click(affiliate_code, referrer):
    """Log affiliate link click and send reminder."""
    json_path = 'data/affiliates.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            affiliates = json.load(f)
    else:
        affiliates = {}
    
    if affiliate_code in affiliates:
        affiliate = affiliates[affiliate_code]
        affiliate['clicks'] = affiliate.get('clicks', 0) + 1
        affiliate['last_click'] = datetime.now().isoformat()
        
        with open(json_path, 'w') as f:
            json.dump(affiliates, f, indent=2)
        
        # Send reminder to affiliate
        if 'phone' in affiliate:
            send_affiliate_reminder(
                affiliate['phone'], 
                affiliate_code,
                affiliate.get('preferred_channel', 'sms')
            )

def handle_channel_switch(from_number, channel):
    """Handle switching between messaging channels."""
    pending_path = 'data/pending_creators.json'
    if os.path.exists(pending_path):
        with open(pending_path, 'r') as f:
            pending = json.load(f)
        if from_number in pending:
            pending[from_number]['preferred_channel'] = channel
            with open(pending_path, 'w') as f:
                json.dump(pending, f, indent=2)
    
    return send_message(from_number, f"""
✅ Channel switch successful!
You're now receiving messages via {channel.upper()}
    """, channel)

def handle_language_switch(from_number, lang_code):
    """Handle language preference changes."""
    pending_path = 'data/pending_creators.json'
    if os.path.exists(pending_path):
        with open(pending_path, 'r') as f:
            pending = json.load(f)
        if from_number in pending:
            pending[from_number]['language'] = lang_code
            with open(pending_path, 'w') as f:
                json.dump(pending, f, indent=2)
    
    return send_message(from_number, f"""
✅ {SUPPORTED_LANGUAGES[lang_code]['flag']} Language set to {SUPPORTED_LANGUAGES[lang_code]['name']}
Military Branch: {SUPPORTED_LANGUAGES[lang_code]['military']}
    """)

def format_language_options():
    """Format language options with flags."""
    return "\n".join([f"• {code} - {data['flag']} {data['name']}" 
                     for code, data in SUPPORTED_LANGUAGES.items()])

def send_digibuyer_flow(phone, name, product_name, product_link, seller_name, preferred_channel='sms'):
    """Send enhanced DigiBuyer flow with affiliate opportunity."""
    # Initial purchase confirmation
    purchase_msg = f"""
🎖️ Thank you for supporting {seller_name}, a fellow veteran!

Your digital product "{product_name}" is ready:
{product_link}

📱 *Support More Veterans:*
Share your purchase and earn:
https://digiapp.com/affiliate/{generate_affiliate_code(phone)}

Reply SHARE to get social media templates
    """
    send_message(phone, purchase_msg, preferred_channel)
    
    # Follow-up with affiliate opportunity
    followup_msg = f"""
🤝 *Veteran Support Opportunity*

You can help more veterans by sharing your story:
1. Share your purchase experience
2. Earn 20% commission on referrals
3. Support homeless veterans

Your unique link:
https://digiapp.com/affiliate/{generate_affiliate_code(phone)}

Reply START to begin your mission
    """
    send_message(phone, followup_msg, preferred_channel)

def send_digiuser_flow(phone, name, product_name, preferred_channel='sms'):
    """Send enhanced DigiUser flow with multiple affiliate opportunities."""
    # Welcome message
    welcome_msg = f"""
🎖️ Welcome to the Veteran Creator Network, {name}!

Your product "{product_name}" is live and ready to help others.

📱 *Your Affiliate Links:*
1. Product Share: https://digiapp.com/p/{generate_affiliate_code(phone)}
2. Service Referral: https://digiapp.com/s/{generate_affiliate_code(phone)}
3. Veteran Network: https://digiapp.com/v/{generate_affiliate_code(phone)}

Reply NETWORK to connect with other veterans
    """
    send_message(phone, welcome_msg, preferred_channel)
    
    # Affiliate program details
    affiliate_msg = f"""
🤝 *Triple Impact Affiliate Program*

1. *Product Sales:* Earn 70% on your digital products
2. *Service Referrals:* Get 20% on platform referrals
3. *Veteran Network:* Receive 10% on network growth

Your dashboard: https://digiapp.com/dashboard/{generate_affiliate_code(phone)}

Reply STATS to view your impact
    """
    send_message(phone, affiliate_msg, preferred_channel)
    
    # Veteran support reminder
    support_msg = f"""
🇺🇸 *Mission: End Veteran Homelessness*

Share your success story to inspire others:
https://digiapp.com/story/{generate_affiliate_code(phone)}

Every referral helps a homeless veteran.

Reply STORY to share your journey
    """
    send_message(phone, support_msg, preferred_channel) 