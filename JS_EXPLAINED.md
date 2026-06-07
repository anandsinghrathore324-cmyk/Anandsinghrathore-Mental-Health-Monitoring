# JS_EXPLAINED.md — Core Logic & Mathematical Sentiment Engine

This document provides a line-by-line logical walkthrough of **`script.js`**, detailing the particle canvases, preloader timelines, snappy validations, sessionStorage caches, counselor filters, and ML sentiment math equations.

---

## Section 1: Preloader & Snappy Credentials Verification (Lines 9 - 271)

```javascript
    const preloader = document.getElementById("aira-preloader");
    const loginPortal = document.getElementById("aira-login-portal");
    const loginForm = document.getElementById("aira-login-form");
    const usernameInput = document.getElementById("login-student-id");
    const passwordInput = document.getElementById("login-password");
    const errorMsg = document.getElementById("login-error-msg");
    const loginSubmitBtn = document.getElementById("login-submit-btn");
    const laserScanner = document.getElementById("login-scanner-laser");
    const demoAutofill = document.getElementById("login-demo-autofill");
    const logoutTrigger = document.getElementById("nav-logout-trigger");
```

### Key Logic Systems:

1. **Session Caching (`sessionStorage`)**:
   Reads `sessionStorage` instantly to bypass authentication checks during active development reloads:
   ```javascript
   const sessionActive = sessionStorage.getItem("aira_session_active") === "true";
   ```
2. **Preloader Simulation (`preloaderInterval`)**:
   Runs a recurring 80ms setup simulation that updates the progress bar track and logs setup indicators dynamically. When `progress >= 100`, fades out the loader, cleans up inline displays, and reveals the login cards.
3. **Login Gate Submit (`loginForm.addEventListener`)**:
   Toggles the **laser scanner element** to `display: block` to render cyber-secure diagnostic feedback.
4. **Credentials Validation Checks**:
   * Evaluates if username matches `student@aira.edu` (or `AIRA-2026`) and password matches `password`.
   * **If Valid:** Instantly updates button text to "Login Successful!", styles the button with glowing green vectors, sets the `aira_session_active` cache token, unlocks scrolling, and removes login elements from the viewport within a snappy 400ms.
   * **If Invalid:** Hides the laser lines, resets the button, and reveals the shaking `.login-error-message` overlay.
5. **Logout State Reset (`logoutTrigger.addEventListener`)**:
   Clears session states, wipes inputs, locks scrolling, rolls viewport to top, and restarts the preloader progress loop cleanly.

---

## Section 2: Neural Particle Canvasbackdrop (Lines 272 - 365)

```javascript
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2.5 + 1.2;
            this.speedX = Math.random() * 0.6 - 0.3;
            this.speedY = Math.random() * 0.6 - 0.3;
            this.color = Math.random() > 0.5 ? "rgba(0, 242, 254, 0.4)" : "rgba(127, 0, 255, 0.4)";
        }
```

### Key Logic Systems:
* **Particle Class**: Configures starting positions, sizing limits, floating speeds, and custom glow colors.
* **`connectParticles()`**: Tracks distances between every pair of particles:
  $$\text{dist} = \sqrt{(x_a - x_b)^2 + (y_a - y_b)^2}$$
  If `dist < 140px`, draw a vector connection line with alpha values inversely proportional to their proximity.
* **`animateParticles()`**: Standard requestAnimationFrame recursive loop to clear canvases, update speed variables, bounce off bounds, and redraw vectors at 60fps.

---

## Section 3: Counselor Geolocation Filters (Lines 535 - 576)

```javascript
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }
```

### Key Logic Systems:
* **The Haversine Equation (`calculateDistance`)**:
  Calculates distance between GPS coordinate nodes.
* **`getDoctorsForCity()`**:
  Matches specialists dynamically inside `doctorsByCity` arrays, sorts them by Haversine proximity, and renders details with online/offline indicators.

---

## Section 4: Workload & Stress Diagnostic Formulas (Lines 908 - 1029)

Here is where student digital workloads are mathematically mapped to specific stress threat risk percentages:

```javascript
// Capturing variables
const studyVal = parseFloat(document.getElementById("study-hours").value);
const sleepVal = parseFloat(document.getElementById("sleep-hours").value);
const screenVal = parseFloat(document.getElementById("screen-time").value);
const academicVal = parseInt(document.getElementById("academic-pressure").value);
const inputAnxiety = parseInt(document.getElementById("anxiety-level").value);
const inputStress = parseInt(document.getElementById("stress-level").value);
```

