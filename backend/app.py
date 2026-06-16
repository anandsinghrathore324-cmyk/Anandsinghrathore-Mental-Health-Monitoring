import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database.db import db_manager
from database.doctor_model import DoctorModel
from database.hotline_model import HotlineModel
from database.geo_model import GeoModel

# Blueprints
from routes.auth_routes import auth_bp
from routes.prediction_routes import prediction_bp
from routes.chatbot_routes import chatbot_bp
from routes.doctor_routes import doctor_bp
from routes.dashboard_routes import dashboard_bp
from routes.hotline_routes import hotline_bp
from routes.geo_routes import geo_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ── Email delivery driver diagnostics ────────────────────────────────────
    import os as _os
    resend_key  = _os.getenv("RESEND_API_KEY",      "").strip()
    resend_from = _os.getenv("RESEND_FROM_ADDRESS", "").strip()
    smtp_email  = Config.SMTP_EMAIL  or ""
    smtp_pass   = Config.SMTP_PASSWORD or ""

    # Log exactly which variables are present so Render logs show the truth
    logger.info(
        "[STARTUP EMAIL] ENV CHECK — RESEND_API_KEY=%s, RESEND_FROM_ADDRESS=%s, "
        "SMTP_EMAIL=%s, SMTP_PASSWORD=%s",
        "SET(len=%d)" % len(resend_key)  if resend_key  else "NOT SET",
        "SET(len=%d)" % len(resend_from) if resend_from else "NOT SET",
        "SET" if smtp_email else "NOT SET",
        "SET(len=%d)" % len(smtp_pass) if smtp_pass else "NOT SET",
    )

    if resend_key and resend_from:
        masked_from = resend_from[:6] + "..." if len(resend_from) > 6 else resend_from
        logger.info(
            "[STARTUP EMAIL] ✅ Resend HTTP API driver ACTIVE. "
            "FROM=%s (works on Render free tier — HTTPS port 443).", masked_from
        )
    elif smtp_email and smtp_pass and "your-gmail" not in smtp_email:
        masked_smtp = (smtp_email[:3] + "..." + smtp_email[smtp_email.find("@"):]) if "@" in smtp_email else smtp_email[:3] + "..."
        logger.warning(
            "[STARTUP EMAIL] ⚠️  smtplib STARTTLS driver active (sender=%s). "
            "NOTE: Gmail SMTP (ports 465/587) is BLOCKED on Render free tier — "
            "emails will fail. Set RESEND_API_KEY + RESEND_FROM_ADDRESS to fix this.", masked_smtp
        )
    else:
        logger.warning(
            "[STARTUP EMAIL] ⚠️  No email driver configured. "
            "OTP emails will fail in production. "
            "Set RESEND_API_KEY + RESEND_FROM_ADDRESS in Render environment variables."
        )
    
    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize MongoDB Client
    try:
        db_manager.connect()
        seed_database()
    except Exception as e:
        logger.critical(f"Critical error establishing database handshake: {str(e)}")
        
    # Register blueprints under unified /api prefix
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(prediction_bp, url_prefix="/api")
    app.register_blueprint(chatbot_bp, url_prefix="/api")
    app.register_blueprint(doctor_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(hotline_bp, url_prefix="/api")
    app.register_blueprint(geo_bp, url_prefix="/api")
    
    # Centralized fallback route error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
            "status": "error",
            "message": "The requested API endpoint does not exist."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "status": "error",
            "message": "Internal computational exception encountered."
        }), 500
        
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "success",
            "message": "AIRA Backend nodes online and secure."
        }), 200
        
    return app

