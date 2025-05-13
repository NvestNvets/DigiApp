import os
import json
from datetime import datetime
from jinja2 import Template
import openai
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

class LandingPageGenerator:
    def __init__(self):
        self.templates_dir = 'templates'
        self.landings_dir = 'static/landings'
        self.ensure_directories()
        
        # Define tier limits
        self.tier_limits = {
            'Launch Pad': {
                'updates_per_year': 3,
                'products_limit': 1,
                'features': ['Basic landing page', 'SMS notifications', 'Affiliate tracking']
            },
            'Brand Booster': {
                'updates_per_year': 6,
                'products_limit': 3,
                'features': ['Enhanced landing page', 'WhatsApp support', 'Priority updates']
            },
            'Flagship': {
                'updates_per_year': float('inf'),
                'products_limit': float('inf'),
                'features': ['Premium landing page', '24/7 support', 'Custom domain']
            },
            'Support Group': {
                'updates_per_year': 12,
                'products_limit': 5,
                'features': ['Premium features', 'Community support', 'Priority assistance']
            }
        }
        
    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.landings_dir, exist_ok=True)
    
    def generate_landing_page(self, creator_data, product_data):
        """Generate a personalized landing page for a veteran's product."""
        # Load base template
        with open(os.path.join(self.templates_dir, 'product_landing.html'), 'r') as f:
            template = Template(f.read())
        
        # Generate unique landing page ID
        landing_id = f"{creator_data['phone'][-4:]}-{datetime.now().strftime('%Y%m%d')}"
        
        # Get tier information
        tier = creator_data.get('tier', 'Launch Pad')
        is_support_group = creator_data.get('is_support_group', False)
        is_verified = creator_data.get('is_verified', False)
        
        # Get mission statistics
        mission_stats = self.get_mission_statistics()
        
        # Get supporters if support group
        supporters = []
        if is_support_group:
            supporters = self.get_supporters(creator_data['phone'])
        
        # Prepare template data
        template_data = {
            'creator_name': creator_data['name'],
            'product_name': product_data['name'],
            'product_description': product_data['description'],
            'price': product_data['price'],
            'payment_link': product_data.get('payment_link'),
            'creator_affiliate_link': f"https://digiapp.com/affiliate/{creator_data['affiliate_code']}",
            'veteran_affiliate_link': self.get_veteran_affiliate_link(),
            'service_affiliate_link': f"https://digiapp.com/service/{creator_data['affiliate_code']}",
            'landing_id': landing_id,
            'military_rank': creator_data.get('rank', 'Veteran'),
            'success_stories': self.get_success_stories(),
            'product_image': product_data.get('image_url', '/static/default-product.jpg'),
            'is_support_group': is_support_group,
            'is_verified': is_verified,
            'supporters': supporters,
            'veterans_helped': mission_stats['veterans_helped'],
            'products_created': mission_stats['products_created'],
            'community_impact': mission_stats['community_impact']
        }
        
        # Render template
        landing_html = template.render(**template_data)
        
        # Save landing page
        landing_path = os.path.join(self.landings_dir, f"{landing_id}.html")
        with open(landing_path, 'w') as f:
            f.write(landing_html)
        
        # Update creator's profile
        self.update_creator_landings(creator_data['phone'], landing_id, product_data)
        
        return {
            'landing_id': landing_id,
            'landing_url': f"/landings/{landing_id}.html",
            'product_data': product_data
        }
    
    def get_supporters(self, phone):
        """Get list of supporters for a veteran."""
        try:
            with open('data/support_groups.json', 'r') as f:
                support_groups = json.load(f)
            
            if phone in support_groups:
                return support_groups[phone].get('supporters', [])
            return []
        except Exception as e:
            print(f"Error getting supporters: {e}")
            return []
    
    def verify_veteran(self, phone, verification_data):
        """Verify a veteran's status using ID.me or eBenefits."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if phone in profiles:
                profile = profiles[phone]
                profile['is_verified'] = True
                profile['verification_date'] = datetime.now().isoformat()
                profile['verification_method'] = verification_data.get('method')
                profile['verification_id'] = verification_data.get('id')
                
                with open('data/profiles.json', 'w') as f:
                    json.dump(profiles, f, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"Error verifying veteran: {e}")
            return False
    
    def apply_support_group(self, phone):
        """Apply for support group status."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if phone in profiles and profiles[phone].get('is_verified'):
                profile = profiles[phone]
                profile['is_support_group'] = True
                profile['support_group_date'] = datetime.now().isoformat()
                profile['tier'] = 'Support Group'
                
                # Initialize support group data
                with open('data/support_groups.json', 'r') as f:
                    support_groups = json.load(f)
                
                support_groups[phone] = {
                    'supporters': [],
                    'start_date': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                with open('data/support_groups.json', 'w') as f:
                    json.dump(support_groups, f, indent=2)
                
                with open('data/profiles.json', 'w') as f:
                    json.dump(profiles, f, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"Error applying for support group: {e}")
            return False
    
    def add_supporter(self, phone, supporter_data):
        """Add a supporter to a veteran's support group."""
        try:
            with open('data/support_groups.json', 'r') as f:
                support_groups = json.load(f)
            
            if phone in support_groups:
                support_groups[phone]['supporters'].append({
                    'name': supporter_data['name'],
                    'join_date': datetime.now().isoformat(),
                    'products_bought': supporter_data.get('products_bought', 0)
                })
                
                with open('data/support_groups.json', 'w') as f:
                    json.dump(support_groups, f, indent=2)
                
                return True
            return False
        except Exception as e:
            print(f"Error adding supporter: {e}")
            return False
    
    def get_mission_statistics(self):
        """Get mission statistics for the landing page."""
        try:
            with open('data/mission_stats.json', 'r') as f:
                stats = json.load(f)
        except FileNotFoundError:
            stats = {
                'veterans_helped': 0,
                'products_created': 0,
                'community_impact': '$0'
            }
        return stats
    
    def get_veteran_affiliate_link(self):
        """Get a random veteran's affiliate link to promote."""
        try:
            with open('data/affiliates.json', 'r') as f:
                affiliates = json.load(f)
            
            # Filter active veterans with success stories
            active_veterans = [
                aff for aff in affiliates.values()
                if aff.get('type') == 'seller' and aff.get('success_stories')
            ]
            
            if active_veterans:
                veteran = random.choice(active_veterans)
                return f"https://digiapp.com/veteran/{veteran['affiliate_code']}"
        except Exception as e:
            print(f"Error getting veteran affiliate link: {e}")
        
        return "https://digiapp.com/veterans"
    
    def get_success_stories(self):
        """Get relevant success stories for the landing page."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            stories = []
            for profile in profiles.values():
                if profile.get('type') == 'seller' and profile.get('success_stories'):
                    stories.extend(profile['success_stories'])
            
            return random.sample(stories, min(3, len(stories)))
        except Exception as e:
            print(f"Error getting success stories: {e}")
            return []
    
    def update_creator_landings(self, phone, landing_id, product_data):
        """Update creator's profile with new landing page."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if phone in profiles:
                profile = profiles[phone]
                if 'landings' not in profile:
                    profile['landings'] = []
                
                profile['landings'].append({
                    'id': landing_id,
                    'created_at': datetime.now().isoformat(),
                    'product_data': product_data
                })
                
                with open('data/profiles.json', 'w') as f:
                    json.dump(profiles, f, indent=2)
        except Exception as e:
            print(f"Error updating creator landings: {e}")
    
    def can_update_product(self, phone, tier):
        """Check if creator can update their product based on tier."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if phone in profiles:
                profile = profiles[phone]
                current_year = datetime.now().year
                
                # Count updates this year
                updates_this_year = sum(
                    1 for landing in profile.get('landings', [])
                    if datetime.fromisoformat(landing['created_at']).year == current_year
                )
                
                # Get tier limits
                tier_limit = self.tier_limits.get(tier, self.tier_limits['Launch Pad'])
                return updates_this_year < tier_limit['updates_per_year']
            
            return False
        except Exception as e:
            print(f"Error checking product update eligibility: {e}")
            return False
    
    def get_tier_features(self, tier):
        """Get features available for a specific tier."""
        return self.tier_limits.get(tier, self.tier_limits['Launch Pad'])['features']
    
    def can_add_product(self, phone, tier):
        """Check if creator can add a new product based on tier."""
        try:
            with open('data/profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if phone in profiles:
                profile = profiles[phone]
                current_products = len(profile.get('landings', []))
                
                # Get tier limits
                tier_limit = self.tier_limits.get(tier, self.tier_limits['Launch Pad'])
                return current_products < tier_limit['products_limit']
            
            return True  # New creators can add their first product
        except Exception as e:
            print(f"Error checking product addition eligibility: {e}")
            return False 