### 1. Sleep Deficit Index:
Tracks how far a student deviates from the ideal baseline of 8 hours of sleep:
$$\text{Sleep Deficit} = \max(0, 8 - \text{Sleep Hours})$$

### 2. Stress Threat Level ($R_{stress}$):
Spikes stress indices using sleep loss multipliers and subjective weight variables:
$$R_{stress} = (\text{Subjective Stress} \times 6) + (\text{Academic pressure} \times 3) + (\text{Sleep Deficit} \times 5)$$
* *If journal text matches `stressed` / `heavy` / `tired`*: Add $8\%$.
* *If journal text matches `exam` / `deadline` / `grades`*: Add $6\%$.
* *Locked between $8\%$ and $98\%$.*

### 3. Anxiety Threat Level ($R_{anxiety}$):
$$R_{anxiety} = (\text{Subjective Anxiety} \times 7) + (\text{Academic pressure} \times 2) + (\text{Sleep Deficit} \times 3)$$
* *If journal text matches `anxious` / `worry` / `nervous`*: Add $10\%$.
* *If journal text matches `scared` / `shaking` / `panic`*: Add $12\%$.
* *Locked between $5\%$ and $99\%$.*

### 4. Depression Threat Level ($R_{depression}$):
$$R_{depression} = (\text{Sleep Deficit} \times 6) + (\max(0, \text{Screen Time} - 6) \times 4) + (\text{Academic pressure} \times 2)$$
* *If selected mood is `melancholy`*: Add $20\%$.
* *If selected mood is `anxious`*: Add $10\%$.
* *If journal text matches `sad` / `lonely` / `cry`*: Add $12\%$.
* *If journal text matches `hopeless` / `empty` / `worthless`*: Add $20\%$.
* *Locked between $4\%$ and $98\%$.*

### 5. Overall Wellness Score ($W$):
$$W = 100 - \frac{R_{stress} + R_{anxiety} + R_{depression}}{3}$$

---

## Section 5: NLP DistilBERT Sentiment Parsing (Lines 1189 - 1251)

```javascript
    function executeDistilBERTNLP(text, stress, anxiety, depression) {
        const dictionary = [
            "exam", "stressed", "grades", "lonely", "exhausted", "tired", "sleep", "fail", "hopeless", "sad",
            "study", "anxious", "worry", "projects", "family", "friends", "happy", "accomplished", "relax"
        ];
        
        let foundKeywords = [];
        dictionary.forEach(word => { if (text.includes(word)) foundKeywords.push(word); });
```

### Key Logic Systems:
* **NLP Keyword Vector**: Analyzes standard vocabulary triggers inside journals, extracts keywords into active visual selector tags, and computes emotion ratios based on diagnostic stress indexes.
* **Normalization Loop**:
  Normalizes sentiment vectors (Joy, Sadness, Anger, Fear) to ensure the total is exactly $100\%$ on the dashboard:
  $$\text{joy} = 100 - \frac{\text{stress} + \text{depression}}{2}$$
  $$\text{sadness} = \text{depression} \times 0.90$$
  $$\text{anger} = \text{stress} \times 0.80$$
  $$\text{fear} = \text{anxiety} \times 0.95$$
  $$\text{sum} = \text{joy} + \text{sadness} + \text{anger} + \text{fear}$$
  $$\text{Normalized Value} = \frac{\text{Value}}{\text{sum}} \times 100$$
* **Update Charts**: Updates Line graphs and Radar graph inputs dynamically, and re-renders ChartJS instances seamlessly.

---

## Section 6: temporal Heatmap stability Engine (Lines 994 - 1025)

```javascript
        let todayMood = "joy";
        if (selectedMood === "sad" || selectedMood === "melancholy") {
            todayMood = "melancholy";
        } else if (selectedMood === "anxious") {
            todayMood = "anxiety";
        } else if (selectedMood === "stressed") {
            todayMood = "burnout";
        } else {
            if (finalWellness < 55) {
                todayMood = finalStress > finalAnxiety ? "burnout" : "anxiety";
            } else if (finalWellness < 80) {
                todayMood = "melancholy";
            }
        }
```

### Key Logic Systems:
* **Day 30 Update**: Evaluates current indices to tag the mood of the 30th slot dynamically.
* **`renderHeatmapGrid()`**: Clears the calendar element, builds 30 grid cell layers, adds hover animations, and binds click listeners to feed the inspector panel details dynamically.
* **Auto-Select**: Uses `setTimeout` to trigger click events on Day 30 cells automatically upon submitting scanners.