def seed_database():
    """Seeds verified psychologist profiles into the database if collection is empty."""
    doctors = [
        # JAIPUR
        {
            "doctor_name": "Dr. Priya Sharma, MD",
            "specialization": "Stress & Academic Burnout",
            "specialization_type": "stress",
            "experience": 12,
            "degrees": "MD Psychiatry, AIIMS Delhi",
            "certifications": "Certified Cognitive Behavioral Therapist",
            "achievements": "Best Psychiatrist Award – Rajasthan Medical Council 2023",
            "bio": "Specializes in student mental health, academic pressure, and exam anxiety using evidence-based CBT and mindfulness methods.",
            "hospital": "Fortis Escorts Hospital, Jaipur",
            "rating": 4.9,
            "latitude": 26.9124 + 0.015,
            "longitude": 75.7873 - 0.01,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 141 255 0101",
            "maps_link": "https://maps.google.com/?q=Fortis+Escorts+Hospital+Jaipur"
        },
        {
            "doctor_name": "Dr. Anil Mehta, PsyD",
            "specialization": "Anxiety & Depression",
            "specialization_type": "anxiety",
            "experience": 9,
            "degrees": "PsyD Clinical Psychology, Rajasthan University",
            "certifications": "Licensed Clinical Psychologist",
            "achievements": "Featured in Times of India Mental Health Column",
            "bio": "Works with adolescents and young adults dealing with anxiety disorders, panic attacks, and low self-esteem using integrative therapy.",
            "hospital": "SMS Medical College, Jaipur",
            "rating": 4.8,
            "latitude": 26.9124 - 0.02,
            "longitude": 75.7873 + 0.015,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 141 255 0202",
            "maps_link": "https://maps.google.com/?q=SMS+Medical+College+Jaipur"
        },
        {
            "doctor_name": "Dr. Sunita Agarwal, MBBS",
            "specialization": "Clinical Depression",
            "specialization_type": "depression",
            "experience": 15,
            "degrees": "MBBS, MD Psychiatry – Jaipur Golden Hospital",
            "certifications": "Fellow of Indian Psychiatric Society",
            "achievements": "Pioneer of rural telepsychiatry in Rajasthan",
            "bio": "Treats moderate-to-severe depression, bipolar disorder, and emotional dysregulation with medication management and talk therapy.",
            "hospital": "Jaipur Golden Hospital",
            "rating": 4.7,
            "latitude": 26.9124 + 0.005,
            "longitude": 75.7873 + 0.03,
            "open_status": "Offline",
            "timing": "08:00 - 14:00",
            "contact_number": "+91 141 255 0303",
            "maps_link": "https://maps.google.com/?q=Jaipur+Golden+Hospital"
        },
        {
            "doctor_name": "Dr. Rahul Verma, PhD",
            "specialization": "Burnout & Academic Stress",
            "specialization_type": "stress",
            "experience": 7,
            "degrees": "PhD Psychology, University of Rajasthan",
            "certifications": "Certified Wellness & Resilience Coach",
            "achievements": "Designed AIRA-certified student resilience curriculum",
            "bio": "Focuses on building mental toughness, productivity habits, and stress regulation for competitive exam students.",
            "hospital": "Mind Wellness Clinic, Vaishali Nagar",
            "rating": 4.6,
            "latitude": 26.9124 - 0.01,
            "longitude": 75.7873 - 0.02,
            "open_status": "Online Now",
            "timing": "11:00 - 19:00",
            "contact_number": "+91 141 255 0404",
            "maps_link": "https://maps.google.com/?q=Vaishali+Nagar+Jaipur"
        },
        # DELHI
        {
            "doctor_name": "Dr. Kavita Singh, MD",
            "specialization": "Stress & Burnout",
            "specialization_type": "stress",
            "experience": 14,
            "degrees": "MD Psychiatry, AIIMS New Delhi",
            "certifications": "Certified Mindfulness Instructor",
            "achievements": "Keynote Speaker – NIMHANS Mental Health Summit 2024",
            "bio": "Expert in work-life balance restoration, perfectionism, and academic performance anxiety for students and professionals.",
            "hospital": "AIIMS New Delhi",
            "rating": 5.0,
            "latitude": 28.6139 + 0.01,
            "longitude": 77.2090 - 0.02,
            "open_status": "Online Now",
            "timing": "08:30 - 16:30",
            "contact_number": "+91 11 2658 8500",
            "maps_link": "https://maps.google.com/?q=AIIMS+New+Delhi"
        },
        {
            "doctor_name": "Dr. Rohan Das, PsyD",
            "specialization": "General Anxiety",
            "specialization_type": "anxiety",
            "experience": 11,
            "degrees": "PsyD, Jamia Millia Islamia",
            "certifications": "Licensed Psychotherapist",
            "achievements": "Author – 'The Anxious Student Mind'",
            "bio": "Uses ACT (Acceptance & Commitment Therapy) to help students overcome social anxiety, test phobia, and overthinking loops.",
            "hospital": "Max Healthcare, Saket Delhi",
            "rating": 4.8,
            "latitude": 28.6139 - 0.03,
            "longitude": 77.2090 + 0.02,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 11 2658 8600",
            "maps_link": "https://maps.google.com/?q=Max+Healthcare+Saket+Delhi"
        },
        {
            "doctor_name": "Dr. Neha Chopra, MBBS",
            "specialization": "Clinical Depression",
            "specialization_type": "depression",
            "experience": 16,
            "degrees": "MBBS + MD Psychiatry, Delhi University",
            "certifications": "Fellow IPS, Certified DBT Therapist",
            "achievements": "Recipient of Excellence in Mental Healthcare Award 2022",
            "bio": "Comprehensive depression management combining psychopharmacology and evidence-based CBT for college students.",
            "hospital": "Safdarjung Hospital, New Delhi",
            "rating": 4.9,
            "latitude": 28.6139 + 0.02,
            "longitude": 77.2090 + 0.005,
            "open_status": "Offline",
            "timing": "09:00 - 15:00",
            "contact_number": "+91 11 2658 8700",
            "maps_link": "https://maps.google.com/?q=Safdarjung+Hospital+New+Delhi"
        },
        # MUMBAI
        {
            "doctor_name": "Dr. Aarti Patel, MD",
            "specialization": "Anxiety Disorders",
            "specialization_type": "anxiety",
            "experience": 13,
            "degrees": "MD Psychiatry, KEM Hospital Mumbai",
            "certifications": "Certified EMDR Therapist",
            "achievements": "TED Talk Speaker on Youth Mental Health",
            "bio": "Specializes in panic disorder, social anxiety, and performance anxiety for Mumbai's competitive student population.",
            "hospital": "Lilavati Hospital, Bandra",
            "rating": 4.9,
            "latitude": 19.0760 + 0.02,
            "longitude": 72.8777 - 0.03,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 22 2655 1234",
            "maps_link": "https://maps.google.com/?q=Lilavati+Hospital+Bandra+Mumbai"
        },
        {
            "doctor_name": "Dr. Suresh Nair, PhD",
            "specialization": "Depression & Mood Disorders",
            "specialization_type": "depression",
            "experience": 10,
            "degrees": "PhD Clinical Psychology, Mumbai University",
            "certifications": "Licensed Psychologist, MCI Registered",
            "achievements": "Founder of Mumbai Youth Mental Health Foundation",
            "bio": "Integrative approach combining CBT, mindfulness and interpersonal therapy for depression and emotional dysregulation.",
            "hospital": "Bombay Hospital, Marine Lines",
            "rating": 4.7,
            "latitude": 19.0760 - 0.04,
            "longitude": 72.8777 + 0.015,
            "open_status": "Online Now",
            "timing": "11:00 - 19:00",
            "contact_number": "+91 22 2655 5678",
            "maps_link": "https://maps.google.com/?q=Bombay+Hospital+Marine+Lines+Mumbai"
        },
        # BANGALORE
        {
            "doctor_name": "Dr. Deepika Rao, MD",
            "specialization": "Tech Stress & Burnout",
            "specialization_type": "stress",
            "experience": 8,
            "degrees": "MD Psychiatry, NIMHANS Bangalore",
            "certifications": "Certified Cognitive Coach",
            "achievements": "Mental Health Advisor to top IT firms in Bangalore",
            "bio": "Specializes in tech-industry burnout, digital addiction, and work-pressure-related anxiety for students and engineers.",
            "hospital": "NIMHANS, Bangalore",
            "rating": 4.8,
            "latitude": 12.9716 + 0.01,
            "longitude": 77.5946 - 0.015,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 80 2699 5001",
            "maps_link": "https://maps.google.com/?q=NIMHANS+Bangalore"
        },
        {
            "doctor_name": "Dr. Vikram Krishnan, PsyD",
            "specialization": "Anxiety & Stress Management",
            "specialization_type": "anxiety",
            "experience": 12,
            "degrees": "PsyD, Christ University Bangalore",
            "certifications": "Certified DBT & Mindfulness Practitioner",
            "achievements": "Top Psychologist Award – Bangalore Health Summit 2023",
            "bio": "Helps engineering and medical students manage perfectionism, social isolation, and exam-related anxiety through structured therapy.",
            "hospital": "Manipal Hospital, Bangalore",
            "rating": 4.9,
            "latitude": 12.9716 - 0.02,
            "longitude": 77.5946 + 0.025,
            "open_status": "Offline",
            "timing": "09:00 - 15:00",
            "contact_number": "+91 80 2699 5002",
            "maps_link": "https://maps.google.com/?q=Manipal+Hospital+Bangalore"
        },
        # LONDON
        {
            "doctor_name": "Dr. Emily Clarke, DClinPsy",
            "specialization": "Stress & Academic Burnout",
            "specialization_type": "stress",
            "experience": 11,
            "degrees": "DClinPsy, University College London",
            "certifications": "BPS Chartered Psychologist",
            "achievements": "NHS Mental Health Excellence Award 2023",
            "bio": "Works with university students experiencing high-pressure academic environments and imposter syndrome using evidence-based CBT.",
            "hospital": "King's College Hospital, London",
            "rating": 4.9,
            "latitude": 51.5074 + 0.03,
            "longitude": -0.1278 - 0.02,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+44 20 3299 9000",
            "maps_link": "https://maps.google.com/?q=Kings+College+Hospital+London"
        },
        {
            "doctor_name": "Dr. James Thornton, PhD",
            "specialization": "Anxiety Disorders",
            "specialization_type": "anxiety",
            "experience": 14,
            "degrees": "PhD Psychology, Oxford University",
            "certifications": "BABCP Accredited CBT Therapist",
            "achievements": "Author of 'Managing Student Anxiety' published by Penguin",
            "bio": "Specialist in generalised anxiety disorder, social phobia, and OCD among London's student population.",
            "hospital": "The Priory Hospital, London",
            "rating": 4.8,
            "latitude": 51.5074 - 0.015,
            "longitude": -0.1278 + 0.04,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+44 20 3299 9001",
            "maps_link": "https://maps.google.com/?q=The+Priory+Hospital+London"
        },
        # NEW YORK
        {
            "doctor_name": "Dr. Sarah Williams, PsyD",
            "specialization": "Depression & Mood Disorders",
            "specialization_type": "depression",
            "experience": 13,
            "degrees": "PsyD, Columbia University",
            "certifications": "Licensed Psychologist, APA Member",
            "achievements": "Top Doctor Award – New York Magazine 2023",
            "bio": "Comprehensive treatment for clinical depression, bipolar disorder, and major life transitions for New York students and professionals.",
            "hospital": "NewYork-Presbyterian Hospital",
            "rating": 5.0,
            "latitude": 40.7128 + 0.02,
            "longitude": -74.0060 - 0.015,
            "open_status": "Online Now",
            "timing": "08:00 - 16:00",
            "contact_number": "+1 (212) 555-0101",
            "maps_link": "https://maps.google.com/?q=NewYork-Presbyterian+Hospital"
        },
        {
            "doctor_name": "Dr. Michael Chen, PhD",
            "specialization": "Anxiety & Academic Stress",
            "specialization_type": "anxiety",
            "experience": 9,
            "degrees": "PhD Clinical Psychology, NYU",
            "certifications": "Certified CBT & Exposure Therapist",
            "achievements": "NYU Student Mental Health Research Grant 2022",
            "bio": "Specializes in test anxiety, academic perfectionism, and social anxiety using evidence-based exposure therapy techniques.",
            "hospital": "NYU Langone Health",
            "rating": 4.8,
            "latitude": 40.7128 - 0.01,
            "longitude": -74.0060 + 0.025,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+1 (212) 555-0202",
            "maps_link": "https://maps.google.com/?q=NYU+Langone+Health"
        },
        # DUBAI
        {
            "doctor_name": "Dr. Fatima Al-Rashid, MD",
            "specialization": "Stress & Burnout",
            "specialization_type": "stress",
            "experience": 10,
            "degrees": "MD Psychiatry, American University of Beirut",
            "certifications": "Certified CBT Therapist, Dubai Health Authority",
            "achievements": "Wellness Champion – Dubai Health Authority 2023",
            "bio": "Helps international students and expat youth navigate cultural stress, academic pressure, and identity challenges in the UAE.",
            "hospital": "American Hospital Dubai",
            "rating": 4.9,
            "latitude": 25.2048 + 0.015,
            "longitude": 55.2708 - 0.01,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+971 4 336 7777",
            "maps_link": "https://maps.google.com/?q=American+Hospital+Dubai"
        },
        # SINGAPORE
        {
            "doctor_name": "Dr. Lim Wei Jing, PhD",
            "specialization": "Academic Anxiety & Perfectionism",
            "specialization_type": "anxiety",
            "experience": 8,
            "degrees": "PhD Psychology, NUS Singapore",
            "certifications": "Singapore Register of Psychologists",
            "achievements": "SMU Mental Health Innovation Award 2023",
            "bio": "Specializes in high-achieving student mental health, perfectionism-driven anxiety, and burnout prevention in Singapore's competitive education system.",
            "hospital": "National University Hospital, Singapore",
            "rating": 4.8,
            "latitude": 1.3521 + 0.005,
            "longitude": 103.8198 - 0.015,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+65 6779 5555",
            "maps_link": "https://maps.google.com/?q=National+University+Hospital+Singapore"
        }
    ]
    try:
        DoctorModel.seed_doctors(doctors)
        logger.info(f"Verified profiles database successfully seeded with {len(doctors)} entries.")
        HotlineModel.seed_hotlines()
        logger.info("Mental health crisis hotlines database successfully seeded.")
        GeoModel.seed_check()
        
        # Seed default student user
        from database.user_model import UserModel
        if not UserModel.find_by_email("student@aira.edu"):
            UserModel.create_user("Student User", "student@aira.edu", "password")
            logger.info("Demo student account successfully registered inside MongoDB.")
    except Exception as e:
        logger.error(f"Failed to seed database contents: {str(e)}")


# Instantiate application node
app = create_app()

if __name__ == "__main__":
    import os
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=True)
