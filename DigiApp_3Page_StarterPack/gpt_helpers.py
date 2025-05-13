import openai
import os
import time
from dotenv import load_dotenv
from functools import lru_cache
import json
from datetime import datetime, timedelta

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Rate limiting
RATE_LIMIT = 3  # requests per minute
last_requests = []

def check_rate_limit():
    """Implement rate limiting for API calls."""
    global last_requests
    now = time.time()
    last_requests = [t for t in last_requests if now - t < 60]
    if len(last_requests) >= RATE_LIMIT:
        time.sleep(60 - (now - last_requests[0]))
    last_requests.append(now)

def safe_gpt_call(prompt, max_tokens=150):
    """Make a safe API call with error handling and rate limiting."""
    try:
        check_rate_limit()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT API Error: {str(e)}")
        return None

@lru_cache(maxsize=100)
def generate_titles(product_summary):
    """Generate 3 potential titles for a product."""
    prompt = f"""As a professional copywriter, suggest 3 catchy, professional titles for this product:
    {product_summary}
    
    Requirements:
    - Each title should be unique and memorable
    - Include relevant keywords
    - Keep each under 60 characters
    - Format as numbered list
    
    Format:
    1. [Title 1]
    2. [Title 2]
    3. [Title 3]"""
    
    result = safe_gpt_call(prompt, max_tokens=100)
    return result.split('\n') if result else ["Title generation failed"]

@lru_cache(maxsize=100)
def write_product_description(product_details):
    """Generate a marketing paragraph for the product."""
    prompt = f"""As a professional copywriter, write a compelling 2-3 sentence marketing description:
    Product Details: {product_details}
    
    Requirements:
    - Focus on benefits and value proposition
    - Use persuasive language
    - Include a call to action
    - Keep it under 200 characters"""
    
    return safe_gpt_call(prompt, max_tokens=150)

@lru_cache(maxsize=100)
def suggest_pricing(product_type, details):
    """Suggest pricing range based on product type and details."""
    prompt = f"""As a pricing expert, suggest an appropriate price range for this {product_type}:
    {details}
    
    Requirements:
    - Consider market standards
    - Factor in value provided
    - Account for production costs
    - Include brief justification
    
    Format:
    Suggested range: $X-$Y
    Justification: [brief explanation]"""
    
    return safe_gpt_call(prompt, max_tokens=100)

@lru_cache(maxsize=100)
def generate_affiliate_email(affiliate_name, product_details, ref_link):
    """Generate custom email copy for affiliate outreach."""
    prompt = f"""Create a professional email template for affiliate outreach:
    Affiliate: {affiliate_name}
    Product: {product_details}
    Referral Link: {ref_link}
    
    Requirements:
    - Professional greeting
    - Clear value proposition
    - Specific benefits for the affiliate
    - Strong call to action
    - Keep it under 300 words"""
    
    return safe_gpt_call(prompt, max_tokens=200)

@lru_cache(maxsize=100)
def create_submission_summary(form_data):
    """Convert form submission into a clean admin summary."""
    prompt = f"""Create a professional summary of this DigiApp submission:
    {form_data}
    
    Requirements:
    - Highlight key information
    - Format as a business report
    - Include action items
    - Note any special requirements
    
    Format:
    SUMMARY
    [Key points]
    
    ACTION ITEMS
    [List of required actions]
    
    NOTES
    [Additional information]"""
    
    return safe_gpt_call(prompt, max_tokens=200)

@lru_cache(maxsize=100)
def generate_landing_page(product_data):
    """Generate HTML content for a landing page."""
    prompt = f"""Create HTML content for a product landing page:
    {product_data}
    
    Requirements:
    - Modern, clean design
    - Clear value proposition
    - Feature highlights
    - Strong call-to-action
    - Mobile-responsive structure
    
    Include:
    - Hero section
    - Features section
    - Benefits section
    - CTA section
    
    Use HTML5 semantic tags and Bootstrap classes."""
    
    return safe_gpt_call(prompt, max_tokens=500)

@lru_cache(maxsize=100)
def enhance_invoice_message(invoice_data):
    """Improve invoice message with professional tone."""
    prompt = f"""Enhance this invoice message to be more professional:
    {invoice_data}
    
    Requirements:
    - Professional tone
    - Clear payment terms
    - Gratitude expression
    - Contact information
    - Keep it concise"""
    
    return safe_gpt_call(prompt, max_tokens=100)

@lru_cache(maxsize=100)
def create_marketplace_listing(title, summary):
    """Generate a one-sentence promotional description."""
    prompt = f"""Create a compelling one-sentence description for marketplace listing:
    Title: {title}
    Summary: {summary}
    
    Requirements:
    - Attention-grabbing
    - Include key benefits
    - Professional tone
    - Under 160 characters
    - Include a call to action"""
    
    return safe_gpt_call(prompt, max_tokens=50)

@lru_cache(maxsize=100)
def generate_social_captions(product_details):
    """Generate social media captions for different platforms."""
    prompt = f"""Create 3 social media captions for this product:
    {product_details}
    
    Requirements:
    - Platform-specific formatting
    - Relevant hashtags
    - Engaging tone
    - Clear value proposition
    - Call to action
    
    Format:
    Instagram: [caption with emojis and hashtags]
    LinkedIn: [professional tone with industry hashtags]
    Twitter: [concise message with trending hashtags]
    
    Keep each under 280 characters."""
    
    return safe_gpt_call(prompt, max_tokens=300)

@lru_cache(maxsize=100)
def get_help_response(user_question):
    """Generate helpful response to user questions."""
    prompt = f"""Provide a clear, simple explanation for this DigiApp question:
    {user_question}
    
    Requirements:
    - Friendly tone
    - Step-by-step instructions
    - Clear examples
    - Actionable advice
    - Keep it under 200 words"""
    
    return safe_gpt_call(prompt, max_tokens=150)

# Cache management
def clear_cache():
    """Clear all cached responses."""
    generate_titles.cache_clear()
    write_product_description.cache_clear()
    suggest_pricing.cache_clear()
    generate_affiliate_email.cache_clear()
    create_submission_summary.cache_clear()
    generate_landing_page.cache_clear()
    enhance_invoice_message.cache_clear()
    create_marketplace_listing.cache_clear()
    generate_social_captions.cache_clear()
    get_help_response.cache_clear() 