/* ==========================================================================
   INTERACTIVE LOGIC: FUTURISTIC STUDENT MENTAL HEALTH & WELLNESS PLATFORM
   CLIENT-SIDE CAPABILITIES: Canvas Particles, Geolocation, NLP, ChartJS, AI Chat
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    
    // ==========================================================================
    // 1. NEURAL NETWORK PARTICLES BACKDROP (CANVAS)
    // ==========================================================================
    const canvas = document.getElementById("bg-canvas");
    const ctx = canvas.getContext("2d");
    
    let particlesArray = [];
    const numberOfParticles = 65;
    
    // Set Canvas Size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener("resize", () => {
        resizeCanvas();
        initParticles();
    });
    
    // Particle Blueprints
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2.5 + 1.2;
            this.speedX = Math.random() * 0.6 - 0.3;
            this.speedY = Math.random() * 0.6 - 0.3;
            this.color = Math.random() > 0.5 ? "rgba(0, 242, 254, 0.4)" : "rgba(127, 0, 255, 0.4)";
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            // Boundary bounce
            if (this.x > canvas.width || this.x < 0) this.speedX = -this.speedX;
            if (this.y > canvas.height || this.y < 0) this.speedY = -this.speedY;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = this.color;
            ctx.fill();
        }
    }
    
    function initParticles() {
        particlesArray = [];
        for (let i = 0; i < numberOfParticles; i++) {
            particlesArray.push(new Particle());
        }
    }
    
    // Connect particles with thin gradient lines
    function connectParticles() {
        let maxDistance = 140;
        for (let a = 0; a < particlesArray.length; a++) {
            for (let b = a; b < particlesArray.length; b++) {
                let dist = Math.hypot(particlesArray[a].x - particlesArray[b].x, particlesArray[a].y - particlesArray[b].y);
                if (dist < maxDistance) {
                    let alpha = (1 - (dist / maxDistance)) * 0.15;
                    ctx.strokeStyle = `rgba(0, 242, 254, ${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.shadowBlur = 0; // Clear shadow for lines to save rendering load
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particlesArray.forEach(p => {
            p.update();
            p.draw();
        });
        connectParticles();
        requestAnimationFrame(animateParticles);
    }
    
    initParticles();
    animateParticles();
    
    // ==========================================================================
    // 2. MOBILE RESPONSIVE HAMBURGER & SCROLL NAVIGATION
    // ==========================================================================
    const navbar = document.getElementById("main-navbar");
    const navLinks = document.getElementById("navbar-links");
    const hamburger = document.getElementById("nav-hamburger-toggle");
    
    // Hamburger active toggle
    hamburger.addEventListener("click", () => {
        hamburger.classList.toggle("active");
        navLinks.classList.toggle("active");
    });
    
    // Smooth navigation active states
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            hamburger.classList.remove("active");
            navLinks.classList.remove("active");
        });
    });
    
    // Navbar glass style on scroll
    window.addEventListener("scroll", () => {
        if (window.scrollY > 40) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });

    // ==========================================================================
    // 3. DIALOGUE INTERACTIVE INPUT SLIDERS & MOOD SELECTION
    // ==========================================================================
    const sliders = [
        { id: "academic-pressure", valId: "academic-pressure-val" },
        { id: "anxiety-level", valId: "anxiety-level-val" },
        { id: "stress-level", valId: "stress-level-val" }
    ];
    
    sliders.forEach(sliderInfo => {
        const input = document.getElementById(sliderInfo.id);
        const label = document.getElementById(sliderInfo.valId);
        if (input && label) {
            input.addEventListener("input", (e) => {
                label.textContent = e.target.value;
            });
        }
    });
    
    // Clickable Emoji Mood selector logic
    let selectedMood = "calm"; // Default mood parameter
    const moodOptions = document.querySelectorAll(".mood-option");
    
    moodOptions.forEach(opt => {
        // Init default
        if (opt.getAttribute("data-mood") === selectedMood) {
            opt.classList.add("active");
        }
        
        opt.addEventListener("click", () => {
            moodOptions.forEach(o => o.classList.remove("active"));
            opt.classList.add("active");
            selectedMood = opt.getAttribute("data-mood");
        });
    });

    // ==========================================================================
    // 4. PRESET CHART.JS DATA STRUCTURES & INITIALIZATION
    // ==========================================================================
    let stressTrendChart = null;
    let emotionProfileChart = null;
    
    function initAnalyticsCharts() {
        const lineCtx = document.getElementById("stressTrendChart").getContext("2d");
        const radarCtx = document.getElementById("emotionProfileChart").getContext("2d");
        
        // Custom Glowing Gradients for Line Chart
        const stressGradient = lineCtx.createLinearGradient(0, 0, 0, 300);
        stressGradient.addColorStop(0, "rgba(0, 242, 254, 0.45)");
        stressGradient.addColorStop(1, "rgba(0, 242, 254, 0.0)");
        
        const anxietyGradient = lineCtx.createLinearGradient(0, 0, 0, 300);
        anxietyGradient.addColorStop(0, "rgba(127, 0, 255, 0.45)");
        anxietyGradient.addColorStop(1, "rgba(127, 0, 255, 0.0)");
        
        // 1. Line Chart Setup
        stressTrendChart = new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Today'],
                datasets: [
                    {
                        label: 'Stress level',
                        data: [4, 5, 3, 6, 7, 5, 4, 5],
                        borderColor: '#00f2fe',
                        backgroundColor: stressGradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: '#00f2fe',
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Anxiety level',
                        data: [3, 4, 2, 5, 6, 4, 3, 4],
                        borderColor: '#7f00ff',
                        backgroundColor: anxietyGradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: '#7f00ff',
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#9ca3af', font: { family: 'Outfit', size: 12 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' },
                        min: 0,
                        max: 10
                    }
                }
            }
        });
        
        // 2. Radar/Doughnut Profile Chart Setup
        emotionProfileChart = new Chart(radarCtx, {
            type: 'doughnut',
            data: {
                labels: ['Joy', 'Sadness', 'Anger/Burnout', 'Fear/Anxiety'],
                datasets: [{
                    label: 'Emotional Distribution',
                    data: [40, 20, 15, 25],
                    backgroundColor: [
                        'rgba(0, 255, 135, 0.65)', // Joy - Emerald
                        'rgba(255, 0, 85, 0.65)',   // Sadness - Rose
                        'rgba(255, 159, 67, 0.65)',  // Anger - Orange
                        'rgba(127, 0, 255, 0.65)'   // Fear - Purple
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 2,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#9ca3af', font: { family: 'Outfit', size: 11 } }
                    }
                }
            }
        });
    }
    
    // Run initial rendering of the charts
    initAnalyticsCharts();

    // ==========================================================================
    // 8. 30-DAY MOOD STABILITY HEATMAP LOGS
    // ==========================================================================
    let heatmapHistory = [];
    const mockPhrases = {
        joy: [
            "Had a great study group session today, felt very productive!",
            "Passed my math midterm with an A! Let's go!",
            "Weekend is here. Caught up on sleep, feeling amazing.",
            "Had a beautiful walk on campus and grabbed coffee with friends.",
            "Resolved a coding bug that was bugging me for 3 days!"
        ],
        melancholy: [
            "Missed my family back home today, feeling a bit lonely.",
            "Struggled with classes and felt down about my academic track.",
            "Rainy weather and zero sleep is making today rough.",
            "Felt isolated and stayed in my room all afternoon.",
            "Just couldn't find the energy to go to the dining hall."
        ],
        burnout: [
            "Spent 12 hours studying in the library. Exhaustion is 10/10.",
            "Literally studied till 4 AM. Brain is completely fried.",
            "Too many deadlines colliding at once. Want to shut down.",
            "Screen time was 11 hours today. My eyes are burning.",
            "I'm saturated. I can't look at another syllabus slide."
        ],
        anxiety: [
            "Midterm tomorrow morning, heart is racing. Can't relax.",
            "Worried about grades and summer internships. Overthinking.",
            "Felt a wave of exam panic during my biology quiz.",
            "Social stress is hitting. Nervous about presenting in class.",
            "My sleep was plagued with stress dreams about failing."
        ]
    };

    function initHeatmapHistory() {
        const moods = ["joy", "melancholy", "burnout", "anxiety"];
        
        // Generate 29 mock days
        for (let i = 1; i <= 29; i++) {
            const mood = moods[Math.floor(Math.random() * moods.length)];
            const baseScore = mood === "joy" ? 85 : mood === "anxiety" ? 50 : mood === "burnout" ? 45 : 35;
            const score = baseScore + Math.floor(Math.random() * 15);
            const journalOptions = mockPhrases[mood];
            const journal = journalOptions[Math.floor(Math.random() * journalOptions.length)];
            
            heatmapHistory.push({
                day: i,
                mood: mood,
                score: score,
                journal: journal
            });
        }

        // Day 30 is default
        heatmapHistory.push({
            day: 30,
            mood: "joy",
            score: 85,
            journal: "Diagnostic Scanner active. Submit a scan to update Today's wellness block!"
        });
    }

    function renderHeatmapGrid() {
        const grid = document.getElementById("mood-heatmap-grid");
        const emptyMsg = document.getElementById("inspector-empty-msg");
        const contentPanel = document.getElementById("inspector-content");
        const dayTitle = document.getElementById("inspector-day-title");
        const scoreBadge = document.getElementById("inspector-wellness-score");
        const moodName = document.getElementById("inspector-mood-name");
        const journalText = document.getElementById("inspector-journal-text");

        if (!grid) return;
        grid.innerHTML = "";

        heatmapHistory.forEach(dayLog => {
            const cell = document.createElement("div");
            cell.className = `heatmap-day-cell mood-${dayLog.mood}`;
            cell.textContent = dayLog.day;
            
            // Add click listener
            cell.addEventListener("click", () => {
                grid.querySelectorAll(".heatmap-day-cell").forEach(c => c.classList.remove("active-selected"));
                cell.classList.add("active-selected");

                emptyMsg.style.display = "none";
                contentPanel.style.display = "block";

                dayTitle.textContent = `Day ${dayLog.day} Status`;
                scoreBadge.textContent = `${dayLog.score} Wellness`;
                
                let emoji = "😊";
                let formattedMoodName = "Joy / Optimism";
                if (dayLog.mood === "melancholy") { emoji = "😭"; formattedMoodName = "Melancholy / Sadness"; }
                if (dayLog.mood === "burnout") { emoji = "😫"; formattedMoodName = "Exhaustion / Burnout"; }
                if (dayLog.mood === "anxiety") { emoji = "🥺"; formattedMoodName = "Anxiety / Fear"; }

                moodName.innerHTML = `${formattedMoodName} ${emoji}`;
                journalText.textContent = `"${dayLog.journal}"`;
            });

            grid.appendChild(cell);
        });
    }

    // Initialize heatmap and render
    initHeatmapHistory();
    renderHeatmapGrid();

    // ==========================================================================
    // 5. THERAPIST RECOMMENDER LOGIC (GEOLOCATION API & SORTER)
    // ==========================================================================
    
    // Complete Mock Psychologists Database Near Stanford Coordinates
    const mockDoctors = [
        {
            name: "Dr. Evelyn Vance, PhD",
            specialization: "Clinical Depression",
            experience: 12,
            degree: "PhD in Clinical Psychology",
            certifications: "Board Certified Cognitive Behavioral Specialist",
            achievements: "Author of 'Mindful Transitions in Collegiate Life'",
            bio: "Specializing in student adjustment disorders, persistent depressive episodes, and cognitive restructuring therapies.",
            hospital: "Stanford Health & Psychiatric Center",
            status: "Online Now",
            hours: "09:00 - 17:00",
            rating: 4.9,
            phone: "+1 (650) 555-0182",
            type: "depression",
            lat: 37.4275, // Near Stanford University
            lon: -122.1697
        },
        {
            name: "Professor Julian Cross",
            specialization: "Stress & Burnout Specialist",
            experience: 16,
            degree: "MD in Psychiatry",
            certifications: "Certified Academic Saturation Counselor",
            achievements: "Developer of the Youth De-Escalation Protocol",
            bio: "Dedicated to helping university graduates balance rigorous course workloads, performance expectations, and sleep deficit conditions.",
            hospital: "Bay Area Neuro-Cognitive Clinic",
            status: "Online Now",
            hours: "08:00 - 16:30",
            rating: 4.8,
            phone: "+1 (650) 555-0294",
            type: "stress",
            lat: 37.4419, // Palo Alto Downtown
            lon: -122.1430
        },
        {
            name: "Dr. Chloe Sterling, LCSW",
            specialization: "General Anxiety Coach",
            experience: 8,
            degree: "Master of Social Work",
            certifications: "Licensed Clinical Social Worker & Mindfulness Practitioner",
            achievements: "Nominated Counselor of the Year (Palo Alto Board)",
            bio: "Utilizes trauma-informed somatic exercises, mindfulness, and Dialectical Behavioral Therapy to alleviate exam panic.",
            hospital: "Sterling Mindfulness Practice",
            status: "Offline",
            hours: "10:00 - 18:00",
            rating: 4.7,
            phone: "+1 (650) 555-0371",
            type: "anxiety",
            lat: 37.4130, // Menlo Park Area
            lon: -122.1802
        },
        {
            name: "Dr. Marcus Patel, PsyD",
            specialization: "Academic Performance Stress",
            experience: 10,
            degree: "Doctor of Psychology",
            certifications: "Certified Student Wellness Practitioner",
            achievements: "Creator of 'Stress-to-Progress' Cognitive Matrix",
            bio: "Addresses exam anxieties, low attention spans, and perfectionist self-criticism loops among competitive students.",
            hospital: "Palo Alto Student Wellness Guild",
            status: "Online Now",
            hours: "09:30 - 17:30",
            rating: 4.9,
            phone: "+1 (650) 555-0453",
            type: "stress",
            lat: 37.4300, // Stanford West
            lon: -122.1810
        },
        {
            name: "Dr. Sarah Lin, PhD",
            specialization: "Clinical Depression",
            experience: 14,
            degree: "PhD in Neuropsychology",
            certifications: "Licensed Clinical Psychologist",
            achievements: "Pioneered virtual cognitive support networks",
            bio: "Investigates biological depression pathways. Employs supportive interpersonal therapies to restore confidence.",
            hospital: "Palo Alto Neuro-Wellness Center",
            status: "Online Now",
            hours: "08:30 - 16:00",
            rating: 5.0,
            phone: "+1 (650) 555-0562",
            type: "depression",
            lat: 37.4520, // East Palo Alto
            lon: -122.1280
        }
    ];

    let userLatitude = 37.427961;  // Defaults (Stanford campus)
    let userLongitude = -122.168444;
    let proximityActive = false;

    // Haversine Distance Sorter
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return parseFloat((R * c).toFixed(1));
    }

    // Render Therapist list dynamically
    function renderDoctors(filterType = "all") {
        const grid = document.getElementById("doctor-results-grid");
        if (!grid) return;
        
        // Calculate distances for all doctors based on active coordinates
        let activeList = mockDoctors.map(doc => {
            return {
                ...doc,
                distance: calculateDistance(userLatitude, userLongitude, doc.lat, doc.lon)
            };
        });

        // Sort by closest distance first
        activeList.sort((a, b) => a.distance - b.distance);

        // Apply filters
        if (filterType !== "all") {
            activeList = activeList.filter(d => d.type === filterType);
        }

        grid.innerHTML = "";

        if (activeList.length === 0) {
            grid.innerHTML = `
                <div class="glass-panel form-group-full" style="padding: 2.5rem; text-align: center; grid-column: span 2;">
                    <i class="fa-solid fa-user-slash" style="font-size: 2rem; color: var(--neon-rose); margin-bottom: 1rem;"></i>
                    <p>No specialists matching the specific filter found nearby.</p>
                </div>`;
            return;
        }

        activeList.forEach(doc => {
            const statusClass = doc.status === "Online Now" ? "online" : "offline";
            const stars = "★".repeat(Math.floor(doc.rating)) + (doc.rating % 1 !== 0 ? "½" : "") + "☆".repeat(5 - Math.ceil(doc.rating));
            
            // Create Mock Avatars based on gender representation
            const genderKey = doc.name.includes("Dr. Sarah") || doc.name.includes("Chloe") || doc.name.includes("Vance") ? "women" : "men";
            const mockAvatarId = doc.experience * 3 % 99;
            const docAvatar = `https://randomuser.me/api/portraits/${genderKey}/${mockAvatarId}.jpg`;

            const card = document.createElement("div");
            card.className = "doctor-card glass-panel";
            card.innerHTML = `
                <span class="doc-status-badge ${statusClass}">${doc.status}</span>
                
                <div class="doc-main-info">
                    <div class="doc-avatar-container">
                        <img src="${docAvatar}" alt="${doc.name}" class="doc-avatar">
                    </div>
                    <div class="doc-meta">
                        <h4>${doc.name}</h4>
                        <div class="doc-specialty">${doc.specialization}</div>
                        <div class="doc-rating">${stars} <span>(${doc.rating})</span></div>
                    </div>
                </div>

                <p class="doc-bio">"${doc.bio}"</p>

                <div class="doc-details-grid">
                    <div class="doc-detail-item">
                        <span class="doc-detail-label">Degrees & Certifications</span>
                        <span class="doc-detail-val">${doc.degree}</span>
                    </div>
                    <div class="doc-detail-item">
                        <span class="doc-detail-label">Distance Node</span>
                        <span class="doc-detail-val"><i class="fa-solid fa-route"></i> ${doc.distance} km away</span>
                    </div>
                    <div class="doc-detail-item">
                        <span class="doc-detail-label">Clinic Center</span>
                        <span class="doc-detail-val">${doc.hospital}</span>
                    </div>
                    <div class="doc-detail-item">
                        <span class="doc-detail-label">Working Hours</span>
                        <span class="doc-detail-val">${doc.hours}</span>
                    </div>
                </div>

                <div class="doc-actions">
                    <a href="tel:${doc.phone.replace(/[^0-9+]/g, '')}" class="neon-btn neon-btn-primary" style="padding: 0.6rem; font-size: 0.82rem; border-radius: 10px;">
                        <i class="fa-solid fa-phone"></i> Contact Specialist
                    </a>
                    <a href="https://maps.google.com/?q=${doc.lat},${doc.lon}" target="_blank" class="neon-btn neon-btn-secondary" style="padding: 0.6rem; font-size: 0.82rem; border-radius: 10px;">
                        <i class="fa-solid fa-map-pin"></i> Maps
                    </a>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Trigger Initial Doctor List Sourcing
    renderDoctors();

    // Geolocation Browser API execution
    const geoBtn = document.getElementById("trigger-geo-api");
    const geoText = document.getElementById("geo-text-status");
    const geoLight = document.getElementById("geo-status-light");

    if (geoBtn) {
        geoBtn.addEventListener("click", () => {
            geoText.textContent = "Querying satellite position...";
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        userLatitude = position.coords.latitude;
                        userLongitude = position.coords.longitude;
                        proximityActive = true;

                        geoLight.classList.add("active");
                        geoText.textContent = `Active GPS Nodes: [Lat: ${userLatitude.toFixed(4)}, Lon: ${userLongitude.toFixed(4)}]`;
                        geoBtn.innerHTML = `<i class="fa-solid fa-satellite-dish"></i> GPS Active`;
                        geoBtn.style.borderColor = "var(--neon-emerald)";

                        // Rerender sorted counselors
                        renderDoctors();
                    },
                    (error) => {
                        console.error("GPS Request Denied/Timeout.", error);
                        geoText.textContent = "Satellite blocked. Reverted to campus fallback.";
                        setTimeout(() => {
                            geoText.textContent = "Proximity matching: Active Fallback Mode";
                        }, 3000);
                    }
                );
            } else {
                geoText.textContent = "HTML5 GPS unsupported in client.";
            }
        });
    }

    // Category Tabs click navigation handler
    const filterTabs = document.querySelectorAll(".filter-tab");
    filterTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            filterTabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            const filterVal = tab.getAttribute("data-filter");
            renderDoctors(filterVal);
        });
    });

    // ==========================================================================
    // 6. REAL-TIME AI SCANNING SIMULATOR (DIAGNOSTIC ALGORITHM)
    // ==========================================================================
    const scanForm = document.getElementById("mental-health-form");
    const submitBtn = document.getElementById("submit-scan-btn");
    const laserBar = document.getElementById("scanner-laser-bar");
    const consoleLog = document.getElementById("terminal-console");
    const resultsSec = document.getElementById("results-display");
    const dashboardSec = document.getElementById("dashboard");

    if (scanForm) {
        scanForm.addEventListener("submit", () => {
            // Standard form validation pass
            if (!scanForm.checkValidity()) return;

            // Trigger AI sweep animation
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing Neural Sequence...`;
            laserBar.style.display = "block";
            consoleLog.style.display = "block";

            // Simulated terminal prints
            const logs = [
                "INIT: Instantiating client tunnel to local secure micro-node...",
                "CHECK: Encrypting user form payload standard variables...",
                "NLP: Extracting journal sequence to DistilBERT vector space model...",
                "MODEL: Loading PyTorch weight metrics for Multilabel classifier...",
                "PROC: Categorizing sleep balance vs screen exposure habits...",
                "SUCCESS: Flask status code 200 returned in 1.4s.",
                "SUCCESS: Visualizing predicted diagnostics..."
            ];

            let logIndex = 0;
            consoleLog.innerHTML = "";

            const logTimer = setInterval(() => {
                if (logIndex < logs.length) {
                    const line = document.createElement("div");
                    line.className = "scan-log-line";
                    line.textContent = `>> ${logs[logIndex]}`;
                    consoleLog.appendChild(line);
                    consoleLog.scrollTop = consoleLog.scrollHeight;
                    logIndex++;
                } else {
                    clearInterval(logTimer);
                    
                    // Display results page smoothly
                    laserBar.style.display = "none";
                    consoleLog.style.display = "none";
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `<i class="fa-solid fa-radar"></i> Re-Analyze My Mental Health`;

                    executeDiagnosticMetrics();
                }
            }, 350);
        });
    }

    // Heavy Math calculations correlating form inputs to outputs
    function executeDiagnosticMetrics() {
        // Capture Form inputs
        const studyVal = parseFloat(document.getElementById("study-hours").value) || 6;
        const sleepVal = parseFloat(document.getElementById("sleep-hours").value) || 7;
        const screenVal = parseFloat(document.getElementById("screen-time").value) || 5;
        const academicVal = parseInt(document.getElementById("academic-pressure").value) || 5;
        const inputAnxiety = parseInt(document.getElementById("anxiety-level").value) || 4;
        const inputStress = parseInt(document.getElementById("stress-level").value) || 5;
        const textVal = document.getElementById("diary-input").value.toLowerCase();

        // 1. COMPUTE STRESS RISK LEVEL (0 - 100%)
        // Formula variables: sleep deficit spikes stress, high pressure spikes stress
        let sleepDeficit = Math.max(0, 8 - sleepVal); // ideal 8 hours
        let baseStress = (inputStress * 6) + (academicVal * 3) + (sleepDeficit * 5);
        
        // Scan for textual keywords impact stress
        if (textVal.includes("stressed") || textVal.includes("heavy") || textVal.includes("tired")) baseStress += 8;
        if (textVal.includes("exam") || textVal.includes("deadline") || textVal.includes("grades")) baseStress += 6;
        let finalStress = Math.min(98, Math.max(8, Math.round(baseStress)));

        // 2. COMPUTE ANXIETY RISK LEVEL (0 - 100%)
        let baseAnxiety = (inputAnxiety * 7) + (academicVal * 2) + (sleepDeficit * 3);
        if (textVal.includes("anxious") || textVal.includes("worry") || textVal.includes("nervous")) baseAnxiety += 10;
        if (textVal.includes("scared") || textVal.includes("shaking") || textVal.includes("panic")) baseAnxiety += 12;
        let finalAnxiety = Math.min(99, Math.max(5, Math.round(baseAnxiety)));

        // 3. COMPUTE DEPRESSION RISK LEVEL (0 - 100%)
        // Screen time and sleep lack strongly correlate
        let screenExcess = Math.max(0, screenVal - 6);
        let baseDepression = (sleepDeficit * 6) + (screenExcess * 4) + (academicVal * 2);
        
        if (selectedMood === "sad") baseDepression += 20;
        if (selectedMood === "anxious") baseDepression += 10;
        if (textVal.includes("sad") || textVal.includes("lonely") || textVal.includes("cry")) baseDepression += 12;
        if (textVal.includes("hopeless") || textVal.includes("empty") || textVal.includes("worthless")) baseDepression += 20;
        let finalDepression = Math.min(98, Math.max(4, Math.round(baseDepression)));

        // 4. OVERALL WELLNESS SCORE
        let avgRisk = (finalStress + finalAnxiety + finalDepression) / 3;
        let finalWellness = Math.round(100 - avgRisk);

        // Render predicted metric rings
        updateCircularProgress("ring-stress", "perc-stress", finalStress);
        updateCircularProgress("ring-anxiety", "perc-anxiety", finalAnxiety);
        updateCircularProgress("ring-depression", "perc-depression", finalDepression);

        // Risk Category Color badges
        updateRiskBadge("badge-stress", finalStress);
        updateRiskBadge("badge-anxiety", finalAnxiety);
        updateRiskBadge("badge-depression", finalDepression);

        // Wellness index displays
        const wellnessScore = document.getElementById("total-wellness-score");
        const wellnessDesc = document.getElementById("wellness-interpretation");
        const diagnosticTime = document.getElementById("diagnostic-timestamp");

        wellnessScore.textContent = finalWellness;
        
        // Dynamic time stamp
        const now = new Date();
        diagnosticTime.innerHTML = `<i class="fa-solid fa-clock"></i> Node Synced: ${now.toISOString().replace('T', ' ').slice(0, 19)}`;

        let interpText = "";
        if (finalWellness >= 75) {
            interpText = "Your cognitive loads are in harmony with physiological patterns. AI recommends maintaining physical breaks every two hours.";
        } else if (finalWellness >= 50) {
            interpText = "Moderate stress registers. Sleep deficits are impacting emotional scores. Focus on structured wind-down periods prior to sleep.";
        } else {
            interpText = "High saturation levels identified. System detects critical anxiety/depression warnings. AI recommends immediate counselor consultation.";
        }
        wellnessDesc.textContent = interpText;

        // 5. NLP DISTILBERT KEYWORD & SENTIMENT DEDUCTION
        executeDistilBERTNLP(textVal, finalStress, finalAnxiety, finalDepression);

        // Display results
        resultsSec.style.display = "block";
        dashboardSec.style.display = "block";

        // Scroll to results cleanly
        resultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Update Charts
        updateAnalyticsData(finalStress, finalAnxiety, finalWellness);

        // Update Day 30 in Heatmap
        let todayMood = "joy";
        if (finalWellness < 55) {
            todayMood = finalStress > finalAnxiety ? "burnout" : "anxiety";
        } else if (finalWellness < 80) {
            todayMood = "melancholy";
        }
        
        heatmapHistory[29] = {
            day: 30,
            mood: todayMood,
            score: finalWellness,
            journal: document.getElementById("diary-input").value || "Submitted today's diagnostic assessment."
        };
        renderHeatmapGrid();
        
        // Auto select Day 30 in the grid to highlight it instantly!
        setTimeout(() => {
            const cells = document.querySelectorAll(".heatmap-day-cell");
            if (cells.length >= 30) {
                cells[29].click();
            }
        }, 100);

        // 6. TAILORED WELLNESS RECOVERY CHECKLIST PLAN
        generateTailoredActionPlan(finalStress, finalAnxiety, finalDepression);
    }

    function generateTailoredActionPlan(stress, anxiety, depression) {
        const planContainer = document.getElementById("wellness-action-plan");
        const checklistContainer = document.getElementById("action-checklist-container");
        const successAlert = document.getElementById("action-success-alert");
        const badgeStatus = document.getElementById("action-plan-badge-status");
        const fillBar = document.getElementById("action-progress-bar-fill");
        const fillText = document.getElementById("action-progress-percent");

        if (!planContainer || !checklistContainer) return;

        // Reset display states
        successAlert.style.display = "none";
        fillBar.style.width = "0%";
        fillText.textContent = "0%";
        badgeStatus.textContent = "0/4 Completed";
        planContainer.style.display = "block";
        planContainer.style.borderColor = "rgba(225, 0, 255, 0.2)";
        planContainer.style.boxShadow = "none";

        // Task pool
        const stressTasks = [
            "Complete a 2-minute Guided Breathing session in the Mindfulness Box",
            "Shut down all university and academic browser tabs for 15 minutes",
            "Perform a dynamic neck, shoulder, and wrist release stretch",
            "Establish a firm wind-down routine 1 hour before sleep tonight"
        ];

        const anxietyTasks = [
            "Use the 4-7-8 Breathing Cycle in the Mindfulness Box for immediate nervous calming",
            "Vent your current worries freely to Aira in the floating chatbot",
            "Hydrate with 250ml of warm herbal tea or water right now",
            "Write down 3 things within physical reach to ground your focus (3-3-3 rule)"
        ];

        const depressionTasks = [
            "Step outside or near a window for 10 minutes of natural light",
            "Review your closest specialist referral notes and check physical distances",
            "Reach out to a trusted university friend, peer, or dial 988 if needed",
            "Log your mood stability status index in the analytics dashboard"
        ];

        const generalTasks = [
            "Establish a 15-minute screen-free break from academic pressures",
            "Commit to achieving a continuous 7.5-hour sleep cycle tonight",
            "Organize your immediate study workspace to minimize visual stress triggers",
            "Take 10 slow, deep nasal breaths to lower cognitive fatigue coefficients"
        ];

        // Pick 4 tasks based on dominant risk
        let selectedTasks = [];

        if (stress >= 60) {
            selectedTasks.push(stressTasks[0], stressTasks[1]);
        }
        if (anxiety >= 60) {
            selectedTasks.push(anxietyTasks[0], anxietyTasks[1]);
        }
        if (depression >= 55) {
            selectedTasks.push(depressionTasks[0], depressionTasks[1]);
        }

        // Fill remaining up to 4 tasks from general pool or unused specialized lists
        const taskPool = [...stressTasks.slice(2), ...anxietyTasks.slice(2), ...depressionTasks.slice(2), ...generalTasks];
        for (let task of taskPool) {
            if (selectedTasks.length >= 4) break;
            if (!selectedTasks.includes(task)) {
                selectedTasks.push(task);
            }
        }

        // Make sure we have exactly 4
        while (selectedTasks.length < 4) {
            selectedTasks.push(generalTasks[selectedTasks.length]);
        }

        // Render checklist in DOM
        checklistContainer.innerHTML = "";
        selectedTasks.forEach((taskText, idx) => {
            const item = document.createElement("label");
            item.className = "checklist-item";
            item.innerHTML = `
                <div class="checklist-checkbox-wrapper">
                    <input type="checkbox" class="checklist-checkbox" id="task-${idx}">
                    <span class="checklist-checkbox-custom"></span>
                </div>
                <span class="checklist-text">${taskText}</span>
            `;
            checklistContainer.appendChild(item);
        });

        // Add event listeners on checkboxes
        const checkboxes = checklistContainer.querySelectorAll(".checklist-checkbox");
        checkboxes.forEach(box => {
            box.addEventListener("change", () => {
                const checkedCount = checklistContainer.querySelectorAll(".checklist-checkbox:checked").length;
                const total = checkboxes.length;
                const percentage = Math.round((checkedCount / total) * 100);

                // Update progress elements
                fillBar.style.width = `${percentage}%`;
                fillText.textContent = `${percentage}%`;
                badgeStatus.textContent = `${checkedCount}/${total} Completed`;

                // Handle success state completion
                if (checkedCount === total) {
                    successAlert.style.display = "flex";
                    // Custom pulse glow highlight
                    planContainer.style.borderColor = "var(--neon-emerald)";
                    planContainer.style.boxShadow = "var(--glow-emerald)";
                } else {
                    successAlert.style.display = "none";
                    planContainer.style.borderColor = "rgba(225, 0, 255, 0.2)";
                    planContainer.style.boxShadow = "none";
                }
            });
        });
    }

    function updateCircularProgress(barId, percId, value) {
        const ring = document.getElementById(barId);
        const text = document.getElementById(percId);
        if (!ring || !text) return;
        
        // 251.2 is the stroke-dasharray circum for r=40
        const circumference = 251.2;
        const offset = circumference - (value / 100) * circumference;
        ring.style.strokeDashoffset = offset;
        
        // Count up animation
        let current = 0;
        const countTimer = setInterval(() => {
            if (current >= value) {
                text.textContent = `${value}%`;
                clearInterval(countTimer);
            } else {
                current += Math.ceil(value / 10);
                if (current > value) current = value;
                text.textContent = `${current}%`;
            }
        }, 30);
    }

    function updateRiskBadge(badgeId, value) {
        const badge = document.getElementById(badgeId);
        if (!badge) return;
        
        badge.className = "risk-badge"; // Reset classes
        if (value < 40) {
            badge.textContent = "Low Risk 😊";
            badge.classList.add("risk-safe");
        } else if (value < 70) {
            badge.textContent = "Moderate Stress 😕";
            badge.classList.add("risk-moderate");
        } else {
            badge.textContent = "High Risk 😫⚠️";
            badge.classList.add("risk-high");
        }
    }

    function executeDistilBERTNLP(text, stress, anxiety, depression) {
        const interpretationText = document.getElementById("nlp-interpretation-text");
        const keywordContainer = document.getElementById("nlp-extracted-keywords");
        
        // Simple client-side text extractor
        const dictionary = [
            "exam", "stressed", "grades", "lonely", "exhausted", "tired", "sleep", "fail", "hopeless", "sad",
            "study", "anxious", "worry", "projects", "family", "friends", "happy", "accomplished", "relax"
        ];

        let foundKeywords = [];
        dictionary.forEach(word => {
            if (text.includes(word)) foundKeywords.push(word);
        });

        // Set Default Fallbacks if text is too short
        if (foundKeywords.length === 0) foundKeywords = ["academic", "routine", "neutral"];

        keywordContainer.innerHTML = "";
        foundKeywords.forEach(word => {
            const tag = document.createElement("span");
            tag.className = "nlp-keyword-tag";
            tag.textContent = word;
            keywordContainer.appendChild(tag);
        });

        // Calculate emotion ratios
        let joyVal = Math.round(100 - (stress + depression)/2);
        let sadVal = Math.round(depression * 0.9);
        let angerVal = Math.round(stress * 0.8);
        let fearVal = Math.round(anxiety * 0.95);

        // Normalize
        const sum = joyVal + sadVal + angerVal + fearVal;
        joyVal = Math.round((joyVal / sum) * 100);
        sadVal = Math.round((sadVal / sum) * 100);
        angerVal = Math.round((angerVal / sum) * 100);
        fearVal = 100 - (joyVal + sadVal + angerVal); // lock at 100% total

        // Update progress bars
        document.getElementById("nlp-joy-perc").textContent = `${joyVal}%`;
        document.getElementById("nlp-joy-bar").style.width = `${joyVal}%`;

        document.getElementById("nlp-sad-perc").textContent = `${sadVal}%`;
        document.getElementById("nlp-sad-bar").style.width = `${sadVal}%`;

        document.getElementById("nlp-anger-perc").textContent = `${angerVal}%`;
        document.getElementById("nlp-anger-bar").style.width = `${angerVal}%`;

        document.getElementById("nlp-fear-perc").textContent = `${fearVal}%`;
        document.getElementById("nlp-fear-bar").style.width = `${fearVal}%`;

        // Text Interpretation summary
        let nlpInterpretation = "";
        if (joyVal > 40) {
            nlpInterpretation = "Semantic vector mapping registers positive sentiment constructs with balanced outlook references.";
        } else if (fearVal > 45 || angerVal > 45) {
            nlpInterpretation = "Semantic analyzer isolated high-density anxiety and workload distress linguistic tags. Prioritize cognitive de-escalation.";
        } else {
            nlpInterpretation = "Linguistic markers suggest persistent mental saturation, melancholic cues, and academic pressure. Recommend scheduling physical balance hours.";
        }
        interpretationText.textContent = `"${nlpInterpretation}"`;
    }

    function updateAnalyticsData(stress, anxiety, wellness) {
        // Update Chart Line today index
        stressTrendChart.data.datasets[0].data[7] = Math.round(stress / 10);
        stressTrendChart.data.datasets[1].data[7] = Math.round(anxiety / 10);
        stressTrendChart.update();

        // Update Radar values
        const joy = parseFloat(document.getElementById("nlp-joy-perc").textContent) || 30;
        const sad = parseFloat(document.getElementById("nlp-sad-perc").textContent) || 20;
        const anger = parseFloat(document.getElementById("nlp-anger-perc").textContent) || 20;
        const fear = parseFloat(document.getElementById("nlp-fear-perc").textContent) || 30;

        emotionProfileChart.data.datasets[0].data = [joy, sad, anger, fear];
        emotionProfileChart.update();

        // Update Mini-dashboard cards text values
        const sleepHours = parseFloat(document.getElementById("sleep-hours").value) || 7;
        const academicVal = parseInt(document.getElementById("academic-pressure").value) || 5;

        document.getElementById("stat-stability").textContent = `${Math.round(wellness * 0.9)}%`;
        document.getElementById("stat-sleep").textContent = sleepHours >= 7 ? "Good" : sleepHours >= 5 ? "Deficit" : "Critical";
        document.getElementById("stat-burnout").textContent = (stress > 65) ? "High" : (stress > 40) ? "Medium" : "Low";
        document.getElementById("stat-academic").textContent = academicVal >= 8 ? "Severe" : academicVal >= 5 ? "High" : "Low";
        document.getElementById("stat-social").textContent = sleepHours < 5 ? "Strained" : "Balanced";
        
        // Find dominant emotion
        const maxEmo = Math.max(joy, sad, anger, fear);
        let dominantText = "Calm";
        if (maxEmo === joy) dominantText = "Joy 😊";
        if (maxEmo === sad) dominantText = "Melancholy 😭";
        if (maxEmo === anger) dominantText = "Exhaustion 😫";
        if (maxEmo === fear) dominantText = "Anxiety 🥺";
        document.getElementById("stat-primary-emo").textContent = dominantText;

        // Dynamic Emoji Alert Strip update
        const emojiElement = document.getElementById("status-emoji");
        const titleElement = document.getElementById("status-message-title");
        const descElement = document.getElementById("status-message-desc");
        const statusScore = document.getElementById("status-score-display");
        const statusStrip = document.getElementById("emoji-status-strip");

        statusScore.textContent = `Wellness score: ${wellness}`;

        // Color & text shifts relative to risk
        if (wellness >= 80) {
            emojiElement.textContent = "😊";
            titleElement.textContent = "Stability Status: Optimal Wellness";
            descElement.textContent = "Your mental health profile displays great resilience. Keep maintaining physical breaks!";
            statusStrip.style.boxShadow = "var(--glow-emerald)";
            statusStrip.style.borderColor = "var(--neon-emerald)";
        } else if (wellness >= 55) {
            emojiElement.textContent = "😕";
            titleElement.textContent = "Stability Status: Moderate Strain";
            descElement.textContent = "Cognitive saturation identified. Sleep cycles are strained. Schedule a wind-down break.";
            statusStrip.style.boxShadow = "0 0 15px rgba(255, 159, 67, 0.3)";
            statusStrip.style.borderColor = "var(--neon-orange)";
        } else {
            emojiElement.textContent = "😭🚨";
            titleElement.textContent = "Stability Status: High Distress Warning";
            descElement.textContent = "Critical indicators identified. Please consider dialling 988 or consult our closest doctor nodes immediately.";
            statusStrip.style.boxShadow = "var(--glow-rose)";
            statusStrip.style.borderColor = "var(--neon-rose)";
        }

        // Recommend specialized therapists based on diagnostic outcome
        let specialtyMatch = "all";
        if (stress > 65) specialtyMatch = "stress";
        else if (anxiety > 65) specialtyMatch = "anxiety";
        else if (depression > 60) specialtyMatch = "depression";

        // Auto highlight tab
        filterTabs.forEach(t => {
            t.classList.remove("active");
            if (t.getAttribute("data-filter") === specialtyMatch) {
                t.classList.add("active");
            }
        });
        renderDoctors(specialtyMatch);
    }

    // ==========================================================================
    // 7. GEN-Z FRIENDLY SMART AI CHATBOT LOGIC ("AIRA")
    // ==========================================================================
    const chatbotWrapper = document.getElementById("chatbot-wrapper");
    const openChatBtn = document.getElementById("open-chat-widget");
    const closeChatBtn = document.getElementById("close-chat-widget");
    const chatPanel = document.getElementById("chat-panel");
    const chatInput = document.getElementById("chatbot-input-field");
    const chatSubmit = document.getElementById("chatbot-submit-btn");
    const msgContainer = document.getElementById("chatbot-msg-container");
    const typingDots = document.getElementById("chat-typing-dots");

    // Toggle panel visibility
    openChatBtn.addEventListener("click", () => {
        openChatBtn.classList.toggle("active");
        chatPanel.classList.toggle("active");
        
        // Auto scroll to latest bubble
        msgContainer.scrollTop = msgContainer.scrollHeight;
    });

    closeChatBtn.addEventListener("click", () => {
        openChatBtn.classList.remove("active");
        chatPanel.classList.remove("active");
    });

    // Hooks from hero button trigger
    const heroTrigger = document.getElementById("hero-chat-trigger");
    if (heroTrigger) {
        heroTrigger.addEventListener("click", () => {
            openChatBtn.classList.add("active");
            chatPanel.classList.add("active");
            msgContainer.scrollTop = msgContainer.scrollHeight;
        });
    }

    const featureTrigger = document.getElementById("feature-chat-trigger");
    if (featureTrigger) {
        featureTrigger.addEventListener("click", () => {
            openChatBtn.classList.add("active");
            chatPanel.classList.add("active");
            msgContainer.scrollTop = msgContainer.scrollHeight;
        });
    }

    const navTrigger = document.getElementById("nav-chat-trigger");
    if (navTrigger) {
        navTrigger.addEventListener("click", () => {
            openChatBtn.classList.add("active");
            chatPanel.classList.add("active");
            msgContainer.scrollTop = msgContainer.scrollHeight;
        });
    }

    // Handle submissions with optional custom queries (e.g. from Suggestion Chips)
    function submitChatMessage(customQuery) {
        const query = (typeof customQuery === "string") ? customQuery.trim() : chatInput.value.trim();
        if (!query) return;

        // Render User Bubble
        renderMessageBubble(query, "user");
        
        // Only clear input field if query was typed manually
        if (typeof customQuery !== "string") {
            chatInput.value = "";
        }

        // Trigger loading typing indicators
        typingDots.style.display = "flex";
        msgContainer.scrollTop = msgContainer.scrollHeight;

        setTimeout(() => {
            typingDots.style.display = "none";
            const botResponse = generateGenZResponse(query);
            renderMessageBubble(botResponse, "bot");
            msgContainer.scrollTop = msgContainer.scrollHeight;
        }, 1100);
    }

    chatSubmit.addEventListener("click", () => submitChatMessage());
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") submitChatMessage();
    });

    // Handle suggestion chips click dynamically
    document.querySelectorAll(".chat-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const chipMsg = chip.getAttribute("data-msg");
            if (chipMsg) {
                submitChatMessage(chipMsg);
            }
        });
    });

    function renderMessageBubble(text, sender) {
        const bubble = document.createElement("div");
        bubble.className = `chat-msg chat-msg-${sender}`;
        bubble.innerHTML = text;
        
        // Insert before typing dots
        msgContainer.insertBefore(bubble, typingDots);
    }

    // AI Response Routing Engine - Supportive, motivational, casual Gen-Z vibes
    function generateGenZResponse(input) {
        const query = input.toLowerCase();

        // 0. Mindfulness / Breathing triggers
        if (query.includes("breath") || query.includes("calm me") || query.includes("mindful") || query.includes("relax")) {
            const replies = [
                "Oh, let's calm down together 😌 Try our guided breathing exercise in the **<a href='#mindfulness' style='color: var(--neon-cyan); text-decoration: underline; font-weight: 600;'>Mindfulness Center</a>**! We have Box Breathing and 4-7-8 methods ready to help you de-escalate anxiety right now! 💙",
                "I feel that! Grounding yourself is super key. I highly recommend heading to our **<a href='#mindfulness' style='color: var(--neon-cyan); text-decoration: underline; font-weight: 600;'>Mindfulness Center</a>** and starting a Box Breathing cycle. I'll wait right here while you reset 🧘‍♀️✨",
                "Slowing down your breath literally rewires exam panic instantly. Give the visual bubble in our **<a href='#mindfulness' style='color: var(--neon-cyan); text-decoration: underline; font-weight: 600;'>Mindfulness Center</a>** a try. Let me know if that helps, bestie! 💙"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 1. Stress triggers
        if (query.includes("stress") || query.includes("burnout") || query.includes("exhausted") || query.includes("tired")) {
            const replies = [
                "Hey 😭 you've been carrying a lot lately. Seriously, academic pressure is no joke. Maybe your brain just needs a small reset 💙 Try shutting the laptop for literally 15 mins. Small breaks count!",
                "Exhaustion is too real. Bestie, please drink some water and put on your favorite comforting track. You are worth more than your productivity scale 🌸",
                "Felt that in my code. Stalling and feeling fried is your nervous system yelling for rest. Give yourself permission to pause tonight, okay? 💙"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 2. Focus struggles
        if (query.includes("focus") || query.includes("attention") || query.includes("concentrate") || query.includes("can't focus")) {
            const replies = [
                "That happens to literally everyone sometimes 🔥 Small progress still counts. How about we just do 5 minutes of study, then a 5-minute scrolling reward? Low-key Pomodoro method hits different.",
                "Attention spans under stress are literally non-existent 😭 Don't beat yourself up! Break the task into micro-steps. Like, writing one sentence. You got this 💙",
                "Your brain is probably just over-stimulated, bestie. Take a deep breath, clear the tabs, and focus on just ONE small thing. Let's get it! 🚀"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 3. Loneliness & Melancholy
        if (query.includes("lonely") || query.includes("alone") || query.includes("isolated") || query.includes("no friends")) {
            const replies = [
                "I’m here with you 💙 You deserve support too. Feeling lonely in college is so common but it doesn't mean you don't belong here. I'm literally always in your pocket if you need a chat.",
                "Sending you the biggest virtual hug ever 🫂 You are so appreciated, even if it feels quiet right now. You're never fully alone while I'm active!",
                "College can feel like a crowded room where you're totally alone, no cap. It's valid to feel this way. I'm here to listen to anything you want to vent about 🌸"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 4. Academic Panics
        if (query.includes("fail") || query.includes("exam") || query.includes("grades") || query.includes("test") || query.includes("college")) {
            const replies = [
                "I promise you, your grades do NOT define your worth 😭 Even if a test goes bad, you are still brilliant, funny, and worthy of good things. One test can't stop your sparkle!",
                "Academic pressure is low-key toxic sometimes. Take a deep breath. Study for 20 mins, then rest. You're going to get through this semester, trust the process 💙",
                "Failing is just a plot twist in your success arc! Seriously. Don't stress too much. We will dust ourselves off and try again. Besties don't quit, but they DO rest 🚀"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 5. Sadness & Crying
        if (query.includes("sad") || query.includes("cry") || query.includes("unhappy") || query.includes("depressed")) {
            const replies = [
                "It is totally okay to cry 😭 Letting it out is actually a sign of strength, not weakness. I'm here for you and I'm listening 💙",
                "Hey... things feel heavy right now, and that's so valid. You don't have to be strong all the time. Sending you all the warm vibes 🌸",
                "I'm keeping space for you. Take your time, breathe, and remember that bad days are temporary even if they feel endless right now 🫂"
            ];
            return replies[Math.floor(Math.random() * replies.length)];
        }

        // 6. Greetings
        if (query.includes("hi") || query.includes("hello") || query.includes("hey") || query.includes("yo")) {
            return "Hey bestie! 👋 How is student life treating you today? Let's talk or vent, I'm all ears! 💙";
        }

        // 7. General positive feedback
        if (query.includes("thanks") || query.includes("thank you") || query.includes("love you") || query.includes("great")) {
            return "Aww, stop it, you're making my circuits blush! 🥰 Always here for you! Keep shining ✨";
        }

        // Fallbacks
        const fallbacks = [
            "Wait, say more about that... I'm listening bestie 💙",
            "Honestly, that is so valid. Tell me more, let's unpack it together 🌸",
            "No cap, student life is wild. I'm here for all of it. How does that make you feel overall? 🫂",
            "You're doing great, seriously. Just taking the time to write it down is a win! What is your next small move? ✨"
        ];
        return fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }

    // ==========================================================================
    // 9. DYNAMIC PACED BREATHING & MINDFULNESS ENGINE
    // ==========================================================================
    const rhythmCards = document.querySelectorAll(".breath-rhythm-card");
    const playBtn = document.getElementById("breath-btn-play");
    const resetBtn = document.getElementById("breath-btn-reset");
    const bubbleOuter = document.getElementById("breath-visual-bubble");
    const labelIndicator = document.getElementById("breath-text-indicator");
    const countdown = document.getElementById("breath-countdown");
    const instructions = document.getElementById("breath-instruction-text");

    let breathInterval = null;
    let breathTimeout = null;
    let isBreathingActive = false;
    let selectedRhythm = "box"; // default Box breathing

    // Preset configurations for intervals
    const rhythmsConfig = {
        box: [
            { state: "inhale", duration: 4, text: "Inhale", desc: "Breathe in slowly through your nose, expanding your chest." },
            { state: "hold", duration: 4, text: "Hold", desc: "Hold your lungs full. Relax your shoulders and focus." },
            { state: "exhale", duration: 4, text: "Exhale", desc: "Release all air slowly through your mouth, letting go of strain." },
            { state: "hold", duration: 4, text: "Hold", desc: "Rest with empty lungs. Clear your thoughts entirely." }
        ],
        relax: [
            { state: "inhale", duration: 4, text: "Inhale", desc: "Quietly breathe in through your nose for 4 seconds." },
            { state: "hold", duration: 7, text: "Hold", desc: "Keep your breath suspended. Focus on absolute stillness." },
            { state: "exhale", duration: 8, text: "Exhale", desc: "Make a soft whoosh sound as you exhale completely for 8 seconds." }
        ],
        coherent: [
            { state: "inhale", duration: 5, text: "Inhale", desc: "Draw breath in smoothly over 5 even seconds." },
            { state: "exhale", duration: 5, text: "Exhale", desc: "Exhale smoothly and steadily over 5 even seconds." }
        ]
    };

    let currentPhaseIndex = 0;
    let currentSecondsRemaining = 4;

    // Handle routine tabs
    rhythmCards.forEach(card => {
        card.addEventListener("click", () => {
            if (isBreathingActive) {
                stopBreathingSession();
            }
            rhythmCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            selectedRhythm = card.getAttribute("data-rhythm");
            resetBreathingVisuals();
        });
    });

    function resetBreathingVisuals() {
        currentPhaseIndex = 0;
        const config = rhythmsConfig[selectedRhythm];
        currentSecondsRemaining = config[0].duration;

        // Reset bubble classes
        bubbleOuter.className = "breath-bubble-outer";
        labelIndicator.textContent = "Paced";
        countdown.textContent = currentSecondsRemaining;
        
        if (selectedRhythm === "box") {
            instructions.textContent = "Box Breathing: 4s Inhale, 4s Hold, 4s Exhale, 4s Hold. Click Start.";
        } else if (selectedRhythm === "relax") {
            instructions.textContent = "4-7-8 Relax: Clinically proven sequence for grounding. Click Start.";
        } else {
            instructions.textContent = "Coherent Breathing: Slow, even 5s cycles to balance blood flow. Click Start.";
        }
    }

    function startBreathingSession() {
        isBreathingActive = true;
        playBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Pause Session`;
        playBtn.style.borderColor = "var(--neon-pink)";
        playBtn.className = "neon-btn neon-btn-secondary";
        resetBtn.disabled = false;

        runBreathingCycleStep();
    }

    function pauseBreathingSession() {
        isBreathingActive = false;
        playBtn.innerHTML = `<i class="fa-solid fa-play"></i> Resume Session`;
        playBtn.className = "neon-btn neon-btn-primary";
        
        clearInterval(breathInterval);
        clearTimeout(breathTimeout);
    }

    function stopBreathingSession() {
        isBreathingActive = false;
        playBtn.innerHTML = `<i class="fa-solid fa-play"></i> Start Session`;
        playBtn.className = "neon-btn neon-btn-primary";
        playBtn.style.borderColor = "transparent";
        resetBtn.disabled = true;

        clearInterval(breathInterval);
        clearTimeout(breathTimeout);
        resetBreathingVisuals();
    }

    function runBreathingCycleStep() {
        const config = rhythmsConfig[selectedRhythm];
        const phase = config[currentPhaseIndex];

        // Apply visual classes
        bubbleOuter.className = `breath-bubble-outer ${phase.state}`;
        labelIndicator.textContent = phase.text;
        currentSecondsRemaining = phase.duration;
        countdown.textContent = currentSecondsRemaining;
        instructions.textContent = phase.desc;

        // Timer countdown loop
        breathInterval = setInterval(() => {
            currentSecondsRemaining--;
            if (currentSecondsRemaining > 0) {
                countdown.textContent = currentSecondsRemaining;
            } else {
                clearInterval(breathInterval);
            }
        }, 1000);

        // Next phase timer trigger
        breathTimeout = setTimeout(() => {
            currentPhaseIndex = (currentPhaseIndex + 1) % config.length;
            if (isBreathingActive) {
                runBreathingCycleStep();
            }
        }, phase.duration * 1000);
    }

    // Bind playback controls
    playBtn.addEventListener("click", () => {
        if (isBreathingActive) {
            pauseBreathingSession();
        } else {
            startBreathingSession();
        }
    });

    resetBtn.addEventListener("click", () => {
        stopBreathingSession();
    });

    // Initialize defaults on start
    resetBreathingVisuals();
});
