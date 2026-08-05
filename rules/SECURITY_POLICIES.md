# AIRA Security & Authentication Policies

---

## 1. Authentication & Session Management

1. **Password Security**:
   * All passwords must be salted and hashed using `bcrypt` (minimum work factor = 12).
   * Plaintext passwords must never be logged or persisted.
2. **JSON Web Tokens (JWT)**:
   * Tokens must be signed with a strong cryptographic secret key stored in environment variables (`JWT_SECRET_KEY`).
   * Token lifetimes must not exceed 24 hours (`JWT_EXPIRATION_HOURS=24`).
3. **One-Time Passwords (OTP)**:
   * OTPs expire strictly after 10 minutes.
   * OTP requests are rate-limited per email address to prevent brute-force abuse.

---

## 2. Network & Email Dispatch

1. **Cloud & Render Compliance**:
   * Standard SMTP ports (25, 465, 587) are blocked on cloud free tiers (e.g. Render).
   * The production email driver uses Brevo's REST API over HTTPS (port 443).
2. **Environment Variables**:
   * Secrets (`SECRET_KEY`, `JWT_SECRET_KEY`, `BREVO_API_KEY`, `GOOGLE_PLACES_API_KEY`, `MONGODB_URI`) must NEVER be committed to Git.
   * Use `.env.example` as a sanitised template.

---

## 3. Data Privacy & External API Security

1. **Google Places Field Masking**:
   * All outbound requests to `places.googleapis.com` must include restrictive `X-Goog-FieldMask` headers to prevent over-fetching and minimize API data footprint.
2. **Input Validation**:
   * All inbound JSON payloads must be validated using `backend/middleware/validation.py` before hitting business logic.
3. **Mental Health Data Handling**:
   * Assessment results, mood logs, and chat interactions are tied strictly to authenticated user IDs.
   * No personally identifiable health data is exposed across unauthenticated endpoints.
4. **Quota Rate Limiting & Fail-Safe Fallbacks**:
   * External API quota failures (HTTP 429) or network timeouts must degrade gracefully into local distance-calculated database results without revealing backend internal credentials or stack traces to end users.

