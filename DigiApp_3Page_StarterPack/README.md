# DigiApp - Veteran Digital Products Platform

A platform empowering veterans to create and sell digital products, providing sustainable income opportunities.

## Features

- Digital product marketplace for veterans
- SMS and WhatsApp communication
- Multi-language support
- Affiliate program
- Tiered product updates
- Veteran support groups

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/digiapp.git
cd digiapp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
APP_URL=http://localhost:5000
BASE_URL=https://your-app.onrender.com

# File Storage
UPLOAD_FOLDER=uploads
DATA_FOLDER=data
INVOICE_FOLDER=invoices

# Payment Configuration
PAYPAL_ME_LINK=https://paypal.me/Apps4Mybiz/5
STRIPE_TIER1_LINK=your_stripe_tier1_link
STRIPE_TIER2_LINK=your_stripe_tier2_link
STRIPE_TIER3_LINK=your_stripe_tier3_link

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=noreply@your-domain.com
```

6. Create required directories:
```bash
mkdir -p uploads data invoices
```

7. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Environment Variables

### Required Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number
- `SECRET_KEY`: Flask secret key
- `PAYPAL_ME_LINK`: Your PayPal.me link

### Optional Variables

- `FLASK_ENV`: Development environment (default: development)
- `APP_URL`: Local development URL (default: http://localhost:5000)
- `BASE_URL`: Production URL
- `SENDGRID_API_KEY`: SendGrid API key for email
- `SENDER_EMAIL`: Email address for sending notifications

## Security Notes

1. Never commit the `.env` file to version control
2. Keep your API keys secure
3. Regularly rotate your secret keys
4. Use HTTPS in production
5. Monitor your API usage

## Project Structure

```
digiapp/
├── app.py              # Main Flask application
├── gpt_helpers.py      # GPT integration functions
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── styles.css     # CSS styles
│   └── script.js      # JavaScript
├── templates/         # HTML templates
│   ├── index.html     # Home page
│   ├── landing.html   # Services page
│   └── thankyou.html  # Confirmation page
├── uploads/           # User uploads
├── data/             # Data storage
└── invoices/         # Generated invoices
```

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - `OPENAI_API_KEY`
     - `SENDGRID_API_KEY`
     - `SENDER_EMAIL`

4. Deploy!

## Development

- Flask 3.0.0
- OpenAI GPT-3.5
- SendGrid for emails
- Pandas for data handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 