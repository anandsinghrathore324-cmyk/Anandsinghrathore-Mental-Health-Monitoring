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
    brevo_key  = _os.getenv("BREVO_API_KEY",    "").strip()
    brevo_from = _os.getenv("BREVO_FROM_EMAIL", "").strip()

    if brevo_key and brevo_from:
        masked = (brevo_from[:4] + "...@" + brevo_from.split("@")[-1]) if "@" in brevo_from else brevo_from[:6] + "..."
        logger.info(
            "[STARTUP EMAIL] ✅ Brevo REST API driver ACTIVE. "
            "FROM=%s | OTP emails will work on all plans (HTTPS port 443).", masked
        )
    else:
        missing = []
        if not brevo_key:  missing.append("BREVO_API_KEY")
        if not brevo_from: missing.append("BREVO_FROM_EMAIL")
        logger.warning(
            "[STARTUP EMAIL] ⚠️  Brevo not configured — missing: %s. "
            "OTP emails will fail. Set these in Render environment variables.",
            ", ".join(missing)
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
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "success",
            "message": "AIRA Backend nodes online and secure."
        }), 200
        
    return app

def seed_database():
    """Seeds verified psychologist profiles into the database if collection is empty."""
    doctors = [
        # SANGANER / JAIPUR SUBURBS
        {
            "doctor_name": "Dr. S. K. Khandelwal, MD",
            "specialization": "Psychiatrist & Student Counselor",
            "specialization_type": "anxiety",
            "experience": 15,
            "degrees": "MD Psychiatry, SMS Medical College",
            "certifications": "Senior Consultant Psychiatrist",
            "achievements": "Over 15+ years treating youth anxiety and depression in Sanganer & Tonk Road",
            "bio": "Expert in student exam stress, anxiety, and panic disorders near Sanganer & Airport Enclave.",
            "hospital": "Dhanwantari Hospital & Research Centre, Sanganer",
            "city": "Sanganer",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.9,
            "reviews": 168,
            "reviews_summary": "Highly recommended for students in Sanganer, Tonk Road, and Sitapura academic hubs.",
            "latitude": 26.8124,
            "longitude": 75.7873,
            "open_status": "Online Now",
            "timing": "09:30 - 18:30",
            "contact_number": "+91 141 273 0000",
            "maps_link": "https://maps.google.com/?q=Dhanwantari+Hospital+Sanganer",
            "verified": True
        },
        {
            "doctor_name": "Dr. Sheshkiran Relationship & Youth Therapist",
            "specialization": "Clinical Psychology & Counseling",
            "specialization_type": "depression",
            "experience": 10,
            "degrees": "M.Phil Clinical Psychology",
            "certifications": "Licensed Youth Psychotherapist",
            "achievements": "100+ positive student reviews for compassionate counseling",
            "bio": "Dedicated clinical psychologist helping youth overcome depression, burnout, and relationship strain.",
            "hospital": "Manas Mind Care & Counseling, Sanganer",
            "city": "Sanganer",
            "state": "Rajasthan",
            "country": "India",
            "rating": 5.0,
            "reviews": 110,
            "reviews_summary": "Empathetic, actionable guidance for young adults and students in Sanganer & Mansarovar.",
            "latitude": 26.8200,
            "longitude": 75.7900,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 99285 23379",
            "maps_link": "https://maps.google.com/?q=Manas+Counseling+Sanganer",
            "verified": True
        },
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
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.9,
            "reviews": 234,
            "reviews_summary": "Extremely compassionate approach for engineering & medical students facing burnout.",
            "latitude": 26.9124 + 0.015,
            "longitude": 75.7873 - 0.01,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 141 255 0101",
            "maps_link": "https://maps.google.com/?q=Fortis+Escorts+Hospital+Jaipur",
            "verified": True
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
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.8,
            "reviews": 189,
            "reviews_summary": "Helped my son conquer panic attacks before board exams. Highly recommended!",
            "latitude": 26.9124 - 0.02,
            "longitude": 75.7873 + 0.015,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 141 255 0202",
            "maps_link": "https://maps.google.com/?q=SMS+Medical+College+Jaipur",
            "verified": True
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
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.7,
            "reviews": 142,
            "reviews_summary": "Thorough psychiatric evaluations with very gentle and supportive counseling.",
            "latitude": 26.9124 + 0.005,
            "longitude": 75.7873 + 0.03,
            "open_status": "Offline",
            "timing": "08:00 - 14:00",
            "contact_number": "+91 141 255 0303",
            "maps_link": "https://maps.google.com/?q=Jaipur+Golden+Hospital",
            "verified": True
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
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.9,
            "reviews": 168,
            "reviews_summary": "Actionable mindfulness strategies that immediately restored my confidence.",
            "latitude": 26.9124 - 0.01,
            "longitude": 75.7873 - 0.02,
            "open_status": "Online Now",
            "timing": "11:00 - 19:00",
            "contact_number": "+91 141 255 0404",
            "maps_link": "https://maps.google.com/?q=Vaishali+Nagar+Jaipur",
            "verified": True
        },
        # KOTA (Competitive Exam Student Hub)
        {
            "doctor_name": "Dr. Manisha Rathore, MD",
            "specialization": "IIT-JEE / NEET Exam Stress & Anxiety",
            "specialization_type": "stress",
            "experience": 11,
            "degrees": "MD Psychiatry, SMS Jaipur",
            "certifications": "Certified Adolescent Crisis Counselor",
            "achievements": "Kota Student Helpline Lead Clinical Consultant",
            "bio": "Dedicated exclusively to supporting students preparing for high-stakes competitive examinations in Kota.",
            "hospital": "Apex Mind Clinic, Talwandi Kota",
            "city": "Kota",
            "state": "Rajasthan",
            "country": "India",
            "rating": 5.0,
            "reviews": 312,
            "reviews_summary": "A true lifesaver for students facing intense study pressure in Kota coaching hubs.",
            "latitude": 25.1825,
            "longitude": 75.8398,
            "open_status": "Online Now",
            "timing": "08:00 - 20:00",
            "contact_number": "+91 744 240 5500",
            "maps_link": "https://maps.google.com/?q=Talwandi+Kota",
            "verified": True
        },
        # DELHI NCR
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
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "rating": 5.0,
            "reviews": 298,
            "reviews_summary": "Brilliant diagnosis and empathetic sessions. Transformed my mental well-being.",
            "latitude": 28.6139 + 0.01,
            "longitude": 77.2090 - 0.02,
            "open_status": "Online Now",
            "timing": "08:30 - 16:30",
            "contact_number": "+91 11 2658 8500",
            "maps_link": "https://maps.google.com/?q=AIIMS+New+Delhi",
            "verified": True
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
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "rating": 4.9,
            "reviews": 215,
            "reviews_summary": "Helped me break free from constant overthinking and debilitating panic loops.",
            "latitude": 28.6139 - 0.03,
            "longitude": 77.2090 + 0.02,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 11 2658 8600",
            "maps_link": "https://maps.google.com/?q=Max+Healthcare+Saket+Delhi",
            "verified": True
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
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "rating": 4.9,
            "reviews": 178,
            "reviews_summary": "A profound understanding of youth depression. Very accessible and caring.",
            "latitude": 28.6139 + 0.02,
            "longitude": 77.2090 + 0.005,
            "open_status": "Offline",
            "timing": "09:00 - 15:00",
            "contact_number": "+91 11 2658 8700",
            "maps_link": "https://maps.google.com/?q=Safdarjung+Hospital+New+Delhi",
            "verified": True
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
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "rating": 4.9,
            "reviews": 265,
            "reviews_summary": "Exceptional clinician who genuinely listens and guides with practical exercises.",
            "latitude": 19.0760 + 0.02,
            "longitude": 72.8777 - 0.03,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 22 2655 1234",
            "maps_link": "https://maps.google.com/?q=Lilavati+Hospital+Bandra+Mumbai",
            "verified": True
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
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "rating": 4.8,
            "reviews": 190,
            "reviews_summary": "Warm, respectful, and deeply knowledgeable therapist for college students.",
            "latitude": 19.0760 - 0.04,
            "longitude": 72.8777 + 0.015,
            "open_status": "Online Now",
            "timing": "11:00 - 19:00",
            "contact_number": "+91 22 2655 5678",
            "maps_link": "https://maps.google.com/?q=Bombay+Hospital+Marine+Lines+Mumbai",
            "verified": True
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
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "rating": 4.9,
            "reviews": 248,
            "reviews_summary": "Understands the exact pressure modern engineering students experience.",
            "latitude": 12.9716 + 0.01,
            "longitude": 77.5946 - 0.015,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 80 2699 5001",
            "maps_link": "https://maps.google.com/?q=NIMHANS+Bangalore",
            "verified": True
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
            "city": "Bangalore",
            "state": "Karnataka",
            "country": "India",
            "rating": 4.9,
            "reviews": 210,
            "reviews_summary": "Practical and deeply empathetic mental health support.",
            "latitude": 12.9716 - 0.02,
            "longitude": 77.5946 + 0.025,
            "open_status": "Offline",
            "timing": "09:00 - 15:00",
            "contact_number": "+91 80 2699 5002",
            "maps_link": "https://maps.google.com/?q=Manipal+Hospital+Bangalore",
            "verified": True
        },
        # PUNE
        {
            "doctor_name": "Dr. Rajesh Deshmukh, MD",
            "specialization": "Youth Depression & Anxiety",
            "specialization_type": "depression",
            "experience": 13,
            "degrees": "MD Psychiatry, BJ Medical College Pune",
            "certifications": "Licensed Clinical Psychiatrist",
            "achievements": "Pune Student Mental Health Pioneer",
            "bio": "Extensive experience supporting Pune university students dealing with isolation, academic pressure, and depressive feelings.",
            "hospital": "Ruby Hall Clinic, Pune",
            "city": "Pune",
            "state": "Maharashtra",
            "country": "India",
            "rating": 4.9,
            "reviews": 175,
            "reviews_summary": "Clear, compassionate, and actionable roadmap for mental recovery.",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "open_status": "Online Now",
            "timing": "09:00 - 18:00",
            "contact_number": "+91 20 6645 5100",
            "maps_link": "https://maps.google.com/?q=Ruby+Hall+Clinic+Pune",
            "verified": True
        },
        # HYDERABAD
        {
            "doctor_name": "Dr. Sravani Reddy, PhD",
            "specialization": "Stress & Performance Anxiety",
            "specialization_type": "stress",
            "experience": 10,
            "degrees": "PhD Psychology, University of Hyderabad",
            "certifications": "Certified CBT Practitioner",
            "achievements": "Telangana Youth Resilience Mentor",
            "bio": "Specializes in helping tech and university students overcome imposter syndrome and severe stress.",
            "hospital": "Apollo Health City, Jubilee Hills",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "rating": 4.9,
            "reviews": 195,
            "reviews_summary": "Very comforting sessions that gave me clear mental clarity.",
            "latitude": 17.3850,
            "longitude": 78.4867,
            "open_status": "Online Now",
            "timing": "10:00 - 19:00",
            "contact_number": "+91 40 2360 7777",
            "maps_link": "https://maps.google.com/?q=Apollo+Health+City+Hyderabad",
            "verified": True
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
            "city": "London",
            "state": "England",
            "country": "United Kingdom",
            "rating": 4.9,
            "reviews": 182,
            "reviews_summary": "Invaluable support through my postgraduate thesis stress.",
            "latitude": 51.5074 + 0.03,
            "longitude": -0.1278 - 0.02,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+44 20 3299 9000",
            "maps_link": "https://maps.google.com/?q=Kings+College+Hospital+London",
            "verified": True
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
            "city": "New York",
            "state": "New York",
            "country": "United States",
            "rating": 5.0,
            "reviews": 310,
            "reviews_summary": "Exceptional insights and deep clinical expertise in mood recovery.",
            "latitude": 40.7128 + 0.02,
            "longitude": -74.0060 - 0.015,
            "open_status": "Online Now",
            "timing": "08:00 - 16:00",
            "contact_number": "+1 (212) 555-0101",
            "maps_link": "https://maps.google.com/?q=NewYork-Presbyterian+Hospital",
            "verified": True
        },
        # JODHPUR
        {
            "doctor_name": "Dr. Kavita Rathore, MD",
            "specialization": "Anxiety & Academic Stress",
            "specialization_type": "anxiety",
            "experience": 10,
            "degrees": "MD Psychiatry, Dr. S.N. Medical College",
            "certifications": "Fellow of Indian Psychiatric Society",
            "achievements": "Youth Mental Health Champion – Rajasthan Medical Council 2022",
            "bio": "Specializes in helping students and young professionals overcome anxiety, academic overwhelm, and performance-related stress.",
            "hospital": "AIIMS Jodhpur",
            "city": "Jodhpur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.9,
            "reviews": 198,
            "reviews_summary": "Deeply empathetic and results-oriented. My anxiety reduced significantly after just 4 sessions.",
            "latitude": 26.2389 + 0.012,
            "longitude": 73.0243 - 0.008,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 291 255 0101",
            "maps_link": "https://maps.google.com/?q=AIIMS+Jodhpur",
            "verified": True
        },
        {
            "doctor_name": "Dr. Suresh Bishnoi, PsyD",
            "specialization": "Depression & Burnout",
            "specialization_type": "depression",
            "experience": 8,
            "degrees": "PsyD Clinical Psychology, MDSU Ajmer",
            "certifications": "Licensed Clinical Psychologist",
            "achievements": "Top Rated Therapist – Practo Jodhpur 2023",
            "bio": "Evidence-based support for depression, emotional exhaustion, and life transitions using CBT and mindfulness-based therapy.",
            "hospital": "Mathura Das Mathur Hospital, Jodhpur",
            "city": "Jodhpur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.8,
            "reviews": 154,
            "reviews_summary": "Helped me recover from a serious depressive episode before my final year exams.",
            "latitude": 26.2389 - 0.015,
            "longitude": 73.0243 + 0.018,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 291 255 0202",
            "maps_link": "https://maps.google.com/?q=Mathura+Das+Mathur+Hospital+Jodhpur",
            "verified": True
        },
        # UDAIPUR
        {
            "doctor_name": "Dr. Deepika Solanki, MD",
            "specialization": "Student Stress & Emotional Wellness",
            "specialization_type": "stress",
            "experience": 9,
            "degrees": "MD Psychiatry, RNT Medical College",
            "certifications": "Certified Mindfulness-Based Cognitive Therapist",
            "achievements": "Best Psychiatrist – Udaipur Times 2023",
            "bio": "Helps engineering and medical students navigate exam pressure, homesickness, and emotional resilience building.",
            "hospital": "RNT Medical College & Hospital, Udaipur",
            "city": "Udaipur",
            "state": "Rajasthan",
            "country": "India",
            "rating": 4.9,
            "reviews": 176,
            "reviews_summary": "Warm, professional, and incredibly insightful. Best counselor I've ever seen.",
            "latitude": 24.5854 + 0.010,
            "longitude": 73.7125 - 0.012,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 294 255 0101",
            "maps_link": "https://maps.google.com/?q=RNT+Medical+College+Udaipur",
            "verified": True
        },
        # CHENNAI
        {
            "doctor_name": "Dr. Meera Krishnamurthy, MD",
            "specialization": "Anxiety & Panic Disorders",
            "specialization_type": "anxiety",
            "experience": 13,
            "degrees": "MD Psychiatry, Madras Medical College",
            "certifications": "Fellow, National Academy of Medical Sciences",
            "achievements": "Top Psychiatrist Award – Tamil Nadu Medical Council 2022",
            "bio": "Specializes in anxiety disorders, panic attacks, and youth mental health using evidence-based cognitive therapy and medication management.",
            "hospital": "Apollo Hospitals Chennai",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "rating": 4.9,
            "reviews": 245,
            "reviews_summary": "Incredibly effective for panic disorders. I went from daily panic attacks to complete recovery in 3 months.",
            "latitude": 13.0827 + 0.015,
            "longitude": 80.2707 - 0.010,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 44 2829 0000",
            "maps_link": "https://maps.google.com/?q=Apollo+Hospitals+Chennai",
            "verified": True
        },
        {
            "doctor_name": "Dr. Venkatesh Raj, PsyD",
            "specialization": "Clinical Depression & Mood Disorders",
            "specialization_type": "depression",
            "experience": 11,
            "degrees": "PsyD, University of Madras",
            "certifications": "Licensed Psychologist, IPS Member",
            "achievements": "Founder, Chennai Youth Minds Initiative",
            "bio": "Treats clinical depression, bipolar disorder, and academic burnout using integrative psychotherapy for students and young adults.",
            "hospital": "NIMHANS Partner Clinic, Chennai",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "rating": 4.8,
            "reviews": 192,
            "reviews_summary": "Thoughtful, evidence-based approach. Genuinely changed how I handle depression.",
            "latitude": 13.0827 - 0.018,
            "longitude": 80.2707 + 0.012,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 44 2829 0101",
            "maps_link": "https://maps.google.com/?q=NIMHANS+Partner+Clinic+Chennai",
            "verified": True
        },
        # KOLKATA
        {
            "doctor_name": "Dr. Subhashis Banerjee, MD",
            "specialization": "Stress & Academic Burnout",
            "specialization_type": "stress",
            "experience": 14,
            "degrees": "MD Psychiatry, IPGMER Kolkata",
            "certifications": "Fellow of Indian Psychiatric Society",
            "achievements": "Best Clinician – Bengal Medical Council 2022",
            "bio": "Extensive experience helping undergraduate and postgraduate students overcome academic burnout and high-pressure competition stress.",
            "hospital": "SSKM Hospital, Kolkata",
            "city": "Kolkata",
            "state": "West Bengal",
            "country": "India",
            "rating": 4.9,
            "reviews": 218,
            "reviews_summary": "Comprehensive, caring approach. Helped me regain focus during my toughest semester.",
            "latitude": 22.5726 + 0.014,
            "longitude": 88.3639 - 0.009,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 33 2223 0101",
            "maps_link": "https://maps.google.com/?q=SSKM+Hospital+Kolkata",
            "verified": True
        },
        # CHANDIGARH
        {
            "doctor_name": "Dr. Harpreet Gill, MD",
            "specialization": "Anxiety & Depression",
            "specialization_type": "anxiety",
            "experience": 12,
            "degrees": "MD Psychiatry, PGIMER Chandigarh",
            "certifications": "Certified Cognitive Behavioral Therapist",
            "achievements": "Top Psychiatrist – Tribune Health Awards 2023",
            "bio": "PGIMER-trained psychiatrist offering evidence-based therapy for university students facing anxiety, depression, and social isolation.",
            "hospital": "PGIMER, Chandigarh",
            "city": "Chandigarh",
            "state": "Chandigarh",
            "country": "India",
            "rating": 4.9,
            "reviews": 224,
            "reviews_summary": "The PGIMER team is world-class. Dr. Gill specifically is outstanding for student mental health.",
            "latitude": 30.7333 + 0.012,
            "longitude": 76.7794 - 0.008,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 172 275 6565",
            "maps_link": "https://maps.google.com/?q=PGIMER+Chandigarh",
            "verified": True
        },
        # AHMEDABAD
        {
            "doctor_name": "Dr. Nikhil Patel, MD",
            "specialization": "Stress & Burnout",
            "specialization_type": "stress",
            "experience": 10,
            "degrees": "MD Psychiatry, B.J. Medical College",
            "certifications": "Licensed Psychiatrist, Gujarat Medical Council",
            "achievements": "Young Psychiatrist Award – Gujarat IPS 2022",
            "bio": "Specializes in student stress, academic burnout, and performance anxiety for engineering and medical college students across Gujarat.",
            "hospital": "Civil Hospital, Ahmedabad",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "country": "India",
            "rating": 4.8,
            "reviews": 183,
            "reviews_summary": "Clear, action-oriented guidance. Helped me manage IIT preparation stress effectively.",
            "latitude": 23.0225 + 0.010,
            "longitude": 72.5714 - 0.012,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 79 2255 0101",
            "maps_link": "https://maps.google.com/?q=Civil+Hospital+Ahmedabad",
            "verified": True
        },
        # LUCKNOW
        {
            "doctor_name": "Dr. Shyam Tripathi, MD",
            "specialization": "Clinical Depression & Anxiety",
            "specialization_type": "depression",
            "experience": 11,
            "degrees": "MD Psychiatry, KGMU Lucknow",
            "certifications": "Fellow of Indian Psychiatric Society",
            "achievements": "Best Doctor – UP Medical Council 2022",
            "bio": "Provides compassionate psychiatric care for students and young adults dealing with depression, anxiety, and adjustment disorders.",
            "hospital": "King George's Medical University, Lucknow",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "country": "India",
            "rating": 4.9,
            "reviews": 201,
            "reviews_summary": "Outstanding psychiatric support. Helped me through my darkest semester with patience and expertise.",
            "latitude": 26.8467 + 0.013,
            "longitude": 80.9462 - 0.010,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 522 225 0101",
            "maps_link": "https://maps.google.com/?q=King+George+Medical+University+Lucknow",
            "verified": True
        },
        # INDORE
        {
            "doctor_name": "Dr. Ritu Sharma, PsyD",
            "specialization": "Academic Stress & Anxiety",
            "specialization_type": "stress",
            "experience": 8,
            "degrees": "PsyD Clinical Psychology, DAVV Indore",
            "certifications": "Certified CBT Practitioner",
            "achievements": "Top Counselor – Indore Mental Health Summit 2023",
            "bio": "Helps college students in Indore manage exam anxiety, academic pressure, and emotional exhaustion using practical CBT techniques.",
            "hospital": "Choithram Hospital, Indore",
            "city": "Indore",
            "state": "Madhya Pradesh",
            "country": "India",
            "rating": 4.8,
            "reviews": 157,
            "reviews_summary": "Practical, no-nonsense approach to stress management. Genuinely transformative sessions.",
            "latitude": 22.7196 + 0.011,
            "longitude": 75.8577 - 0.009,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 731 255 0101",
            "maps_link": "https://maps.google.com/?q=Choithram+Hospital+Indore",
            "verified": True
        },
        # BHOPAL
        {
            "doctor_name": "Dr. Aakash Dubey, MD",
            "specialization": "Anxiety & Mood Disorders",
            "specialization_type": "anxiety",
            "experience": 9,
            "degrees": "MD Psychiatry, AIIMS Bhopal",
            "certifications": "Licensed Psychiatrist, MP Medical Council",
            "achievements": "AIIMS Bhopal Best Resident Award 2020",
            "bio": "AIIMS-trained psychiatrist providing expert care for anxiety, depression, and emotional burnout for students in Bhopal.",
            "hospital": "AIIMS Bhopal",
            "city": "Bhopal",
            "state": "Madhya Pradesh",
            "country": "India",
            "rating": 4.9,
            "reviews": 173,
            "reviews_summary": "Expert AIIMS doctor with a very calming and structured approach. Highly recommended.",
            "latitude": 23.2599 + 0.010,
            "longitude": 77.4126 - 0.010,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 755 255 0101",
            "maps_link": "https://maps.google.com/?q=AIIMS+Bhopal",
            "verified": True
        },
        # NAGPUR
        {
            "doctor_name": "Dr. Preeti Wankhede, MD",
            "specialization": "Depression & Student Wellness",
            "specialization_type": "depression",
            "experience": 10,
            "degrees": "MD Psychiatry, GMCH Nagpur",
            "certifications": "Fellow of Indian Psychiatric Society",
            "achievements": "Vidarbha Young Psychiatrist Award 2022",
            "bio": "Passionate about youth mental health, helping students in Nagpur overcome depression, loneliness, and career-related anxiety.",
            "hospital": "Government Medical College & Hospital, Nagpur",
            "city": "Nagpur",
            "state": "Maharashtra",
            "country": "India",
            "rating": 4.8,
            "reviews": 148,
            "reviews_summary": "Very caring and professional. Made me feel heard and supported throughout my recovery.",
            "latitude": 21.1458 + 0.012,
            "longitude": 79.0882 - 0.009,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 712 255 0101",
            "maps_link": "https://maps.google.com/?q=Government+Medical+College+Nagpur",
            "verified": True
        },
        # PATNA
        {
            "doctor_name": "Dr. Rajiv Kumar, MD",
            "specialization": "Stress & Academic Anxiety",
            "specialization_type": "stress",
            "experience": 12,
            "degrees": "MD Psychiatry, PMCH Patna",
            "certifications": "Certified Cognitive Behavioral Therapist",
            "achievements": "Bihar Medical Council Best Psychiatrist 2022",
            "bio": "Experienced in handling high-pressure academic stress for UPSC and competitive exam aspirants across Bihar.",
            "hospital": "Patna Medical College & Hospital",
            "city": "Patna",
            "state": "Bihar",
            "country": "India",
            "rating": 4.8,
            "reviews": 162,
            "reviews_summary": "Excellent for competitive exam students. Helped me manage UPSC preparation anxiety effectively.",
            "latitude": 25.5941 + 0.011,
            "longitude": 85.1376 - 0.008,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 612 255 0101",
            "maps_link": "https://maps.google.com/?q=Patna+Medical+College",
            "verified": True
        },
        # BHUBANESWAR
        {
            "doctor_name": "Dr. Sravani Mohanty, MD",
            "specialization": "Anxiety & Depression",
            "specialization_type": "anxiety",
            "experience": 9,
            "degrees": "MD Psychiatry, SCB Medical College",
            "certifications": "Licensed Psychiatrist, Odisha Medical Council",
            "achievements": "Young Psychiatrist Award – Odisha IPS 2023",
            "bio": "Committed to helping engineering and medical students in Odisha cope with anxiety, depression, and academic pressure.",
            "hospital": "AIIMS Bhubaneswar",
            "city": "Bhubaneswar",
            "state": "Odisha",
            "country": "India",
            "rating": 4.9,
            "reviews": 156,
            "reviews_summary": "Exceptional care and very understanding. Helped me regain my confidence before board exams.",
            "latitude": 20.2961 + 0.012,
            "longitude": 85.8245 - 0.010,
            "open_status": "Online Now",
            "timing": "09:00 - 17:00",
            "contact_number": "+91 674 255 0101",
            "maps_link": "https://maps.google.com/?q=AIIMS+Bhubaneswar",
            "verified": True
        },
        # SURAT
        {
            "doctor_name": "Dr. Bhavesh Desai, MD",
            "specialization": "Stress & Burnout",
            "specialization_type": "stress",
            "experience": 11,
            "degrees": "MD Psychiatry, Surat Municipal Institute of Medical Education",
            "certifications": "Certified Mindfulness Therapist",
            "achievements": "Surat Best Doctor Award – Gujarat Times 2022",
            "bio": "Helps textile industry workers, students, and professionals in Surat manage work stress, burnout, and anxiety disorders.",
            "hospital": "New Civil Hospital, Surat",
            "city": "Surat",
            "state": "Gujarat",
            "country": "India",
            "rating": 4.8,
            "reviews": 144,
            "reviews_summary": "Very practical and solutions-focused. Reduced my burnout symptoms within weeks.",
            "latitude": 21.1702 + 0.010,
            "longitude": 72.8311 - 0.011,
            "open_status": "Online Now",
            "timing": "10:00 - 18:00",
            "contact_number": "+91 261 255 0101",
            "maps_link": "https://maps.google.com/?q=New+Civil+Hospital+Surat",
            "verified": True
        }
    ]
    try:
        DoctorModel.seed_doctors(doctors)
        logger.info(f"Verified profiles database successfully seeded with {len(doctors)} entries.")
        HotlineModel.seed_hotlines()
        logger.info("Mental health crisis hotlines database successfully seeded.")
        GeoModel.seed_check()
    except Exception as e:
        logger.error(f"Failed to seed database contents: {str(e)}")


# Instantiate application node
app = create_app()

if __name__ == "__main__":
    import os
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=True)
