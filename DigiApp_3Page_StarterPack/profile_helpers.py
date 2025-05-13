import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Military ranks and roles
MILITARY_RANKS = {
    'EN': {
        'officer': ['General', 'Colonel', 'Major', 'Captain', 'Lieutenant'],
        'enlisted': ['Sergeant Major', 'Master Sergeant', 'Sergeant', 'Corporal', 'Specialist']
    },
    'ES': {
        'officer': ['General', 'Coronel', 'Mayor', 'Capitán', 'Teniente'],
        'enlisted': ['Sargento Mayor', 'Sargento Maestro', 'Sargento', 'Cabo', 'Especialista']
    },
    # Add more languages as needed
}

def create_digibuyer_profile(phone, name, language='EN'):
    """Create a DigiBuyer profile with military theme."""
    profile = {
        'type': 'buyer',
        'phone': phone,
        'name': name,
        'language': language,
        'rank': 'Civilian',
        'joined': datetime.now().isoformat(),
        'purchases': [],
        'affiliate_code': generate_affiliate_code(phone),
        'preferred_channel': 'sms',
        'referrals': 0,
        'earnings': 0,
        'impact_score': 0,
        'veteran_supported': []
    }
    
    # Save profile
    save_profile(profile)
    return profile

def create_digiuser_profile(phone, name, language='EN'):
    """Create a DigiUser profile with military theme."""
    profile = {
        'type': 'seller',
        'phone': phone,
        'name': name,
        'language': language,
        'rank': 'Veteran',
        'joined': datetime.now().isoformat(),
        'products': [],
        'affiliate_code': generate_affiliate_code(phone),
        'preferred_channel': 'sms',
        'earnings': 0,
        'referrals': 0,
        'impact_score': 0,
        'network_size': 0,
        'veterans_helped': 0,
        'success_stories': []
    }
    
    # Save profile
    save_profile(profile)
    return profile

def generate_affiliate_code(phone):
    """Generate a unique affiliate code."""
    return f"VET{phone[-4:]}"

def save_profile(profile):
    """Save user profile to JSON file."""
    profiles_path = 'data/profiles.json'
    profiles = {}
    
    if os.path.exists(profiles_path):
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)
    
    profiles[profile['phone']] = profile
    
    with open(profiles_path, 'w') as f:
        json.dump(profiles, f, indent=2)

def get_profile(phone):
    """Get user profile by phone number."""
    profiles_path = 'data/profiles.json'
    if os.path.exists(profiles_path):
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)
        return profiles.get(phone)
    return None

def update_profile(phone, updates):
    """Update user profile with new information."""
    profile = get_profile(phone)
    if profile:
        profile.update(updates)
        save_profile(profile)
        return profile
    return None

def get_military_rank(profile):
    """Get appropriate military rank based on profile activity."""
    if profile['type'] == 'buyer':
        return 'Civilian'
    
    # Calculate rank based on activity
    if profile.get('earnings', 0) > 1000:
        return MILITARY_RANKS[profile['language']]['officer'][0]
    elif profile.get('earnings', 0) > 500:
        return MILITARY_RANKS[profile['language']]['officer'][1]
    elif profile.get('referrals', 0) > 10:
        return MILITARY_RANKS[profile['language']]['enlisted'][0]
    elif profile.get('referrals', 0) > 5:
        return MILITARY_RANKS[profile['language']]['enlisted'][1]
    else:
        return MILITARY_RANKS[profile['language']]['enlisted'][-1]

def update_impact_score(phone, points):
    """Update user's impact score and rank."""
    profile = get_profile(phone)
    if profile:
        profile['impact_score'] = profile.get('impact_score', 0) + points
        profile['rank'] = get_military_rank(profile)
        save_profile(profile)
        return profile
    return None

def add_veteran_supported(buyer_phone, veteran_phone):
    """Record veteran support in buyer's profile."""
    profile = get_profile(buyer_phone)
    if profile and profile['type'] == 'buyer':
        if 'veteran_supported' not in profile:
            profile['veteran_supported'] = []
        profile['veteran_supported'].append(veteran_phone)
        update_impact_score(buyer_phone, 10)  # Award points for supporting veterans
        save_profile(profile)
        return profile
    return None

def add_success_story(seller_phone, story):
    """Add success story to seller's profile."""
    profile = get_profile(seller_phone)
    if profile and profile['type'] == 'seller':
        if 'success_stories' not in profile:
            profile['success_stories'] = []
        profile['success_stories'].append({
            'story': story,
            'date': datetime.now().isoformat()
        })
        update_impact_score(seller_phone, 20)  # Award points for sharing story
        save_profile(profile)
        return profile
    return None

def generate_profile_summary(profile):
    """Generate a military-themed profile summary with impact metrics."""
    rank = get_military_rank(profile)
    
    if profile['type'] == 'buyer':
        return f"""
🎖️ {rank} {profile['name']}
📱 {profile['phone']}
🌐 {profile['language']}
📅 Joined: {profile['joined']}
🛍️ Purchases: {len(profile.get('purchases', []))}
🤝 Veterans Supported: {len(profile.get('veteran_supported', []))}
💪 Impact Score: {profile.get('impact_score', 0)}
💰 Earnings: ${profile.get('earnings', 0)}
        """
    else:
        return f"""
🎖️ {rank} {profile['name']}
📱 {profile['phone']}
🌐 {profile['language']}
📅 Joined: {profile['joined']}
💰 Earnings: ${profile.get('earnings', 0)}
🤝 Referrals: {profile.get('referrals', 0)}
🛍️ Products: {len(profile.get('products', []))}
💪 Impact Score: {profile.get('impact_score', 0)}
👥 Network Size: {profile.get('network_size', 0)}
🇺🇸 Veterans Helped: {profile.get('veterans_helped', 0)}
        """

def update_earnings(phone, amount):
    """Update user earnings and rank."""
    profile = get_profile(phone)
    if profile and profile['type'] == 'seller':
        profile['earnings'] = profile.get('earnings', 0) + amount
        profile['rank'] = get_military_rank(profile)
        save_profile(profile)
        return profile
    return None

def update_referrals(phone):
    """Update user referrals and rank."""
    profile = get_profile(phone)
    if profile and profile['type'] == 'seller':
        profile['referrals'] = profile.get('referrals', 0) + 1
        profile['rank'] = get_military_rank(profile)
        save_profile(profile)
        return profile
    return None 