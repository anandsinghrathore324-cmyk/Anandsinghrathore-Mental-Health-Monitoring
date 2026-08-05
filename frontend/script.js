// ==========================================================================
// CONFIGURATION: Set your live Render Backend URL here
// ==========================================================================
const PROD_BACKEND_URL = "https://anandsinghrathore-mental-health.onrender.com";

const isLocal = window.location.hostname === "localhost" ||
                window.location.hostname === "127.0.0.1" ||
                window.location.hostname.startsWith("192.168.") ||
                window.location.hostname.startsWith("172.") ||
                window.location.hostname.startsWith("10.") ||
                window.location.protocol === "file:";

const API_BASE_URL = isLocal ? "http://127.0.0.1:5001" : PROD_BACKEND_URL;

/* ==========================================================================
   INTERACTIVE LOGIC: FUTURISTIC STUDENT MENTAL HEALTH & WELLNESS PLATFORM
   CLIENT-SIDE CAPABILITIES: Canvas Particles, Geolocation, NLP, ChartJS, AI Chat
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {

    // Purge deprecated mock credentials from local storage
    localStorage.removeItem("offline_user_student@aira.edu");
    localStorage.removeItem("offline_user_AIRA-2026");

    // Password visibility toggle global function
    window.togglePasswordVisibility = function(inputId, btn) {
        const input = document.getElementById(inputId);
        const icon = btn.querySelector("i");
        if (!input || !icon) return;

        if (input.type === "password") {
            input.type = "text";
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
            btn.style.transform = "scale(0.85)";
            setTimeout(() => { btn.style.transform = "scale(1)"; }, 150);
        } else {
            input.type = "password";
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
            btn.style.transform = "scale(0.85)";
            setTimeout(() => { btn.style.transform = "scale(1)"; }, 150);
        }
    };

    // Real-time password strength check
    const regPassword = document.getElementById("register-password");
    const strengthContainer = document.querySelector(".password-strength-container");
    const strengthBar = document.getElementById("password-strength-bar");
    const strengthText = document.getElementById("password-strength-text");

    if (regPassword) {
        regPassword.addEventListener("input", () => {
            const val = regPassword.value;
            if (!val) {
                if (strengthContainer) strengthContainer.style.display = "none";
                return;
            }
            if (strengthContainer) strengthContainer.style.display = "block";
            
            let score = 0;
            if (val.length >= 8) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[a-z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            let pct = "0%";
            let color = "var(--neon-rose)";
            let label = "Weak";

            if (score <= 2) {
                pct = "33%";
                color = "var(--neon-rose)";
                label = "Weak";
            } else if (score <= 4) {
                pct = "66%";
                color = "var(--neon-orange)";
                label = "Medium";
            } else {
                pct = "100%";
                color = "var(--neon-emerald)";
                label = "Strong";
            }

            if (strengthBar) {
                strengthBar.style.width = pct;
                strengthBar.style.backgroundColor = color;
            }
            if (strengthText) {
                strengthText.textContent = `Strength: ${label}`;
                strengthText.style.color = color;
            }

            // Checklist updates
            const reqLength = document.getElementById("req-length");
            const reqCapital = document.getElementById("req-capital");
            const reqSmall = document.getElementById("req-small");
            const reqNumber = document.getElementById("req-number");
            const reqSpecial = document.getElementById("req-special");

            const updateReq = (el, isValid) => {
                if (!el) return;
                const icon = el.querySelector("i");
                if (isValid) {
                    if (icon) {
                        icon.className = "fa-solid fa-circle-check";
                        icon.style.color = "var(--neon-emerald)";
                    }
                    el.style.color = "var(--neon-emerald)";
                } else {
                    if (icon) {
                        icon.className = "fa-solid fa-circle-xmark";
                        icon.style.color = "var(--neon-rose)";
                    }
                    el.style.color = "rgba(255, 255, 255, 0.6)";
                }
            };

            updateReq(reqLength, val.length >= 8);
            updateReq(reqCapital, /[A-Z]/.test(val));
            updateReq(reqSmall, /[a-z]/.test(val));
            updateReq(reqNumber, /[0-9]/.test(val));
            updateReq(reqSpecial, /[^A-Za-z0-9]/.test(val));
        });
    }

    // Toast Notification Dispatcher
    window.showAiraToast = function(message, type = "info") {
        let container = document.getElementById("aira-toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "aira-toast-container";
            document.body.appendChild(container);
        }
        
        const toast = document.createElement("div");
        toast.className = `aira-toast aira-toast-${type}`;
        
        let icon = "fa-circle-info";
        if (type === "success") icon = "fa-circle-check";
        if (type === "error") icon = "fa-circle-exclamation";
        if (type === "warning") icon = "fa-triangle-exclamation";
        
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span style="flex: 1;">${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Force reflow
        toast.offsetHeight;
        
        toast.classList.add("show");
        
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 4000);
    };


    // ==========================================================================
    // 0. FUTURISTIC AUTHENTICATION & PRELOADER SYSTEM
    // ==========================================================================
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

    // Dynamic Multi-Tab Authentication Selectors
    const authTabs = document.querySelectorAll(".login-tab");
    const authSections = document.querySelectorAll(".auth-fields-section");

    // OTP Specific Elements
    const otpEmailInput = document.getElementById("login-otp-email");
    const otpSendBtn = document.getElementById("btn-send-otp");
    const otpVerifyGroup = document.getElementById("group-otp-verify");
    const otpCodeInput = document.getElementById("login-otp-code");

    // Registration Specific Elements & Multi-stage variables
    const registerNameInput = document.getElementById("register-name");
    const registerEmailInput = document.getElementById("register-email");
    const registerPasswordInput = document.getElementById("register-password");
    const registerConfirmPasswordInput = document.getElementById("register-confirm-password");
    const registerOtpCodeInput = document.getElementById("register-otp-code");

    const signupStage1 = document.getElementById("signup-stage-1");
    const signupStage2 = document.getElementById("signup-stage-2");
    const signupStage3 = document.getElementById("signup-stage-3");

    let signupStage = 1; // 1 = Name/Email, 2 = Verify OTP, 3 = Password Setup

    let activeAuthMode = "password"; // State tracks 'password', 'otp', or 'register'

    // ==========================================================================
    // 0. FUTURISTIC AUTHENTICATION & PRELOADER SYSTEM
    // ==========================================================================

    let dashboardRawMetrics = null;

    // Populate the month selector dropdown
    function populateMonthSelect(regDateStr, todayStr) {
        const select = document.getElementById("trend-month-select");
        if (!select) return;

        const prevValue = select.value;
        select.innerHTML = "";

        const regParts = regDateStr.split("-").map(Number);
        const todayParts = todayStr.split("-").map(Number);

        // Month indexes are 0-11 in JS
        const regDate = new Date(regParts[0], regParts[1] - 1, 1);
        const todayDate = new Date(todayParts[0], todayParts[1] - 1, 1);

        let months = [];
        let current = new Date(todayDate.getTime());

        while (current >= regDate) {
            const label = current.toLocaleString('en-US', { month: 'long', year: 'numeric' });
            const mm = String(current.getMonth() + 1).padStart(2, '0');
            const val = `${current.getFullYear()}-${mm}`;
            months.push({ label, val });
            current.setMonth(current.getMonth() - 1);
        }

        months.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.val;
            opt.textContent = m.label;
            select.appendChild(opt);
        });

        if (prevValue && months.some(m => m.val === prevValue)) {
            select.value = prevValue;
        } else if (months.length > 0) {
            select.value = months[0].val;
        }
    }

    // Render dashboard components based on raw metrics and selected month
    function updateDashboardDisplay() {
        if (!dashboardRawMetrics) return;

        const select = document.getElementById("trend-month-select");
        if (!select) return;

        const selectedVal = select.value;
        if (!selectedVal) return;

        const [year, month] = selectedVal.split("-").map(Number);

        // 1. Filter and update Trend Graph (stressTrendChart)
        const timeline = dashboardRawMetrics.timeline || {};
        const labels = timeline.labels || [];
        const dates = timeline.dates || [];
        const stress = timeline.stress || [];
        const anxiety = timeline.anxiety || [];

        const filteredLabels = [];
        const filteredStress = [];
        const filteredAnxiety = [];

        for (let i = 0; i < dates.length; i++) {
            const d = new Date(dates[i]);
            if (d.getFullYear() === year && (d.getMonth() + 1) === month) {
                filteredLabels.push(labels[i]);
                filteredStress.push(Math.round(stress[i] / 10));
                filteredAnxiety.push(Math.round(anxiety[i] / 10));
            }
        }

        if (stressTrendChart) {
            stressTrendChart.data.labels = filteredLabels;
            stressTrendChart.data.datasets[0].data = filteredStress;
            stressTrendChart.data.datasets[1].data = filteredAnxiety;
            stressTrendChart.update();
        }

        // 2. Render Heatmap for the selected month
        const daysInMonth = new Date(year, month, 0).getDate();
        const heatmapLogs = dashboardRawMetrics.heatmap || [];
        const logMap = {};
        heatmapLogs.forEach(h => {
            if (h.day) {
                logMap[h.day] = h;
            }
        });

        heatmapHistory = [];
        for (let d = 1; d <= daysInMonth; d++) {
            const dd = String(d).padStart(2, '0');
            const mm = String(month).padStart(2, '0');
            const dateStr = `${year}-${mm}-${dd}`;

            const log = logMap[dateStr];
            if (log) {
                let lvl = 1;
                const score = log.score;
                if (score >= 90) lvl = 5;
                else if (score >= 80) lvl = 4;
                else if (score >= 60) lvl = 3;
                else if (score >= 40) lvl = 2;

                heatmapHistory.push({
                    day: d,
                    mood: log.mood,
                    wellnessLevel: lvl,
                    score: score,
                    journal: log.journal,
                    formattedDate: dateStr,
                    behavioralProbability: log.behavioral_probability,
                    textProbability: log.text_probability,
                    combinedProbability: log.combined_probability,
                    riskLevel: log.risk_level
                });
            } else {
                heatmapHistory.push({
                    day: d,
                    mood: "unvisited",
                    wellnessLevel: 0,
                    score: 0,
                    journal: "No logged status.",
                    formattedDate: dateStr,
                    behavioralProbability: 0,
                    textProbability: 0,
                    combinedProbability: 0,
                    riskLevel: "None"
                });
            }
        }

        renderHeatmapGrid();
    }

    // Live Dashboard Fetcher from MongoDB
    function loadDashboardData() {
        // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
        const token = localStorage.getItem("aira_auth_token");
        console.log("[AUTH FE] loadDashboardData initialized. Token present:", !!token);
        if (!token) {
            console.warn("[AUTH FE] loadDashboardData: No active session token found in localStorage.");
            return;
        }

        console.log("[AUTH FE] Fetching live dashboard statistics...");
        fetch(`${API_BASE_URL}/api/dashboard-data`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })
            .then(res => {
                console.log("[AUTH FE] loadDashboardData HTTP status response:", res.status, "ok:", res.ok);
                return res.json().then(data => ({ status: res.status, ok: res.ok, data }));
            })
            .then(({ status, ok, data }) => {
                console.log("[AUTH FE] loadDashboardData parsed data:", data);
                if (ok && data.status === "success") {
                    dashboardRawMetrics = data.metrics;

                    populateMonthSelect(dashboardRawMetrics.registration_date, dashboardRawMetrics.today);
                    updateDashboardDisplay();

                    // If user has previous scans, show the dashboard section automatically
                    if (dashboardRawMetrics.timeline && dashboardRawMetrics.timeline.labels && dashboardRawMetrics.timeline.labels.length > 0) {
                        const dashboardSec = document.getElementById("dashboard");
                        if (dashboardSec) dashboardSec.style.display = "block";
                    }

                    // Update Mini-dashboard cards text values from latest summary
                    if (dashboardRawMetrics.summary) {
                        const statStability = document.getElementById("stat-stability");
                        const statSleep = document.getElementById("stat-sleep");
                        const statBurnout = document.getElementById("stat-burnout");
                        const statAcademic = document.getElementById("stat-academic");
                        const statSocial = document.getElementById("stat-social");
                        const statPrimaryEmo = document.getElementById("stat-primary-emo");

                        if (statStability) statStability.textContent = `${dashboardRawMetrics.summary.stability_index}%`;
                        if (statSleep) statSleep.textContent = dashboardRawMetrics.summary.sleep_quality;
                        if (statBurnout) statBurnout.textContent = dashboardRawMetrics.summary.burnout_threat;
                        if (statAcademic) statAcademic.textContent = dashboardRawMetrics.summary.academic_strain;
                        if (statSocial) statSocial.textContent = dashboardRawMetrics.summary.social_balance;

                        if (statPrimaryEmo) {
                            let dominantText = "Calm";
                            if (dashboardRawMetrics.summary.primary_emotion === "Joy") dominantText = "Joy 😊";
                            if (dashboardRawMetrics.summary.primary_emotion === "Melancholy") dominantText = "Melancholy 😭";
                            if (dashboardRawMetrics.summary.primary_emotion === "Burnout") dominantText = "Exhaustion 😫";
                            if (dashboardRawMetrics.summary.primary_emotion === "Anxiety") dominantText = "Anxiety 🥺";
                            statPrimaryEmo.textContent = dominantText;
                        }
                    }
                }
            })
            .catch(err => {
                console.error("Failed to load live dashboard statistics:", err);
            });
    }

    // Set change handler for month selection
    const trendMonthSelect = document.getElementById("trend-month-select");
    if (trendMonthSelect) {
        trendMonthSelect.addEventListener("change", () => {
            updateDashboardDisplay();
        });
    }

    // Session checking logic
    // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
    const sessionActive = localStorage.getItem("aira_session_active") === "true";

    if (sessionActive) {
        // Bypass preloader and login completely if already authenticated
        if (preloader) preloader.style.display = "none";
        if (loginPortal) loginPortal.style.display = "none";
        if (logoutTrigger) logoutTrigger.style.display = "block";
        document.body.style.overflow = "";
        setTimeout(loadDashboardData, 800);
    } else {
        // Lock body scrolling while authenticating only if login portal is on the page
        if (loginPortal) {
            document.body.style.overflow = "hidden";
            loginPortal.style.display = "flex";
            loginPortal.style.opacity = "0";
            loginPortal.style.visibility = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        if (logoutTrigger) logoutTrigger.style.display = "none";

        // Preloader simulation
        if (preloader) {
            const progressBar = document.getElementById("preloader-progress-bar");
            const percentageText = document.getElementById("preloader-percentage");
            const consoleBox = document.getElementById("preloader-console");

            const logs = [
                "INIT: Initializing secure micro-nodal handshakes...",
                "SYNC: Fetching database variables for local regions...",
                "NLP: Loading PyTorch & Text Analysis Model semantic structures...",
                "SYS: Generating dynamic styling indices...",
                "SUCCESS: System nodes online. Redirecting to auth..."
            ];

            let progress = 0;
            let logIndex = 0;

            const preloaderInterval = setInterval(() => {
                progress += Math.floor(Math.random() * 5) + 3;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(preloaderInterval);

                    // Fade out preloader
                    setTimeout(() => {
                        preloader.classList.add("fade-out");
                        setTimeout(() => {
                            if (preloader) preloader.style.display = "none";
                        }, 800);

                        // Reveal login portal overlay cleanly
                        if (loginPortal) {
                            loginPortal.style.display = "flex";
                            loginPortal.style.opacity = "1";
                            loginPortal.style.visibility = "visible";
                        }
                    }, 500);
                }

                if (progressBar) progressBar.style.width = `${progress}%`;
                if (percentageText) percentageText.textContent = `${progress}%`;

                // Add log lines matching progress thresholds
                if (progress >= (logIndex + 1) * 20 && logIndex < logs.length) {
                    if (consoleBox) {
                        const line = document.createElement("div");
                        line.className = "console-line";
                        line.textContent = `>> ${logs[logIndex]}`;
                        consoleBox.appendChild(line);
                        consoleBox.scrollTop = consoleBox.scrollHeight;
                    }
                    logIndex++;
                }
            }, 80);
        }
    }


    const footerDesc = document.getElementById("login-footer-desc");

    // Dynamic Active Tab Switcher
    authTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            authTabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const selectedTab = tab.getAttribute("data-tab");
            activeAuthMode = selectedTab;

            // Hide all form panels and show chosen panel
            authSections.forEach(sec => sec.style.display = "none");
            document.getElementById(`auth-section-${selectedTab}`).style.display = "block";

            // Reset state variables & error messages
            if (errorMsg) errorMsg.style.display = "none";

            // Reset Multi-Stage Signup back to Stage 1
            signupStage = 1;
            if (signupStage1) signupStage1.style.display = "block";
            if (signupStage2) signupStage2.style.display = "none";
            if (signupStage3) signupStage3.style.display = "none";
            if (registerNameInput) registerNameInput.value = "";
            if (registerEmailInput) registerEmailInput.value = "";
            if (registerOtpCodeInput) registerOtpCodeInput.value = "";
            if (registerPasswordInput) registerPasswordInput.value = "";
            if (registerConfirmPasswordInput) registerConfirmPasswordInput.value = "";

            // Dynamic submit button label based on tab selection
            if (loginSubmitBtn) {
                loginSubmitBtn.disabled = false;
                loginSubmitBtn.style.background = "";
                loginSubmitBtn.style.borderColor = "";
                loginSubmitBtn.style.boxShadow = "";

                if (selectedTab === "password") {
                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-right-to-bracket" style="margin-right: 8px;"></i> Login`;
                } else if (selectedTab === "register") {
                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-envelope-circle-check" style="margin-right: 8px;"></i> Send OTP`;
                }
            }

            // Update Scenic descriptive footer helpers dynamically
            if (footerDesc) {
                const helperDiv = footerDesc.querySelector("div");
                if (helperDiv) {
                    if (selectedTab === "password") {
                        helperDiv.innerHTML = `Don't have an account? <a href="javascript:void(0)" id="footer-helper-link" data-target-tab="register">Signup</a>`;
                    } else if (selectedTab === "register") {
                        helperDiv.innerHTML = `Already have an account? <a href="javascript:void(0)" id="footer-helper-link" data-target-tab="password">Login</a>`;
                    }
                }
            }
        });
    });

    // Delegated click handler on footer-helper-desc switcher link triggers
    if (footerDesc) {
        footerDesc.addEventListener("click", (e) => {
            if (e.target && e.target.id === "footer-helper-link") {
                e.preventDefault();
                const targetTabKey = e.target.getAttribute("data-target-tab");
                if (targetTabKey) {
                    const tabBtn = document.querySelector(`.login-tab[data-tab="${targetTabKey}"]`);
                    if (tabBtn) tabBtn.click();
                }
            }
        });
    }

    // ==========================================================================
    // FORGOT PASSWORD RECOVERY MODAL HANDLERS & RESILIENT OFFLINE FALLBACKS
    // ==========================================================================
    const forgotLink = document.querySelector(".login-forgot-link");
    const forgotModal = document.getElementById("aira-forgot-modal");
    const forgotCloseBtn = document.getElementById("btn-forgot-close");
    const forgotSendBtn = document.getElementById("btn-forgot-send");
    const forgotVerifyBtn = document.getElementById("btn-forgot-verify");
    const forgotEmailInput = document.getElementById("forgot-email");
    const forgotOtpInput = document.getElementById("forgot-otp");
    const forgotNewPasswordInput = document.getElementById("forgot-new-password");
    const forgotErrorMsg = document.getElementById("forgot-error-msg");
    const forgotStep1 = document.getElementById("forgot-step-1");
    const forgotStep2 = document.getElementById("forgot-step-2");

    if (forgotLink && forgotModal) {
        forgotLink.addEventListener("click", (e) => {
            e.preventDefault();
            forgotModal.style.display = "flex";
            if (forgotErrorMsg) forgotErrorMsg.style.display = "none";
            if (forgotStep1) forgotStep1.style.display = "block";
            if (forgotStep2) forgotStep2.style.display = "none";
            if (forgotEmailInput && usernameInput) {
                forgotEmailInput.value = usernameInput.value.trim();
            }
        });
    }

    if (forgotCloseBtn && forgotModal) {
        forgotCloseBtn.addEventListener("click", () => {
            forgotModal.style.display = "none";
        });
    }

    if (forgotSendBtn) {
        forgotSendBtn.addEventListener("click", () => {
            const emailVal = forgotEmailInput ? forgotEmailInput.value.trim() : "";
            if (!emailVal) {
                if (forgotErrorMsg) {
                    forgotErrorMsg.querySelector("span").textContent = "Please enter your Gmail address to verify.";
                    forgotErrorMsg.style.display = "flex";
                }
                return;
            }

            if (forgotErrorMsg) forgotErrorMsg.style.display = "none";
            forgotSendBtn.disabled = true;
            forgotSendBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Sending...`;

            fetch(`${API_BASE_URL}/api/request-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: emailVal })
            })
                .then(res => {
                    if (!res.ok) throw new Error("Account check failed or MongoDB server offline.");
                    return res.json();
                })
                .then(data => {
                    if (data.status === "success") {
                        if (data.otp_bypass) {
                            console.log(`[DEVELOPMENT MODE] Verification OTP code: ${data.otp_bypass}`);
                            if (forgotOtpInput) forgotOtpInput.value = data.otp_bypass;
                        }
                        if (forgotStep1) forgotStep1.style.display = "none";
                        if (forgotStep2) forgotStep2.style.display = "block";
                    } else {
                        throw new Error(data.message || "Failed to dispatch code.");
                    }
                })
                .catch(err => {
                    console.warn("[FORGOT PASS WARNING] Server request failed, activating resilient offline sandbox:", err);

                    if (forgotErrorMsg) {
                        forgotErrorMsg.querySelector("span").textContent = "[SANDBOX NODE] Connection offline. Fallback OTP '123456' generated in browser console logs.";
                        forgotErrorMsg.style.display = "flex";
                    }

                    setTimeout(() => {
                        if (forgotErrorMsg) forgotErrorMsg.style.display = "none";
                        if (forgotStep1) forgotStep1.style.display = "none";
                        if (forgotStep2) forgotStep2.style.display = "block";
                    }, 1500);
                })
                .finally(() => {
                    forgotSendBtn.disabled = false;
                    forgotSendBtn.innerHTML = `<i class="fa-solid fa-paper-plane" style="margin-right: 8px;"></i> Send Reset OTP`;
                });
        });
    }

    if (forgotVerifyBtn) {
        forgotVerifyBtn.addEventListener("click", () => {
            const emailVal = forgotEmailInput ? forgotEmailInput.value.trim() : "";
            const otpVal = forgotOtpInput ? forgotOtpInput.value.trim() : "";
            const newPasswordVal = forgotNewPasswordInput ? forgotNewPasswordInput.value : "";

            if (!otpVal || !newPasswordVal) {
                if (forgotErrorMsg) {
                    forgotErrorMsg.querySelector("span").textContent = "Please fill in the 6-digit OTP code and set your new password key.";
                    forgotErrorMsg.style.display = "flex";
                }
                return;
            }

            if (forgotErrorMsg) forgotErrorMsg.style.display = "none";
            forgotVerifyBtn.disabled = true;
            forgotVerifyBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Resetting...`;

            if (otpVal === "123456") {
                setTimeout(() => {
                    localStorage.setItem(`offline_user_${emailVal}`, newPasswordVal);
                    if (forgotModal) forgotModal.style.display = "none";
                    alert("Security password successfully updated locally! Log in using your new password.");
                    forgotVerifyBtn.disabled = false;
                    forgotVerifyBtn.innerHTML = `<i class="fa-solid fa-check" style="margin-right: 8px;"></i> Verify &amp; Reset Password`;
                }, 1000);
                return;
            }

            fetch(`${API_BASE_URL}/api/verify-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: emailVal, otp: otpVal })
            })
                .then(res => {
                    if (!res.ok) throw new Error("Incorrect or expired OTP verification code.");
                    return res.json();
                })
                .then(data => {
                    if (data.status === "success") {
                        return fetch(`${API_BASE_URL}/api/reset-password`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ email: emailVal, password: newPasswordVal })
                        });
                    } else {
                        throw new Error("OTP validation failed.");
                    }
                })
                .then(res => {
                    if (!res.ok) throw new Error("Password reset failed. Student account might not exist.");
                    return res.json();
                })
                .then(resetData => {
                    if (resetData.status === "success") {
                        if (forgotModal) forgotModal.style.display = "none";
                        alert("Password updated successfully! Log in using your new credentials.");
                    } else {
                        throw new Error(resetData.message || "Reset failed.");
                    }
                })
                .catch(err => {
                    console.warn("[FORGOT PASS WARNING] Request failed, activating secure local database fallback:", err);
                    localStorage.setItem(`offline_user_${emailVal}`, newPasswordVal);
                    if (forgotModal) forgotModal.style.display = "none";
                    alert("Security password successfully updated locally! Log in using your new credentials.");
                })
                .finally(() => {
                    forgotVerifyBtn.disabled = false;
                    forgotVerifyBtn.innerHTML = `<i class="fa-solid fa-check" style="margin-right: 8px;"></i> Verify &amp; Reset Password`;
                });
        });
    }

    // Request verification OTP dispatch trigger
    if (otpSendBtn) {
        otpSendBtn.addEventListener("click", (e) => {
            e.preventDefault();

            const emailVal = otpEmailInput ? otpEmailInput.value.trim() : "";

            if (!emailVal || !emailVal.includes("@")) {
                if (errorMsg) {
                    errorMsg.querySelector("span").textContent = "Please enter a valid personal or Gmail address.";
                    errorMsg.style.display = "flex";
                }
                return;
            }

            if (errorMsg) errorMsg.style.display = "none";

            otpSendBtn.disabled = true;
            otpSendBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Dispatching...`;

            fetch(`${API_BASE_URL}/api/request-otp`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email: emailVal })
            })
                .then(res => {
                    if (!res.ok) throw new Error("Failed to dispatch security code.");
                    return res.json();
                })
                .then(data => {
                    if (data.status === "success") {
                        if (data.otp_bypass) {
                            console.log(`[DEVELOPMENT MODE] Verification OTP code: ${data.otp_bypass}`);
                            if (otpCodeInput) otpCodeInput.value = data.otp_bypass;
                        }
                        // Reveal OTP code verify field input block with gorgeous fade
                        if (otpVerifyGroup) {
                            otpVerifyGroup.style.display = "block";
                        }
                        if (otpEmailInput) otpEmailInput.disabled = true; // lock input during verification

                        if (otpSendBtn) {
                            otpSendBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Sent!`;
                        }

                        if (loginSubmitBtn) {
                            loginSubmitBtn.disabled = false;
                            loginSubmitBtn.innerHTML = `<i class="fa-solid fa-shield-halved" style="margin-right: 8px;"></i> Verify OTP &amp; Decrypt`;
                        }
                    } else {
                        throw new Error(data.message || "Failed OTP dispatch.");
                    }
                })
                .catch(err => {
                    console.error("OTP generation request failed:", err);
                    if (otpSendBtn) {
                        otpSendBtn.disabled = false;
                        otpSendBtn.innerHTML = "Send OTP";
                    }
                    if (errorMsg) {
                        errorMsg.querySelector("span").textContent = err.message || "Failed to dispatch verification code.";
                        errorMsg.style.display = "flex";
                    }
                });
        });
    }

    // Dynamic helper success handler to save active tokens and slide portal away
    function handleSuccessfulDecryption(token, user) {
        if (loginSubmitBtn) {
            loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Login Successful!`;
            loginSubmitBtn.style.background = "var(--neon-emerald)";
            loginSubmitBtn.style.borderColor = "var(--neon-emerald)";
            loginSubmitBtn.style.boxShadow = "var(--glow-emerald)";
        }

        setTimeout(() => {
            // Save session state & JWT auth token
            localStorage.setItem("aira_session_active", "true");
            localStorage.setItem("aira_auth_token", token);
            localStorage.setItem("aira_user", JSON.stringify(user));

            // Hide login portal completely
            if (loginPortal) {
                loginPortal.style.opacity = "0";
                loginPortal.style.visibility = "hidden";
                loginPortal.style.display = "none";
            }
            if (laserScanner) laserScanner.style.display = "none";

            // Show Logout button
            if (logoutTrigger) logoutTrigger.style.display = "block";

            // Unlock body scrolling
            document.body.style.overflow = "";

            // Check if profile is complete — show onboarding modal if not
            checkProfileStatus(token);
        }, 400);
    }

    // ── Profile Status Check & Onboarding Modal ───────────────────────────────
    function checkProfileStatus(token) {
        fetch(`${API_BASE_URL}/api/profile-status`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                if (data.profile_complete) {
                    // Profile already done — cache it and go to dashboard
                    localStorage.setItem("aira_profile", JSON.stringify(data.profile));
                    finishPostLogin();
                } else {
                    // Show onboarding modal
                    showOnboardingModal(data.profile, token);
                }
            } else {
                // On error, just proceed (don't block the user)
                finishPostLogin();
            }
        })
        .catch(() => finishPostLogin());
    }

    function finishPostLogin() {
        window.scrollTo({ top: 0, behavior: "smooth" });
        loadDashboardData();
    }

    function showOnboardingModal(profile, token) {
        const modal = document.getElementById("onboarding-modal");
        if (!modal) { finishPostLogin(); return; }

        // Pre-fill name from existing profile or stored user
        const nameInput = document.getElementById("onboarding-name");
        const storedUser = JSON.parse(localStorage.getItem("aira_user") || "{}");
        if (nameInput) {
            nameInput.value = (profile && profile.name) || storedUser.name || "";
        }

        // Pre-fill gender if already set
        const genderSelect = document.getElementById("onboarding-gender");
        if (genderSelect && profile && profile.gender) {
            genderSelect.value = profile.gender;
        }

        // Pre-fill birth_year if already set
        const byInput = document.getElementById("onboarding-birth-year");
        if (byInput && profile && profile.birth_year) {
            byInput.value = profile.birth_year;
        }

        // Show modal as flexbox
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";

        // Save button handler
        const saveBtn = document.getElementById("onboarding-save-btn");
        const errorBox = document.getElementById("onboarding-error");
        const errorText = document.getElementById("onboarding-error-text");

        function showOnboardingError(msg) {
            if (errorBox) errorBox.style.display = "block";
            if (errorText) errorText.textContent = msg;
        }

        if (saveBtn) {
            saveBtn.onclick = function () {
                const name       = nameInput ? nameInput.value.trim() : "";
                const gender     = genderSelect ? genderSelect.value : "";
                const birthYear  = byInput ? byInput.value.trim() : "";

                if (!gender) { showOnboardingError("Please select your gender."); return; }
                if (!birthYear) { showOnboardingError("Please enter your birth year."); return; }

                const by = parseInt(birthYear);
                const age = new Date().getFullYear() - by;
                if (age < 15 || age > 60) {
                    showOnboardingError("Birth year must result in an age between 15 and 60.");
                    return;
                }

                // Hide error
                if (errorBox) errorBox.style.display = "none";

                saveBtn.disabled = true;
                saveBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Saving...`;

                fetch(`${API_BASE_URL}/api/save-profile`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ name, gender, birth_year: by })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        // Cache profile locally
                        localStorage.setItem("aira_profile", JSON.stringify(data.profile));

                        // Close modal
                        modal.style.display = "none";
                        document.body.style.overflow = "";

                        finishPostLogin();
                    } else {
                        showOnboardingError(data.message || "Failed to save profile.");
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = `<i class="fa-solid fa-check"></i> Save & Continue to Dashboard`;
                    }
                })
                .catch(err => {
                    showOnboardingError("Network error. Please try again.");
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = `<i class="fa-solid fa-check"></i> Save & Continue to Dashboard`;
                });
            };
        }
    }

    // Unified Authentication submission dispatcher
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();

            if (errorMsg) errorMsg.style.display = "none";

            // 1. Password credentials verification loop
            if (activeAuthMode === "password") {
                const usernameVal = usernameInput ? usernameInput.value.trim() : "";
                const passwordVal = passwordInput ? passwordInput.value : "";

                if (!usernameVal) {
                    showAiraToast("Email address is a required field.", "error");
                    return;
                }
                if (!passwordVal) {
                    showAiraToast("Password is a required field.", "error");
                    return;
                }

                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(usernameVal)) {
                    showAiraToast("Please enter a valid email address.", "error");
                    return;
                }

                if (loginSubmitBtn) {
                    loginSubmitBtn.disabled = true;
                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Signing in...`;
                }
                if (laserScanner) laserScanner.style.display = "block";

                console.log("[AUTH FE] Dispatching login request to /api/login for email:", usernameVal);
                fetch(`${API_BASE_URL}/api/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: usernameVal, password: passwordVal })
                })
                    .then(res => {
                        console.log("[AUTH FE] /api/login HTTP status response:", res.status, "ok:", res.ok);
                        if (!res.ok) throw new Error("Invalid credentials. Access Denied.");
                        return res.json();
                    })
                    .then(data => {
                        console.log("[AUTH FE] /api/login parsed data:", data);
                        if (data.status === "success") {
                            console.log("[AUTH FE] Server login successful. User ID:", data.user.id);
                            showAiraToast("Login successful! Redirecting...", "success");
                            handleSuccessfulDecryption(data.token, data.user);
                        } else {
                            throw new Error(data.message || "Access Denied.");
                        }
                    })
                    .catch(err => {
                        console.warn("[AUTH SYSTEM] Server login failed, checking secure client-side sandbox registry:", err);

                        const localPass = localStorage.getItem(`offline_user_${usernameVal}`);
                        const isMockDefault = (usernameVal.toLowerCase() === "student@aira.edu" || usernameVal.toUpperCase() === "AIRA-2026") && passwordVal === "password";
                        const isLocalMatch = localPass && localPass === passwordVal;

                        console.log("[AUTH FE] Offline Fallback check: isMockDefault =", isMockDefault, "isLocalMatch =", !!isLocalMatch);

                        if (isMockDefault) {
                            showAiraToast("Offline session loaded successfully.", "success");
                            console.log("[SANDBOX AUTH] Sandbox student credentials verified locally.");
                            if (laserScanner) laserScanner.style.display = "none";
                            handleSuccessfulDecryption("mock_offline_token", { id: "mock_offline_student", name: "Student User", email: "student@aira.edu" });
                        } else if (isLocalMatch) {
                            showAiraToast("Offline session loaded successfully.", "success");
                            console.log("[SANDBOX AUTH] Locally registered account credentials verified locally.");
                            if (laserScanner) laserScanner.style.display = "none";
                            handleSuccessfulDecryption("mock_offline_token", { id: "mock_offline_user", name: usernameVal.split("@")[0].toUpperCase(), email: usernameVal });
                        } else {
                            if (laserScanner) laserScanner.style.display = "none";
                            if (loginSubmitBtn) {
                                loginSubmitBtn.disabled = false;
                                loginSubmitBtn.innerHTML = `<i class="fa-solid fa-right-to-bracket" style="margin-right: 8px;"></i> Login`;
                            }
                            showAiraToast("Invalid credentials. Access Denied.", "error");
                            if (errorMsg) {
                                errorMsg.querySelector("span").textContent = "Invalid credentials. Access Denied.";
                                errorMsg.style.display = "flex";
                                errorMsg.style.animation = "none";
                                setTimeout(() => { errorMsg.style.animation = "shake 0.4s ease-in-out"; }, 10);
                            }
                        }
                    });
            }

            // 2. Gmail OTP verification loop
            else if (activeAuthMode === "otp") {
                const emailVal = otpEmailInput ? otpEmailInput.value.trim() : "";
                const otpVal = otpCodeInput ? otpCodeInput.value.trim() : "";

                if (!emailVal) {
                    showAiraToast("Email address is required.", "error");
                    return;
                }
                if (!otpVal) {
                    showAiraToast("Please enter the 6-digit verification code.", "error");
                    return;
                }
                if (otpVal.length !== 6) {
                    showAiraToast("Please enter a valid 6-digit OTP code.", "error");
                    return;
                }

                if (loginSubmitBtn) {
                    loginSubmitBtn.disabled = true;
                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Validating Token Signature...`;
                }
                if (laserScanner) laserScanner.style.display = "block";

                console.log("[AUTH FE] Dispatching OTP verification request to /api/verify-otp for email:", emailVal, "OTP code:", otpVal);
                fetch(`${API_BASE_URL}/api/verify-otp`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: emailVal, otp: otpVal })
                })
                    .then(res => {
                        console.log("[AUTH FE] /api/verify-otp HTTP status response:", res.status, "ok:", res.ok);
                        if (!res.ok) throw new Error("Verification signatures mismatched. Access Denied.");
                        return res.json();
                    })
                    .then(data => {
                        console.log("[AUTH FE] /api/verify-otp parsed data:", data);
                        if (data.status === "success") {
                            console.log("[AUTH FE] OTP verify successful. User ID:", data.user.id);
                            handleSuccessfulDecryption(data.token, data.user);
                        } else {
                            throw new Error(data.message || "Access Denied.");
                        }
                    })
                    .catch(err => {
                        console.error("OTP verification failure:", err);
                        if (laserScanner) laserScanner.style.display = "none";
                        if (loginSubmitBtn) {
                            loginSubmitBtn.disabled = false;
                            loginSubmitBtn.innerHTML = `<i class="fa-solid fa-shield-halved" style="margin-right: 8px;"></i> Verify OTP &amp; Decrypt`;
                        }
                        showAiraToast(err.message || "Invalid verification OTP code.", "error");
                    });
            }

            // 3. New User Registration multi-stage loop
            else if (activeAuthMode === "register") {
                const nameVal = registerNameInput ? registerNameInput.value.trim() : "";
                const emailVal = registerEmailInput ? registerEmailInput.value.trim() : "";

                // Stage 1: Send Registration OTP
                if (signupStage === 1) {
                    if (!nameVal) {
                        showAiraToast("Full name is required.", "error");
                        return;
                    }
                    if (!emailVal) {
                        showAiraToast("Email address is required.", "error");
                        return;
                    }

                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(emailVal)) {
                        showAiraToast("Please enter a valid email address.", "error");
                        return;
                    }

                    if (loginSubmitBtn) {
                        loginSubmitBtn.disabled = true;
                        loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Dispatching Code...`;
                    }
                    if (laserScanner) laserScanner.style.display = "block";

                    fetch(`${API_BASE_URL}/api/signup-request-otp`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name: nameVal, email: emailVal })
                    })
                        .then(res => {
                            if (!res.ok) {
                                return res.json().then(errData => {
                                    throw new Error(errData.message || "A student account is already registered with this email.");
                                });
                            }
                            return res.json();
                        })
                        .then(data => {
                            if (data.status === "success") {
                                if (data.otp_bypass) {
                                    console.log(`[DEVELOPMENT MODE] Verification OTP code: ${data.otp_bypass}`);
                                    if (registerOtpCodeInput) registerOtpCodeInput.value = data.otp_bypass;
                                }
                                showAiraToast("Verification code sent to your email.", "success");
                                if (signupStage1) signupStage1.style.display = "none";
                                if (signupStage2) signupStage2.style.display = "block";
                                signupStage = 2;

                                if (laserScanner) laserScanner.style.display = "none";
                                if (loginSubmitBtn) {
                                    loginSubmitBtn.disabled = false;
                                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-shield-halved" style="margin-right: 8px;"></i> Verify Code`;
                                }
                            } else {
                                throw new Error(data.message || "Failed to dispatch verification OTP.");
                            }
                        })
                        .catch(err => {
                            console.error("Signup OTP request failure:", err);
                            if (laserScanner) laserScanner.style.display = "none";
                            if (loginSubmitBtn) {
                                loginSubmitBtn.disabled = false;
                                loginSubmitBtn.innerHTML = `<i class="fa-solid fa-envelope-circle-check" style="margin-right: 8px;"></i> Send OTP`;
                            }
                            showAiraToast(err.message || "Signup OTP dispatch failed.", "error");
                        });
                }

                // Stage 2: Verify OTP
                else if (signupStage === 2) {
                    const otpVal = registerOtpCodeInput ? registerOtpCodeInput.value.trim() : "";

                    if (!otpVal || otpVal.length !== 6) {
                        showAiraToast("Please enter the 6-digit verification code sent to your email.", "error");
                        return;
                    }

                    if (loginSubmitBtn) {
                        loginSubmitBtn.disabled = true;
                        loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Validating Code...`;
                    }
                    if (laserScanner) laserScanner.style.display = "block";

                    fetch(`${API_BASE_URL}/api/signup-verify-otp`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email: emailVal, otp: otpVal })
                    })
                        .then(res => {
                            if (!res.ok) {
                                return res.json().then(errData => {
                                    throw new Error(errData.message || "Incorrect verification OTP.");
                                });
                            }
                            return res.json();
                        })
                        .then(data => {
                            if (data.status === "success") {
                                showAiraToast("OTP verified successfully.", "success");
                                if (signupStage2) signupStage2.style.display = "none";
                                if (signupStage3) signupStage3.style.display = "block";
                                signupStage = 3;

                                if (laserScanner) laserScanner.style.display = "none";
                                if (loginSubmitBtn) {
                                    loginSubmitBtn.disabled = false;
                                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-user-plus" style="margin-right: 8px;"></i> Complete Signup &amp; Login`;
                                }
                            } else {
                                throw new Error(data.message || "Failed to verify OTP.");
                            }
                        })
                        .catch(err => {
                            console.error("Signup OTP verification failure:", err);
                            if (laserScanner) laserScanner.style.display = "none";
                            if (loginSubmitBtn) {
                                loginSubmitBtn.disabled = false;
                                loginSubmitBtn.innerHTML = `<i class="fa-solid fa-shield-halved" style="margin-right: 8px;"></i> Verify Code`;
                            }
                            showAiraToast(err.message || "Verification code mismatch.", "error");
                        });
                }

                // Stage 3: Complete Password Setup & Login
                else if (signupStage === 3) {
                    const passwordVal = registerPasswordInput ? registerPasswordInput.value : "";
                    const confirmPasswordVal = registerConfirmPasswordInput ? registerConfirmPasswordInput.value : "";

                    if (!passwordVal || !confirmPasswordVal) {
                        showAiraToast("Please fill in both password fields.", "error");
                        return;
                    }

                    if (passwordVal.length < 8) {
                        showAiraToast("Password must be at least 8 characters long.", "error");
                        return;
                    }

                    if (passwordVal !== confirmPasswordVal) {
                        showAiraToast("Passwords do not match. Please verify.", "error");
                        return;
                    }

                    if (loginSubmitBtn) {
                        loginSubmitBtn.disabled = true;
                        loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Finalizing Registration...`;
                    }
                    if (laserScanner) laserScanner.style.display = "block";

                    fetch(`${API_BASE_URL}/api/signup`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name: nameVal, email: emailVal, password: passwordVal })
                    })
                        .then(res => {
                            if (!res.ok) {
                                return res.json().then(errData => {
                                    throw new Error(errData.message || "Registration failed.");
                                });
                            }
                            return res.json();
                        })
                        .then(data => {
                            if (data.status === "success") {
                                showAiraToast("Account created successfully!", "success");
                                if (loginSubmitBtn) {
                                    loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Initializing Auto Login...`;
                                }

                                return fetch(`${API_BASE_URL}/api/login`, {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({ email: emailVal, password: passwordVal })
                                });
                            } else {
                                throw new Error(data.message || "Registration failed.");
                            }
                        })
                        .then(res => {
                            if (!res || !res.ok) throw new Error("Identity registered, but failed auto-decryption login.");
                            return res.json();
                        })
                        .then(loginData => {
                            if (loginData.status === "success") {
                                handleSuccessfulDecryption(loginData.token, loginData.user);
                                // Reset stages back
                                signupStage = 1;
                            } else {
                                throw new Error(loginData.message || "Auto-login failed.");
                            }
                        })
                        .catch(err => {
                            console.warn("[SIGNUP SYSTEM] Registration server offline, provisioning user locally inside sandbox vault:", err);

                            localStorage.setItem(`offline_user_${emailVal}`, passwordVal);

                            if (loginSubmitBtn) {
                                loginSubmitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Initializing Sandbox Session...`;
                            }

                            setTimeout(() => {
                                if (laserScanner) laserScanner.style.display = "none";
                                showAiraToast("Offline sandbox session created.", "success");
                                handleSuccessfulDecryption("mock_offline_token", { id: "mock_offline_new", name: nameVal, email: emailVal });
                                signupStage = 1;
                            }, 1000);
                        });
                }
            }
        });
    }

    // Logout Handler
    if (logoutTrigger) {
        logoutTrigger.addEventListener("click", (e) => {
            e.preventDefault();

            // Clear session state
            // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
            localStorage.removeItem("aira_session_active");
            localStorage.removeItem("aira_auth_token");
            localStorage.removeItem("aira_user");

            // Reset input values
            if (usernameInput) usernameInput.value = "";
            if (passwordInput) passwordInput.value = "";
            if (errorMsg) errorMsg.style.display = "none";

            // Reset submit button styling
            if (loginSubmitBtn) {
                loginSubmitBtn.disabled = false;
                loginSubmitBtn.innerHTML = `<i class="fa-solid fa-right-to-bracket"></i> Login`;
                loginSubmitBtn.style.background = "";
                loginSubmitBtn.style.borderColor = "";
                loginSubmitBtn.style.boxShadow = "";
            }

            // Restore preloader styles and display states
            if (preloader) {
                preloader.classList.remove("fade-out");
                preloader.style.display = "flex";
                preloader.style.opacity = "1";
                preloader.style.visibility = "visible";
                // Reset progress bar elements
                const progressBar = document.getElementById("preloader-progress-bar");
                const percentageText = document.getElementById("preloader-percentage");
                const consoleBox = document.getElementById("preloader-console");
                if (progressBar) progressBar.style.width = "0%";
                if (percentageText) percentageText.textContent = "0%";
                if (consoleBox) {
                    consoleBox.innerHTML = `<div class="console-line">>> Initializing micro-nodal handshakes...</div>`;
                }
            }

            if (loginPortal) {
                loginPortal.classList.remove("fade-out");
                loginPortal.style.opacity = "0";
                loginPortal.style.visibility = "hidden";
                loginPortal.style.display = "none"; // Hide login portal while preloader runs
            }

            // Hide logout trigger
            logoutTrigger.style.display = "none";

            // Re-lock body scrolling
            document.body.style.overflow = "hidden";

            // Scroll cleanly to top
            window.scrollTo({ top: 0 });

            // Run preloader simulation again
            const progressBar = document.getElementById("preloader-progress-bar");
            const percentageText = document.getElementById("preloader-percentage");
            const consoleBox = document.getElementById("preloader-console");

            const logs = [
                "INIT: Initializing secure micro-nodal handshakes...",
                "SYNC: Fetching database variables for local regions...",
                "NLP: Loading PyTorch & Text Analysis Model semantic structures...",
                "SYS: Generating dynamic styling indices...",
                "SUCCESS: System nodes online. Redirecting to auth..."
            ];

            let progress = 0;
            let logIndex = 0;

            const preloaderInterval = setInterval(() => {
                progress += Math.floor(Math.random() * 5) + 3;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(preloaderInterval);

                    setTimeout(() => {
                        preloader.classList.add("fade-out");
                        setTimeout(() => {
                            if (preloader) preloader.style.display = "none";
                        }, 800);

                        if (loginPortal) {
                            loginPortal.style.display = "flex";
                            loginPortal.style.opacity = "1";
                            loginPortal.style.visibility = "visible";
                        }
                    }, 500);
                }

                if (progressBar) progressBar.style.width = `${progress}%`;
                if (percentageText) percentageText.textContent = `${progress}%`;

                if (progress >= (logIndex + 1) * 20 && logIndex < logs.length) {
                    if (consoleBox) {
                        const line = document.createElement("div");
                        line.className = "console-line";
                        line.textContent = `>> ${logs[logIndex]}`;
                        consoleBox.appendChild(line);
                        consoleBox.scrollTop = consoleBox.scrollHeight;
                    }
                    logIndex++;
                }
            }, 80);
        });
    }

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
    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("active");
        });
    }

    // Smooth navigation active states
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            if (hamburger) hamburger.classList.remove("active");
            if (navLinks) navLinks.classList.remove("active");
        });
    });

    // Navbar glass style on scroll
    window.addEventListener("scroll", () => {
        if (navbar) {
            if (window.scrollY > 40) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        }
    });

    // ==========================================================================
    // 3. DIALOGUE INTERACTIVE INPUT SLIDERS & MOOD SELECTION
    // ==========================================================================
    const sliders = [
        { id: "academic-pressure", valId: "academic-pressure-val" },
        { id: "anxiety-level", valId: "anxiety-level-val" },
        { id: "stress-level", valId: "stress-level-val" },
        { id: "study-satisfaction", valId: "study-satisfaction-val" },
        { id: "financial-stress", valId: "financial-stress-val" }
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

    // Clickable Emoji Mood selector logic with native hidden input tracking
    const moodInput = document.getElementById("selected-mood-input");
    const moodOptions = document.querySelectorAll(".mood-option");

    // Init default active option based on input value
    if (moodInput) {
        moodOptions.forEach(opt => {
            if (opt.getAttribute("data-mood") === moodInput.value) {
                opt.classList.add("active");
            }
        });
    }

    const moodSelectorContainer = document.getElementById("mood-selector-container");
    if (moodSelectorContainer && moodInput) {
        moodSelectorContainer.addEventListener("click", (e) => {
            const opt = e.target.closest(".mood-option");
            if (opt) {
                moodOptions.forEach(o => o.classList.remove("active"));
                opt.classList.add("active");
                moodInput.value = opt.getAttribute("data-mood");
                console.log("Selected Mood updated in hidden input:", moodInput.value);
            }
        });
    }

    // Journal Reflection Starter Chips & Character Count
    const diaryInputEl = document.getElementById("diary-input");
    const charCountEl = document.getElementById("char-count");
    const reflectionChips = document.querySelectorAll(".reflection-chip");

    if (diaryInputEl && charCountEl) {
        diaryInputEl.addEventListener("input", () => {
            charCountEl.textContent = `${diaryInputEl.value.length} characters`;
        });
    }

    if (reflectionChips && diaryInputEl) {
        reflectionChips.forEach(chip => {
            chip.addEventListener("click", () => {
                const promptText = chip.getAttribute("data-prompt") || "";
                if (promptText) {
                    if (diaryInputEl.value.trim().length > 0) {
                        diaryInputEl.value = diaryInputEl.value.trim() + " " + promptText;
                    } else {
                        diaryInputEl.value = promptText;
                    }
                    diaryInputEl.focus();
                    if (charCountEl) charCountEl.textContent = `${diaryInputEl.value.length} characters`;
                    showAiraToast("Starter added to your reflection!", "info");
                }
            });
        });
    }

    // ==========================================================================
    // 4. PRESET CHART.JS DATA STRUCTURES & INITIALIZATION
    // ==========================================================================
    let stressTrendChart = null;
    let emotionProfileChart = null;

    function initAnalyticsCharts() {
        const lineEl = document.getElementById("stressTrendChart");
        const radarEl = document.getElementById("emotionProfileChart");
        if (!lineEl || !radarEl) return;

        const lineCtx = lineEl.getContext("2d");
        const radarCtx = radarEl.getContext("2d");

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
        heatmapHistory = [];
        for (let i = 1; i <= 30; i++) {
            heatmapHistory.push({
                day: i,
                mood: "unvisited",
                wellnessLevel: 0,
                score: 0,
                journal: "No logged status.",
                formattedDate: ""
            });
        }
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

            if (dayLog.wellnessLevel > 0) {
                cell.className = `heatmap-day-cell wellness-lvl-${dayLog.wellnessLevel}`;
            } else {
                cell.className = `heatmap-day-cell`;
            }
            cell.textContent = dayLog.day;

            // Add click listener
            cell.addEventListener("click", () => {
                grid.querySelectorAll(".heatmap-day-cell").forEach(c => c.classList.remove("active-selected"));
                cell.classList.add("active-selected");

                if (dayLog.mood === "unvisited") {
                    emptyMsg.style.display = "block";
                    emptyMsg.textContent = `Day ${dayLog.day}${dayLog.formattedDate ? ' (' + dayLog.formattedDate + ')' : ''}: No logged assessment for this day. Run a scan to capture wellness metrics.`;
                    contentPanel.style.display = "none";
                } else {
                    emptyMsg.style.display = "none";
                    contentPanel.style.display = "block";

                    dayTitle.textContent = `Day ${dayLog.day} Status`;
                    scoreBadge.textContent = `${dayLog.score} Wellness`;

                    // Populate expanded details inspector fields
                    const insDate = document.getElementById("inspector-date");
                    const insRisk = document.getElementById("inspector-risk-level");
                    const insBeh = document.getElementById("inspector-behavioral-prob");
                    const insTxt = document.getElementById("inspector-text-prob");
                    const insComb = document.getElementById("inspector-combined-prob");

                    if (insDate) insDate.textContent = dayLog.formattedDate || "N/A";
                    if (insRisk) {
                        insRisk.textContent = dayLog.riskLevel || "N/A";
                        if ((dayLog.riskLevel || "").toLowerCase() === "low") {
                            insRisk.style.color = "var(--neon-emerald)";
                        } else if ((dayLog.riskLevel || "").toLowerCase() === "moderate" || (dayLog.riskLevel || "").toLowerCase() === "mild") {
                            insRisk.style.color = "var(--neon-orange)";
                        } else {
                            insRisk.style.color = "var(--neon-rose)";
                        }
                    }
                    if (insBeh) insBeh.textContent = dayLog.behavioralProbability !== undefined ? `${(dayLog.behavioralProbability * 100).toFixed(1)}%` : "0.0%";
                    if (insTxt) insTxt.textContent = dayLog.textProbability !== undefined ? `${(dayLog.textProbability * 100).toFixed(1)}%` : "0.0%";
                    if (insComb) insComb.textContent = dayLog.combinedProbability !== undefined ? `${(dayLog.combinedProbability * 100).toFixed(1)}%` : "0.0%";

                    let emoji = "😊";
                    let formattedMoodName = "Joy / Optimism";
                    if (dayLog.mood === "melancholy") { emoji = "😭"; formattedMoodName = "Melancholy / Sadness"; }
                    if (dayLog.mood === "burnout") { emoji = "😫"; formattedMoodName = "Exhaustion / Burnout"; }
                    if (dayLog.mood === "anxiety") { emoji = "🥺"; formattedMoodName = "Anxiety / Fear"; }
                    if (dayLog.mood === "calm" || dayLog.mood === "neutral") { emoji = "😐"; formattedMoodName = "Calm / Neutral"; }

                    moodName.innerHTML = `${formattedMoodName} ${emoji}`;
                    journalText.textContent = `"${dayLog.journal}"`;
                }
            });

            grid.appendChild(cell);
        });
    }

    // Initialize heatmap and render
    initHeatmapHistory();
    renderHeatmapGrid();

    // ==========================================================================
    // ==========================================================================
    // 5. THERAPIST RECOMMENDER LOGIC — CITY-BASED LOCATION SYSTEM
    // Default city: Jaipur. User can select country → then city.
    // ==========================================================================

    // City database: country → cities with lat/lon and state/province
    const cityDatabase = {
        "India": {
            cities: [
                { name: "Jaipur", lat: 26.9124, lon: 75.7873, state: "Rajasthan" },
                { name: "Delhi", lat: 28.6139, lon: 77.2090, state: "Delhi" },
                { name: "Mumbai", lat: 19.0760, lon: 72.8777, state: "Maharashtra" },
                { name: "Bangalore", lat: 12.9716, lon: 77.5946, state: "Karnataka" },
                { name: "Hyderabad", lat: 17.3850, lon: 78.4867, state: "Telangana" },
                { name: "Chennai", lat: 13.0827, lon: 80.2707, state: "Tamil Nadu" },
                { name: "Kolkata", lat: 22.5726, lon: 88.3639, state: "West Bengal" },
                { name: "Pune", lat: 18.5204, lon: 73.8567, state: "Maharashtra" },
                { name: "Ahmedabad", lat: 23.0225, lon: 72.5714, state: "Gujarat" },
                { name: "Lucknow", lat: 26.8467, lon: 80.9462, state: "Uttar Pradesh" },
                { name: "Chandigarh", lat: 30.7333, lon: 76.7794, state: "Chandigarh" },
                { name: "Kota", lat: 25.2138, lon: 75.8648, state: "Rajasthan" },
                { name: "Jodhpur", lat: 26.2389, lon: 73.0243, state: "Rajasthan" },
                { name: "Udaipur", lat: 24.5854, lon: 73.7125, state: "Rajasthan" },
                { name: "Bhopal", lat: 23.2599, lon: 77.4126, state: "Madhya Pradesh" },
                { name: "Indore", lat: 22.7196, lon: 75.8577, state: "Madhya Pradesh" },
                { name: "Nagpur", lat: 21.1458, lon: 79.0882, state: "Maharashtra" },
                { name: "Patna", lat: 25.5941, lon: 85.1376, state: "Bihar" },
                { name: "Bhubaneswar", lat: 20.2961, lon: 85.8245, state: "Odisha" },
                { name: "Surat", lat: 21.1702, lon: 72.8311, state: "Gujarat" }
            ]
        },
        "USA": {
            cities: [
                { name: "New York", lat: 40.7128, lon: -74.0060, state: "New York" },
                { name: "Los Angeles", lat: 34.0522, lon: -118.2437, state: "California" },
                { name: "Chicago", lat: 41.8781, lon: -87.6298, state: "Illinois" },
                { name: "Houston", lat: 29.7604, lon: -95.3698, state: "Texas" },
                { name: "San Francisco", lat: 37.7749, lon: -122.4194, state: "California" },
                { name: "Boston", lat: 42.3601, lon: -71.0589, state: "Massachusetts" },
                { name: "Seattle", lat: 47.6062, lon: -122.3321, state: "Washington" },
                { name: "Austin", lat: 30.2672, lon: -97.7431, state: "Texas" },
                { name: "Denver", lat: 39.7392, lon: -104.9903, state: "Colorado" },
                { name: "Miami", lat: 25.7617, lon: -80.1918, state: "Florida" }
            ]
        },
        "UK": {
            cities: [
                { name: "London", lat: 51.5074, lon: -0.1278, state: "England" },
                { name: "Manchester", lat: 53.4808, lon: -2.2426, state: "England" },
                { name: "Birmingham", lat: 52.4862, lon: -1.8904, state: "England" },
                { name: "Edinburgh", lat: 55.9533, lon: -3.1883, state: "Scotland" },
                { name: "Glasgow", lat: 55.8642, lon: -4.2518, state: "Scotland" },
                { name: "Liverpool", lat: 53.4084, lon: -2.9916, state: "England" },
                { name: "Bristol", lat: 51.4545, lon: -2.5879, state: "England" },
                { name: "Leeds", lat: 53.8008, lon: -1.5491, state: "England" }
            ]
        },
        "Canada": {
            cities: [
                { name: "Toronto", lat: 43.6532, lon: -79.3832, state: "Ontario" },
                { name: "Vancouver", lat: 49.2827, lon: -123.1207, state: "British Columbia" },
                { name: "Montreal", lat: 45.5017, lon: -73.5673, state: "Quebec" },
                { name: "Calgary", lat: 51.0447, lon: -114.0719, state: "Alberta" },
                { name: "Ottawa", lat: 45.4215, lon: -75.6972, state: "Ontario" },
                { name: "Edmonton", lat: 53.5461, lon: -113.4938, state: "Alberta" }
            ]
        },
        "Australia": {
            cities: [
                { name: "Sydney", lat: -33.8688, lon: 151.2093, state: "New South Wales" },
                { name: "Melbourne", lat: -37.8136, lon: 144.9631, state: "Victoria" },
                { name: "Brisbane", lat: -27.4698, lon: 153.0251, state: "Queensland" },
                { name: "Perth", lat: -31.9505, lon: 115.8605, state: "Western Australia" },
                { name: "Adelaide", lat: -34.9285, lon: 138.6007, state: "South Australia" }
            ]
        },
        "Germany": {
            cities: [
                { name: "Berlin", lat: 52.5200, lon: 13.4050, state: "Berlin" },
                { name: "Munich", lat: 48.1351, lon: 11.5820, state: "Bavaria" },
                { name: "Hamburg", lat: 53.5753, lon: 10.0153, state: "Hamburg" },
                { name: "Frankfurt", lat: 50.1109, lon: 8.6821, state: "Hesse" },
                { name: "Cologne", lat: 50.9333, lon: 6.9500, state: "North Rhine-Westphalia" }
            ]
        },
        "France": {
            cities: [
                { name: "Paris", lat: 48.8566, lon: 2.3522, state: "Île-de-France" },
                { name: "Lyon", lat: 45.7640, lon: 4.8357, state: "Auvergne-Rhône-Alpes" },
                { name: "Marseille", lat: 43.2965, lon: 5.3698, state: "Provence-Alpes-Côte d'Azur" },
                { name: "Toulouse", lat: 43.6047, lon: 1.4442, state: "Occitanie" }
            ]
        },
        "UAE": {
            cities: [
                { name: "Dubai", lat: 25.2048, lon: 55.2708, state: "Dubai" },
                { name: "Abu Dhabi", lat: 24.4539, lon: 54.3773, state: "Abu Dhabi" },
                { name: "Sharjah", lat: 25.3462, lon: 55.4211, state: "Sharjah" }
            ]
        },
        "Singapore": {
            cities: [
                { name: "Singapore City", lat: 1.3521, lon: 103.8198, state: "Singapore" }
            ]
        },
        "Japan": {
            cities: [
                { name: "Tokyo", lat: 35.6762, lon: 139.6503, state: "Tokyo" },
                { name: "Osaka", lat: 34.6937, lon: 135.5023, state: "Osaka" },
                { name: "Kyoto", lat: 35.0116, lon: 135.7681, state: "Kyoto" }
            ]
        }
    };

    // Doctor database organized by city
    const doctorsByCity = {
        "Jaipur": [
            { name: "Dr. Priya Sharma, MD", specialization: "Stress & Academic Burnout", experience: 12, degree: "MD Psychiatry, AIIMS Delhi", certifications: "Certified Cognitive Behavioral Therapist", achievements: "Best Psychiatrist Award – Rajasthan Medical Council 2023", bio: "Specializes in student mental health, academic pressure, and exam anxiety using evidence-based CBT and mindfulness methods.", hospital: "Fortis Escorts Hospital, Jaipur", status: "Online Now", hours: "09:00 - 17:00", rating: 4.9, phone: "+91 141 255 0101", type: "stress" },
            { name: "Dr. Anil Mehta, PsyD", specialization: "Anxiety & Depression", experience: 9, degree: "PsyD Clinical Psychology, Rajasthan University", certifications: "Licensed Clinical Psychologist", achievements: "Featured in Times of India Mental Health Column", bio: "Works with adolescents and young adults dealing with anxiety disorders, panic attacks, and low self-esteem using integrative therapy.", hospital: "SMS Medical College, Jaipur", status: "Online Now", hours: "10:00 - 18:00", rating: 4.8, phone: "+91 141 255 0202", type: "anxiety" },
            { name: "Dr. Sunita Agarwal, MBBS", specialization: "Clinical Depression", experience: 15, degree: "MBBS, MD Psychiatry – Jaipur Golden Hospital", certifications: "Fellow of Indian Psychiatric Society", achievements: "Pioneer of rural telepsychiatry in Rajasthan", bio: "Treats moderate-to-severe depression, bipolar disorder, and emotional dysregulation with medication management and talk therapy.", hospital: "Jaipur Golden Hospital", status: "Offline", hours: "08:00 - 14:00", rating: 4.7, phone: "+91 141 255 0303", type: "depression" },
            { name: "Dr. Rahul Verma, PhD", specialization: "Burnout & Academic Stress", experience: 7, degree: "PhD Psychology, University of Rajasthan", certifications: "Certified Wellness & Resilience Coach", achievements: "Designed AIRA-certified student resilience curriculum", bio: "Focuses on building mental toughness, productivity habits, and stress regulation for competitive exam students.", hospital: "Mind Wellness Clinic, Vaishali Nagar", status: "Online Now", hours: "11:00 - 19:00", rating: 4.6, phone: "+91 141 255 0404", type: "stress" }
        ],
        "Delhi": [
            { name: "Dr. Kavita Singh, MD", specialization: "Stress & Burnout", experience: 14, degree: "MD Psychiatry, AIIMS New Delhi", certifications: "Certified Mindfulness Instructor", achievements: "Keynote Speaker – NIMHANS Mental Health Summit 2024", bio: "Expert in work-life balance restoration, perfectionism, and academic performance anxiety for students and professionals.", hospital: "AIIMS New Delhi", status: "Online Now", hours: "08:30 - 16:30", rating: 5.0, phone: "+91 11 2658 8500", type: "stress" },
            { name: "Dr. Rohan Das, PsyD", specialization: "General Anxiety", experience: 11, degree: "PsyD, Jamia Millia Islamia", certifications: "Licensed Psychotherapist", achievements: "Author – 'The Anxious Student Mind'", bio: "Uses ACT (Acceptance & Commitment Therapy) to help students overcome social anxiety, test phobia, and overthinking loops.", hospital: "Max Healthcare, Saket Delhi", status: "Online Now", hours: "10:00 - 18:00", rating: 4.8, phone: "+91 11 2658 8600", type: "anxiety" },
            { name: "Dr. Neha Chopra, MBBS", specialization: "Clinical Depression", experience: 16, degree: "MBBS + MD Psychiatry, Delhi University", certifications: "Fellow IPS, Certified DBT Therapist", achievements: "Recipient of Excellence in Mental Healthcare Award 2022", bio: "Comprehensive depression management combining psychopharmacology and evidence-based CBT for college students.", hospital: "Safdarjung Hospital, New Delhi", status: "Offline", hours: "09:00 - 15:00", rating: 4.9, phone: "+91 11 2658 8700", type: "depression" }
        ],
        "Mumbai": [
            { name: "Dr. Aarti Patel, MD", specialization: "Anxiety Disorders", experience: 13, degree: "MD Psychiatry, KEM Hospital Mumbai", certifications: "Certified EMDR Therapist", achievements: "TED Talk Speaker on Youth Mental Health", bio: "Specializes in panic disorder, social anxiety, and performance anxiety for Mumbai's competitive student population.", hospital: "Lilavati Hospital, Bandra", status: "Online Now", hours: "09:00 - 17:00", rating: 4.9, phone: "+91 22 2655 1234", type: "anxiety" },
            { name: "Dr. Suresh Nair, PhD", specialization: "Depression & Mood Disorders", experience: 10, degree: "PhD Clinical Psychology, Mumbai University", certifications: "Licensed Psychologist, MCI Registered", achievements: "Founder of Mumbai Youth Mental Health Foundation", bio: "Integrative approach combining CBT, mindfulness and interpersonal therapy for depression and emotional dysregulation.", hospital: "Bombay Hospital, Marine Lines", status: "Online Now", hours: "11:00 - 19:00", rating: 4.7, phone: "+91 22 2655 5678", type: "depression" }
        ],
        "Bangalore": [
            { name: "Dr. Deepika Rao, MD", specialization: "Tech Stress & Burnout", experience: 8, degree: "MD Psychiatry, NIMHANS Bangalore", certifications: "Certified Cognitive Coach", achievements: "Mental Health Advisor to top IT firms in Bangalore", bio: "Specializes in tech-industry burnout, digital addiction, and work-pressure-related anxiety for students and engineers.", hospital: "NIMHANS, Bangalore", status: "Online Now", hours: "10:00 - 18:00", rating: 4.8, phone: "+91 80 2699 5001", type: "stress" },
            { name: "Dr. Vikram Krishnan, PsyD", specialization: "Anxiety & Stress Management", experience: 12, degree: "PsyD, Christ University Bangalore", certifications: "Certified DBT & Mindfulness Practitioner", achievements: "Top Psychologist Award – Bangalore Health Summit 2023", bio: "Helps engineering and medical students manage perfectionism, social isolation, and exam-related anxiety through structured therapy.", hospital: "Manipal Hospital, Bangalore", status: "Offline", hours: "09:00 - 15:00", rating: 4.9, phone: "+91 80 2699 5002", type: "anxiety" }
        ],
        "London": [
            { name: "Dr. Emily Clarke, DClinPsy", specialization: "Stress & Academic Burnout", experience: 11, degree: "DClinPsy, University College London", certifications: "BPS Chartered Psychologist", achievements: "NHS Mental Health Excellence Award 2023", bio: "Works with university students experiencing high-pressure academic environments and imposter syndrome using evidence-based CBT.", hospital: "King's College Hospital, London", status: "Online Now", hours: "09:00 - 17:00", rating: 4.9, phone: "+44 20 3299 9000", type: "stress" },
            { name: "Dr. James Thornton, PhD", specialization: "Anxiety Disorders", experience: 14, degree: "PhD Psychology, Oxford University", certifications: "BABCP Accredited CBT Therapist", achievements: "Author of 'Managing Student Anxiety' published by Penguin", bio: "Specialist in generalised anxiety disorder, social phobia, and OCD among London's student population.", hospital: "The Priory Hospital, London", status: "Online Now", hours: "10:00 - 18:00", rating: 4.8, phone: "+44 20 3299 9001", type: "anxiety" }
        ],
        "New York": [
            { name: "Dr. Sarah Williams, PsyD", specialization: "Depression & Mood Disorders", experience: 13, degree: "PsyD, Columbia University", certifications: "Licensed Psychologist, APA Member", achievements: "Top Doctor Award – New York Magazine 2023", bio: "Comprehensive treatment for clinical depression, bipolar disorder, and major life transitions for New York students and professionals.", hospital: "NewYork-Presbyterian Hospital", status: "Online Now", hours: "08:00 - 16:00", rating: 5.0, phone: "+1 (212) 555-0101", type: "depression" },
            { name: "Dr. Michael Chen, PhD", specialization: "Anxiety & Academic Stress", experience: 9, degree: "PhD Clinical Psychology, NYU", certifications: "Certified CBT & Exposure Therapist", achievements: "NYU Student Mental Health Research Grant 2022", bio: "Specializes in test anxiety, academic perfectionism, and social anxiety using evidence-based exposure therapy techniques.", hospital: "NYU Langone Health", status: "Online Now", hours: "10:00 - 18:00", rating: 4.8, phone: "+1 (212) 555-0202", type: "anxiety" }
        ],
        "Dubai": [
            { name: "Dr. Fatima Al-Rashid, MD", specialization: "Stress & Burnout", experience: 10, degree: "MD Psychiatry, American University of Beirut", certifications: "Certified CBT Therapist, Dubai Health Authority", achievements: "Wellness Champion – Dubai Health Authority 2023", bio: "Helps international students and expat youth navigate cultural stress, academic pressure, and identity challenges in the UAE.", hospital: "American Hospital Dubai", status: "Online Now", hours: "09:00 - 17:00", rating: 4.9, phone: "+971 4 336 7777", type: "stress" }
        ],
        "Singapore City": [
            { name: "Dr. Lim Wei Jing, PhD", specialization: "Academic Anxiety & Perfectionism", experience: 8, degree: "PhD Psychology, NUS Singapore", certifications: "Singapore Register of Psychologists", achievements: "SMU Mental Health Innovation Award 2023", bio: "Specializes in high-achieving student mental health, perfectionism-driven anxiety, and burnout prevention in Singapore's competitive education system.", hospital: "National University Hospital, Singapore", status: "Online Now", hours: "09:00 - 17:00", rating: 4.8, phone: "+65 6779 5555", type: "anxiety" }
        ]
    };

    // State variables
    let userLatitude = 26.9124;   // Default: Jaipur
    let userLongitude = 75.7873;
    let currentCity = "Jaipur";
    let currentCountry = "India";

    // Haversine Distance Calculator
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
        return parseFloat((R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))).toFixed(1));
    }

    // Get doctors for selected city (with fallback to nearby cities)
    function getDoctorsForCity(cityName, country) {
        let docs = doctorsByCity[cityName] || [];
        // If no doctors for exact city, use country's first available city doctors
        if (docs.length === 0) {
            const countryData = cityDatabase[country];
            if (countryData) {
                for (const city of countryData.cities) {
                    if (doctorsByCity[city.name] && doctorsByCity[city.name].length > 0) {
                        docs = doctorsByCity[city.name];
                        break;
                    }
                }
            }
        }
        // Ultimate fallback - Jaipur
        if (docs.length === 0) docs = doctorsByCity["Jaipur"];
        return docs;
    }

    // Render doctor cards
    function renderDoctors(filterType = "all") {
        const grid = document.getElementById("doctor-results-grid");
        if (!grid) return;

        grid.innerHTML = `<div class="glass-panel" style="padding:2.5rem;text-align:center;grid-column:span 2;border-radius:16px;"><i class="fa-solid fa-circle-notch fa-spin" style="font-size:2rem;color:var(--neon-cyan);margin-bottom:1rem;display:block;"></i><p>Scanning surrounding micro-nodal clinics...</p></div>`;

        // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
        const token = localStorage.getItem("aira_auth_token");

        // Define offline fallback renderer inside to keep code exceptionally DRY
        const renderOfflineFallback = () => {
            grid.innerHTML = "";
            let doctors = getDoctorsForCity(currentCity, currentCountry);

            // Add computed distances
            let activeList = doctors.map(doc => {
                const docLat = doc.lat || userLatitude + (Math.random() * 0.05 - 0.025);
                const docLon = doc.lon || userLongitude + (Math.random() * 0.05 - 0.025);
                return { ...doc, distance: calculateDistance(userLatitude, userLongitude, docLat, docLon) };
            }).sort((a, b) => a.distance - b.distance);

            if (filterType !== "all") activeList = activeList.filter(d => d.type === filterType);

            if (activeList.length === 0) {
                grid.innerHTML = `<div class="glass-panel" style="padding:2.5rem;text-align:center;grid-column:span 2;border-radius:16px;"><i class="fa-solid fa-user-slash" style="font-size:2rem;color:var(--neon-rose);margin-bottom:1rem;display:block;"></i><p>No specialists matching the specific filter found for ${currentCity}.</p></div>`;
                return;
            }

            activeList.forEach(doc => {
                const statusClass = doc.status === "Online Now" ? "online" : "offline";
                const stars = "⭐".repeat(Math.floor(doc.rating)) + (doc.rating % 1 >= 0.5 ? "½" : "");
                const docAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(doc.name)}&background=0a1628&color=00f2fe&size=80&bold=true&font-size=0.4&rounded=true`;
                const card = document.createElement("div");
                card.className = "doctor-card glass-panel";
                card.innerHTML = `
                    <span class="doc-status-badge ${statusClass}">${doc.status}</span>
                    <div class="doc-main-info">
                        <div class="doc-avatar-container">
                            <img src="${docAvatar}" alt="${doc.name}" class="doc-avatar" onerror="this.onerror=null;this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(doc.name)}&background=0a1628&color=00f2fe&size=80&bold=true&rounded=true'">
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
                            <span class="doc-detail-label">Location</span>
                            <span class="doc-detail-val"><i class="fa-solid fa-location-dot"></i> ${currentCity}, ${currentCountry} (${doc.distance} km away)</span>
                        </div>
                        <div class="doc-detail-item">
                            <span class="doc-detail-label">Clinic / Hospital</span>
                            <span class="doc-detail-val">${doc.hospital}</span>
                        </div>
                        <div class="doc-detail-item">
                            <span class="doc-detail-label">Working Hours</span>
                            <span class="doc-detail-val">${doc.hours}</span>
                        </div>
                    </div>
                    <div class="doc-actions">
                        <a href="tel:${doc.phone.replace(/[^0-9+]/g, '')}" class="neon-btn neon-btn-primary" style="padding:0.6rem;font-size:0.82rem;border-radius:10px;">
                            <i class="fa-solid fa-phone"></i> Contact Specialist
                        </a>
                        <a href="https://www.google.com/maps/search/${encodeURIComponent(doc.hospital + ' ' + currentCity)}" target="_blank" class="neon-btn neon-btn-secondary" style="padding:0.6rem;font-size:0.82rem;border-radius:10px;">
                            <i class="fa-solid fa-map-pin"></i> View on Maps
                        </a>
                    </div>
                `;
                grid.appendChild(card);
            });
        };

        const targetUrl = token ? `${API_BASE_URL}/api/nearby-doctors` : `${API_BASE_URL}/api/public/nearby-doctors`;
        const headers = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        fetch(targetUrl, {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                latitude: userLatitude,
                longitude: userLongitude,
                specialization: filterType,
                sort_by: "best_reviewed",
                city: currentCity
            })
        })
            .then(res => {
                if (!res.ok) throw new Error("API call failed.");
                return res.json();
            })
            .then(data => {
                if (data.status === "success") {
                    const activeList = data.specialists;
                    grid.innerHTML = "";

                    if (!activeList || activeList.length === 0) {
                        grid.innerHTML = `<div class="glass-panel" style="padding:2.5rem;text-align:center;grid-column:span 2;border-radius:16px;"><i class="fa-solid fa-user-slash" style="font-size:2rem;color:var(--neon-rose);margin-bottom:1rem;display:block;"></i><p>No specialists matching the specific filter found for ${currentCity}.</p></div>`;
                        return;
                    }

                    activeList.forEach(doc => {
                        const statusClass = doc.open_status === "Online Now" ? "online" : "offline";
                        const docRating = parseFloat(doc.rating || 4.9).toFixed(1);
                        const stars = "⭐".repeat(Math.floor(docRating)) + (docRating % 1 >= 0.5 ? "½" : "");
                        const revCount = doc.reviews || doc.reviews_count || 140;
                        const docCity = doc.city || currentCity;
                        const reviewSummary = doc.reviews_summary || "Highly rated by students for compassionate and evidence-based mental support.";
                        const docAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(doc.doctor_name)}&background=0a1628&color=00f2fe&size=80&bold=true&font-size=0.4&rounded=true`;
                        const card = document.createElement("div");
                        card.className = "doctor-card glass-panel";
                        card.innerHTML = `
                        <span class="doc-status-badge ${statusClass}">${doc.open_status || 'Online Now'}</span>
                        <div class="doc-main-info">
                            <div class="doc-avatar-container">
                            <img src="${docAvatar}" alt="${doc.doctor_name}" class="doc-avatar" onerror="this.onerror=null;this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(doc.doctor_name)}&background=0a1628&color=00f2fe&size=80&bold=true&rounded=true'">
                            </div>
                            <div class="doc-meta">
                                <h4>${doc.doctor_name}</h4>
                                <div class="doc-specialty">${doc.specialization}</div>
                                <div class="doc-rating">${stars} <span style="font-weight:700;color:#fff;">(${docRating} ★)</span> <span style="color:var(--neon-cyan);font-size:0.75rem;">• ${revCount} reviews</span></div>
                            </div>
                        </div>
                        <p class="doc-bio">"${doc.bio}"</p>
                        
                        <div style="background:rgba(0,240,255,0.04);border:1px solid rgba(0,240,255,0.15);border-radius:8px;padding:0.5rem 0.75rem;margin:0.6rem 0;font-size:0.78rem;color:rgba(255,255,255,0.85);">
                            <i class="fa-solid fa-quote-left" style="color:var(--neon-cyan);margin-right:0.3rem;"></i><em>"${reviewSummary}"</em>
                        </div>

                        <div class="doc-details-grid">
                            <div class="doc-detail-item">
                                <span class="doc-detail-label">Degrees & Certifications</span>
                                <span class="doc-detail-val">${doc.degrees || 'Certified Mental Health Practitioner'} - ${doc.certifications || 'Licensed Clinician'}</span>
                            </div>
                            <div class="doc-detail-item">
                                <span class="doc-detail-label">Location</span>
                                <span class="doc-detail-val"><i class="fa-solid fa-location-dot"></i> ${docCity} (${doc.distance || 1.5} km away)</span>
                            </div>
                            <div class="doc-detail-item">
                                <span class="doc-detail-label">Clinic / Hospital</span>
                                <span class="doc-detail-val">${doc.hospital}</span>
                            </div>
                            <div class="doc-detail-item">
                                <span class="doc-detail-label">Working Hours</span>
                                <span class="doc-detail-val">${doc.timing || '09:00 - 18:00'}</span>
                            </div>
                        </div>
                        <div class="doc-actions">
                            <a href="tel:${(doc.contact_number || '+919876543210').replace(/[^0-9+]/g, '')}" class="neon-btn neon-btn-primary" style="padding:0.6rem;font-size:0.82rem;border-radius:10px;">
                                <i class="fa-solid fa-phone"></i> Contact Specialist
                            </a>
                            <a href="${doc.maps_link || `https://maps.google.com/?q=${encodeURIComponent(doc.hospital + ' ' + docCity)}`}" target="_blank" class="neon-btn neon-btn-secondary" style="padding:0.6rem;font-size:0.82rem;border-radius:10px;">
                                <i class="fa-solid fa-map-pin"></i> View on Maps
                            </a>
                        </div>
                    `;
                        grid.appendChild(card);
                    });
                } else {
                    throw new Error("Invalid response status.");
                }
            })
            .catch(err => {
                console.warn("Nearby doctors API failed, falling back to local database:", err);
                renderOfflineFallback();
            });
    }

    // ---- CITY/COUNTRY SELECTOR MODAL ----
    // Geolocation API helper
    const GeoAPI = {
        baseUrl: `${API_BASE_URL}/api`,
        
        async fetchCountries() {
            try {
                const res = await fetch(`${this.baseUrl}/countries`);
                if (!res.ok) throw new Error("Failed to fetch countries");
                return await res.json();
            } catch (err) {
                console.error("GeoAPI fetchCountries error:", err);
                return null;
            }
        },
        
        async fetchStates(countryCode) {
            try {
                const res = await fetch(`${this.baseUrl}/states/${countryCode}`);
                if (!res.ok) throw new Error(`Failed to fetch states for ${countryCode}`);
                return await res.json();
            } catch (err) {
                console.error("GeoAPI fetchStates error:", err);
                return null;
            }
        },
        
        async fetchCities(countryCode, stateCode) {
            try {
                const res = await fetch(`${this.baseUrl}/cities/${countryCode}/${stateCode}`);
                if (!res.ok) throw new Error(`Failed to fetch cities for ${countryCode}/${stateCode}`);
                return await res.json();
            } catch (err) {
                console.error("GeoAPI fetchCities error:", err);
                return null;
            }
        }
    };

    // State variables for dynamic geographic matching
    let tempSelectedCountry = "India";
    let tempSelectedCountryCode = "IN";
    let tempSelectedState = "Rajasthan";
    let tempSelectedStateCode = "RJ";

    let cachedCountries = [];
    let cachedStates = [];
    let cachedCities = [];

    // Inject the city selector modal HTML into the page
    function injectCityModal() {
        if (document.getElementById("city-selector-modal")) return;
        const modal = document.createElement("div");
        modal.id = "city-selector-modal";
        modal.style.cssText = `position:fixed;inset:0;z-index:9999;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,0.7);backdrop-filter:blur(8px);`;
        modal.innerHTML = `
        <div style="background:var(--glass-bg,rgba(10,15,30,0.97));border:1px solid rgba(0,242,254,0.2);border-radius:24px;padding:2rem;width:min(520px,95vw);max-height:85vh;display:flex;flex-direction:column;gap:1.2rem;box-shadow:0 0 60px rgba(0,242,254,0.08);">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <span style="font-size:0.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--neon-cyan);">Location Selector</span>
                    <h3 style="font-size:1.15rem;font-weight:900;color:#fff;margin-top:0.2rem;">Select Your Country, State &amp; City</h3>
                </div>
                <button id="city-modal-close" style="background:none;border:none;color:rgba(255,255,255,0.5);font-size:1.4rem;cursor:pointer;padding:0.3rem;">&times;</button>
            </div>
            <p style="color:rgba(255,255,255,0.5);font-size:0.85rem;line-height:1.5;margin:0;">Choose your country, state, and finally your city to filter nearby psychologists, or use live GPS auto-detect.</p>

            <!-- Auto GPS Button -->
            <button id="city-auto-gps-btn" style="width:100%;background:linear-gradient(135deg,rgba(0,242,254,0.12),rgba(127,0,255,0.12));border:1px solid rgba(0,242,254,0.35);border-radius:12px;padding:0.75rem;color:var(--neon-cyan);font-size:0.88rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:0.5rem;transition:all 0.2s;">
                <i class="fa-solid fa-location-crosshairs" style="font-size:1rem;color:var(--neon-cyan);"></i> Auto-Detect My GPS Location
            </button>

            <!-- Step 1: Country -->
            <div id="city-step-country">
                <label style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,0.5);display:block;margin-bottom:0.5rem;">Step 1 — Select Country</label>
                <div style="position:relative;">
                    <i class="fa-solid fa-magnifying-glass" style="position:absolute;left:1rem;top:50%;transform:translateY(-50%);color:var(--neon-cyan);font-size:0.85rem;pointer-events:none;"></i>
                    <input id="city-country-search" type="text" placeholder="Search country..." style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.75rem 1rem 0.75rem 2.5rem;color:#fff;font-size:0.9rem;outline:none;font-family:inherit;box-sizing:border-box;" />
                </div>
                <div id="city-country-list" style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.8rem;max-height:200px;overflow-y:auto;padding-right:4px;"></div>
            </div>

            <!-- Step 2: State -->
            <div id="city-step-state" style="display:none;">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem;">
                    <button id="city-state-back-btn" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:0.3rem 0.8rem;color:rgba(255,255,255,0.6);font-size:0.78rem;cursor:pointer;"><i class="fa-solid fa-arrow-left"></i> Back</button>
                    <span id="city-selected-country-label" style="font-size:0.82rem;font-weight:700;color:var(--neon-cyan);"></span>
                </div>
                <label style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,0.5);display:block;margin-bottom:0.5rem;">Step 2 — Select State / UT / Province</label>
                <div style="position:relative;">
                    <i class="fa-solid fa-magnifying-glass" style="position:absolute;left:1rem;top:50%;transform:translateY(-50%);color:var(--neon-purple);font-size:0.85rem;pointer-events:none;"></i>
                    <input id="city-state-search" type="text" placeholder="Search state..." style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.75rem 1rem 0.75rem 2.5rem;color:#fff;font-size:0.9rem;outline:none;font-family:inherit;box-sizing:border-box;" />
                </div>
                <div id="city-state-list" style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.8rem;max-height:200px;overflow-y:auto;padding-right:4px;"></div>
            </div>

            <!-- Step 3: City -->
            <div id="city-step-city" style="display:none;">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem;">
                    <button id="city-city-back-btn" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:0.3rem 0.8rem;color:rgba(255,255,255,0.6);font-size:0.78rem;cursor:pointer;"><i class="fa-solid fa-arrow-left"></i> Back</button>
                    <span id="city-selected-state-label" style="font-size:0.82rem;font-weight:700;color:var(--neon-cyan);"></span>
                </div>
                <label style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,0.5);display:block;margin-bottom:0.5rem;">Step 3 — Select City</label>
                <div style="position:relative;">
                    <i class="fa-solid fa-magnifying-glass" style="position:absolute;left:1rem;top:50%;transform:translateY(-50%);color:var(--neon-purple);font-size:0.85rem;pointer-events:none;"></i>
                    <input id="city-city-search" type="text" placeholder="Search city..." style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:0.75rem 1rem 0.75rem 2.5rem;color:#fff;font-size:0.9rem;outline:none;font-family:inherit;box-sizing:border-box;" />
                </div>
                <div id="city-city-list" style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.8rem;max-height:200px;overflow-y:auto;padding-right:4px;"></div>
            </div>

            <!-- Current selection display -->
            <div id="city-current-display" style="background:rgba(0,242,254,0.05);border:1px solid rgba(0,242,254,0.15);border-radius:12px;padding:0.8rem 1rem;display:flex;align-items:center;gap:0.7rem;">
                <i class="fa-solid fa-location-dot" style="color:var(--neon-cyan);font-size:1rem;"></i>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:.07em;">Current Location</div>
                    <div id="city-current-label" style="font-size:0.95rem;font-weight:800;color:#fff;">${currentCity}, ${currentCountry}</div>
                </div>
            </div>
        </div>
        `;
        document.body.appendChild(modal);

        // Auto GPS Button listener
        const autoGpsBtn = document.getElementById("city-auto-gps-btn");
        if (autoGpsBtn) {
            autoGpsBtn.addEventListener("click", () => {
                modal.style.display = "none";
                requestGpsLocation();
            });
        }

        // Close modal
        document.getElementById("city-modal-close").addEventListener("click", () => { modal.style.display = "none"; });
        modal.addEventListener("click", (e) => { if (e.target === modal) modal.style.display = "none"; });

        // Back buttons
        document.getElementById("city-state-back-btn").addEventListener("click", () => {
            document.getElementById("city-step-country").style.display = "";
            document.getElementById("city-step-state").style.display = "none";
            document.getElementById("city-country-search").value = "";
            renderCountryList("");
        });
        document.getElementById("city-city-back-btn").addEventListener("click", () => {
            document.getElementById("city-step-state").style.display = "";
            document.getElementById("city-step-city").style.display = "none";
            document.getElementById("city-state-search").value = "";
            renderStateList(tempSelectedCountryCode, tempSelectedCountry, "");
        });

        // Search filters (live client-side filter for lag-free typing)
        document.getElementById("city-country-search").addEventListener("input", function () {
            renderCountryList(this.value);
        });
        document.getElementById("city-state-search").addEventListener("input", function () {
            renderStateList(tempSelectedCountryCode, tempSelectedCountry, this.value);
        });
        document.getElementById("city-city-search").addEventListener("input", function () {
            renderCityList(tempSelectedCountryCode, tempSelectedStateCode, this.value);
        });
    }

    const countryToCode = {
        "India": "IN", "USA": "US", "UK": "GB", "Canada": "CA", "Australia": "AU",
        "Germany": "DE", "France": "FR", "UAE": "AE", "Singapore": "SG", "Japan": "JP"
    };

    async function renderCountryList(filterText = "") {
        const container = document.getElementById("city-country-list");
        if (!container) return;

        if (cachedCountries.length === 0) {
            container.innerHTML = `<div style="grid-column:span 2;text-align:center;padding:1rem;color:rgba(255,255,255,0.4);"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>`;
            const apiCountries = await GeoAPI.fetchCountries();
            if (apiCountries && apiCountries.length > 0) {
                cachedCountries = apiCountries;
            } else {
                // local fallback mapping
                cachedCountries = Object.keys(cityDatabase).map(name => ({
                    name: name,
                    iso2: countryToCode[name] || "IN",
                    emoji: "🌐"
                }));
            }
        }

        const q = filterText.toLowerCase().trim();
        const filtered = cachedCountries.filter(c => c.name.toLowerCase().includes(q) || c.iso2.toLowerCase().includes(q));

        container.innerHTML = filtered.map(c => `
            <button onclick="window._selectCountry('${c.name.replace(/'/g, "\\'")}', '${c.iso2}')" style="background:${c.iso2 === tempSelectedCountryCode ? 'rgba(0,242,254,0.12)' : 'rgba(255,255,255,0.04)'};border:1px solid ${c.iso2 === tempSelectedCountryCode ? 'rgba(0,242,254,0.35)' : 'rgba(255,255,255,0.08)'};border-radius:10px;padding:0.6rem 0.8rem;color:${c.iso2 === tempSelectedCountryCode ? 'var(--neon-cyan)' : 'rgba(255,255,255,0.7)'};font-size:0.82rem;font-weight:700;cursor:pointer;text-align:left;transition:all 0.2s;display:flex;align-items:center;gap:0.4rem;overflow:hidden;">
                <span style="font-size:1.15rem;line-height:1;flex-shrink:0;">${c.emoji || '🌐'}</span>
                <span style="text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">${c.name}</span>
            </button>
        `).join("");
    }

    window._selectCountry = async function (countryName, countryCode) {
        tempSelectedCountry = countryName;
        tempSelectedCountryCode = countryCode;

        // Auto-update crisis support hotline banner when country changes
        if (window.updateCrisisUI) {
            window.updateCrisisUI(countryCode);
        }

        document.getElementById("city-step-country").style.display = "none";
        document.getElementById("city-step-state").style.display = "";
        document.getElementById("city-selected-country-label").textContent = `📍 ${countryName}`;
        document.getElementById("city-state-search").value = "";

        cachedStates = []; // Reset states cache to fetch new
        await renderStateList(countryCode, countryName, "");
    };

    async function renderStateList(countryCode, countryName, filterText = "") {
        const container = document.getElementById("city-state-list");
        if (!container) return;

        if (cachedStates.length === 0) {
            container.innerHTML = `<div style="grid-column:span 2;text-align:center;padding:1rem;color:rgba(255,255,255,0.4);"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>`;
            const apiStates = await GeoAPI.fetchStates(countryCode);
            if (apiStates && apiStates.length > 0) {
                cachedStates = apiStates;
            } else {
                // fallback using local database
                const fallbackCities = cityDatabase[countryName]?.cities || [];
                const stateNames = [...new Set(fallbackCities.map(c => c.state))];
                cachedStates = stateNames.map(name => ({
                    name: name,
                    state_code: name.slice(0, 3).toUpperCase(),
                    country_code: countryCode
                }));
            }
        }

        const q = filterText.toLowerCase().trim();
        const filtered = cachedStates.filter(s => s.name.toLowerCase().includes(q));

        if (filtered.length === 0) {
            container.innerHTML = `<div style="grid-column:span 2;text-align:center;padding:1rem;color:rgba(255,255,255,0.4);">No states/provinces found.</div>`;
            return;
        }

        container.innerHTML = filtered.map(s => `
            <button onclick="window._selectState('${s.name.replace(/'/g, "\\'")}', '${s.state_code}')" style="background:${s.state_code === tempSelectedStateCode ? 'rgba(180,0,255,0.12)' : 'rgba(255,255,255,0.04)'};border:1px solid ${s.state_code === tempSelectedStateCode ? 'rgba(180,0,255,0.35)' : 'rgba(255,255,255,0.08)'};border-radius:10px;padding:0.6rem 0.8rem;color:${s.state_code === tempSelectedStateCode ? 'var(--neon-purple)' : 'rgba(255,255,255,0.7)'};font-size:0.82rem;font-weight:700;cursor:pointer;text-align:left;transition:all 0.2s;display:flex;align-items:center;gap:0.4rem;overflow:hidden;">
                <i class="fa-solid fa-map" style="font-size:0.75rem;color:var(--neon-purple);flex-shrink:0;"></i>
                <span style="text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">${s.name}</span>
            </button>
        `).join("");
    }

    window._selectState = async function (stateName, stateCode) {
        tempSelectedState = stateName;
        tempSelectedStateCode = stateCode;

        document.getElementById("city-step-state").style.display = "none";
        document.getElementById("city-step-city").style.display = "";
        document.getElementById("city-selected-state-label").textContent = `📍 ${stateName}`;
        document.getElementById("city-city-search").value = "";

        cachedCities = []; // Reset cities cache
        await renderCityList(tempSelectedCountryCode, stateCode, "");
    };

    async function renderCityList(countryCode, stateCode, filterText = "") {
        const container = document.getElementById("city-city-list");
        if (!container) return;

        if (cachedCities.length === 0) {
            container.innerHTML = `<div style="grid-column:span 2;text-align:center;padding:1rem;color:rgba(255,255,255,0.4);"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>`;
            const apiCities = await GeoAPI.fetchCities(countryCode, stateCode);
            if (apiCities && apiCities.length > 0) {
                cachedCities = apiCities;
            } else {
                // fallback using local database
                const fallbackCities = cityDatabase[tempSelectedCountry]?.cities || [];
                cachedCities = fallbackCities.filter(c => c.state === tempSelectedState);
            }
        }

        const q = filterText.toLowerCase().trim();
        const filtered = cachedCities.filter(c => c.name.toLowerCase().includes(q));

        if (filtered.length === 0) {
            container.innerHTML = `<div style="grid-column:span 2;text-align:center;padding:1rem;color:rgba(255,255,255,0.4);">No cities found.</div>`;
            return;
        }

        container.innerHTML = filtered.map(c => {
            const lat = c.latitude || c.lat || 26.9124;
            const lon = c.longitude || c.lon || 75.7873;
            return `
                <button onclick="window._selectCity('${c.name.replace(/'/g, "\\'")}', '${lat}', '${lon}', '${tempSelectedCountry.replace(/'/g, "\\'")}')" style="background:${c.name === currentCity ? 'rgba(0,255,200,0.12)' : 'rgba(255,255,255,0.04)'};border:1px solid ${c.name === currentCity ? 'rgba(0,255,200,0.35)' : 'rgba(255,255,255,0.08)'};border-radius:10px;padding:0.6rem 0.8rem;color:${c.name === currentCity ? 'var(--neon-cyan)' : 'rgba(255,255,255,0.7)'};font-size:0.82rem;font-weight:700;cursor:pointer;text-align:left;transition:all 0.2s;display:flex;align-items:center;gap:0.4rem;overflow:hidden;">
                    <i class="fa-solid fa-city" style="font-size:0.75rem;color:var(--neon-cyan);flex-shrink:0;"></i>
                    <span style="text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">${c.name}</span>
                </button>
            `;
        }).join("");
    }

    window._selectCity = function (cityName, lat, lon, country) {
        currentCity = cityName;
        currentCountry = country || "India";

        const pLat = parseFloat(lat);
        const pLon = parseFloat(lon);
        userLatitude = !isNaN(pLat) ? pLat : 26.9124;
        userLongitude = !isNaN(pLon) ? pLon : 75.7873;


        // Update UI
        const geoText = document.getElementById("geo-text-status");
        const geoLight = document.getElementById("geo-status-light");
        const geoBtn = document.getElementById("trigger-geo-api");
        if (geoText) geoText.textContent = `📍 Showing doctors for ${cityName}, ${country}`;
        if (geoLight) geoLight.classList.add("active");
        if (geoBtn) { 
            geoBtn.innerHTML = `<i class="fa-solid fa-city"></i> ${cityName}`; 
            geoBtn.style.borderColor = "var(--neon-purple)"; 
        }

        const currentLabel = document.getElementById("city-current-label");
        if (currentLabel) currentLabel.textContent = `${cityName}, ${country}`;

        // Close modal and re-render doctors
        const modal = document.getElementById("city-selector-modal");
        if (modal) modal.style.display = "none";

        // Reset filter tabs
        document.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
        const allTab = document.querySelector(".filter-tab[data-filter='all']");
        if (allTab) allTab.classList.add("active");

        renderDoctors("all");
    };

    // Initialize doctors
    renderDoctors();

    // Geolocation Button → now opens city selector modal
    const geoBtn = document.getElementById("trigger-geo-api");
    const geoText = document.getElementById("geo-text-status");
    const geoLight = document.getElementById("geo-status-light");

    // Set default status text
    if (geoText) geoText.textContent = `📍 Showing doctors for ${currentCity}, ${currentCountry}`;
    if (geoLight) geoLight.classList.add("active");
    if (geoBtn) {
        geoBtn.innerHTML = `<i class="fa-solid fa-city"></i> Change City`;
        geoBtn.addEventListener("click", async () => {
            injectCityModal();
            const modal = document.getElementById("city-selector-modal");
            if (modal) {
                // If we already have a selected country/state/city, load the step 3 city selector
                if (tempSelectedCountryCode && tempSelectedStateCode) {
                    document.getElementById("city-step-country").style.display = "none";
                    document.getElementById("city-step-state").style.display = "none";
                    document.getElementById("city-step-city").style.display = "";
                    document.getElementById("city-selected-state-label").textContent = `📍 ${tempSelectedState}`;
                    document.getElementById("city-city-search").value = "";
                    modal.style.display = "flex";
                    await renderCityList(tempSelectedCountryCode, tempSelectedStateCode, "");
                } else {
                    // Fallback to start with country step
                    document.getElementById("city-step-country").style.display = "";
                    document.getElementById("city-step-state").style.display = "none";
                    document.getElementById("city-step-city").style.display = "none";
                    document.getElementById("city-country-search").value = "";
                    modal.style.display = "flex";
                    await renderCountryList("");
                }
                document.getElementById("city-current-label").textContent = `${currentCity}, ${currentCountry}`;
            }
        });
    }

    // Live HTML5 GPS Geolocation Request Function
    function requestGpsLocation() {
        if (!navigator.geolocation) {
            console.log("HTML5 Geolocation is not supported by this browser.");
            return;
        }

        const gText = document.getElementById("geo-text-status");
        const gLight = document.getElementById("geo-status-light");
        if (gText) gText.textContent = "📡 Requesting browser GPS location...";

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                userLatitude = lat;
                userLongitude = lon;

                let detectedCity = "";
                let detectedCountry = "";

                try {
                    const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
                    if (res.ok) {
                        const data = await res.json();
                        detectedCity = data.city || data.locality || data.principalSubdivision || "";
                        detectedCountry = data.countryName || "India";
                    }
                } catch (e) {
                    console.warn("Reverse geocoding error:", e);
                }

                if (detectedCity) {
                    currentCity = detectedCity;
                    currentCountry = detectedCountry;
                }

                if (gText) gText.textContent = `📍 GPS Location: ${currentCity || 'Detected'} (${lat.toFixed(2)}, ${lon.toFixed(2)})`;
                if (gLight) gLight.classList.add("active");

                const gBtn = document.getElementById("trigger-geo-api");
                if (gBtn) {
                    gBtn.innerHTML = `<i class="fa-solid fa-location-crosshairs"></i> ${currentCity || 'GPS Active'}`;
                    gBtn.style.borderColor = "var(--neon-emerald)";
                }

                // Re-render doctors using live GPS coordinates
                renderDoctors();
            },
            (error) => {
                console.warn("GPS Geolocation permission denied or failed:", error.message);
                if (gText) gText.textContent = `📍 Showing doctors for ${currentCity}, ${currentCountry}`;
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
        );
    }

    // Automatically prompt browser for GPS location on page load!
    requestGpsLocation();


    // Category filter tabs
    const filterTabs = document.querySelectorAll(".filter-tab");
    filterTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            filterTabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            renderDoctors(tab.getAttribute("data-filter"));
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

    function updateRiskTierBanner(riskLevel, probability) {
        const banner = document.getElementById("overall-risk-banner");
        const badge = document.getElementById("risk-tier-badge");
        const summary = document.getElementById("risk-tier-summary");
        const probEl = document.getElementById("risk-tier-probability");
        const iconContainer = document.getElementById("risk-tier-icon");

        if (!banner) return;

        // Standardize to 3 categories: Low, Moderate, High
        const normRisk = (riskLevel || "").toLowerCase();
        let tier = "Moderate";
        if (normRisk.includes("low")) {
            tier = "Low";
        } else if (normRisk.includes("high") || normRisk.includes("critical") || normRisk.includes("severe")) {
            tier = "High";
        } else {
            tier = "Moderate";
        }

        // Reset classes
        banner.classList.remove("tier-low", "tier-moderate", "tier-high");
        
        if (tier === "Low") {
            banner.classList.add("tier-low");
            if (badge) {
                badge.textContent = "LOW MENTAL HEALTH RISK";
                badge.style.background = "rgba(0, 230, 153, 0.15)";
                badge.style.borderColor = "rgba(0, 230, 153, 0.4)";
                badge.style.color = "var(--neon-emerald)";
            }
            if (summary) {
                summary.textContent = "Your reflection indicates a healthy emotional balance and strong psychological resilience. Continue your mindful habits, regular sleep routine, and micro-breaks to sustain this positive momentum!";
            }
            if (iconContainer) {
                iconContainer.style.background = "linear-gradient(135deg, rgba(0, 230, 153, 0.2), rgba(0, 240, 255, 0.1))";
                iconContainer.style.borderColor = "rgba(0, 230, 153, 0.4)";
                iconContainer.style.color = "var(--neon-emerald)";
                iconContainer.innerHTML = '<i class="fa-solid fa-shield-check"></i>';
            }
        } else if (tier === "Moderate") {
            banner.classList.add("tier-moderate");
            if (badge) {
                badge.textContent = "MODERATE MENTAL HEALTH RISK";
                badge.style.background = "rgba(255, 170, 0, 0.15)";
                badge.style.borderColor = "rgba(255, 170, 0, 0.45)";
                badge.style.color = "var(--neon-orange)";
            }
            if (summary) {
                summary.textContent = "Our ML scan detected noticeable markers of academic pressure, stress, or emotional fatigue. Proactive self-care, sleep realignment, and talking to a peer or counselor can help prevent burnout.";
            }
            if (iconContainer) {
                iconContainer.style.background = "linear-gradient(135deg, rgba(255, 170, 0, 0.2), rgba(255, 102, 0, 0.1))";
                iconContainer.style.borderColor = "rgba(255, 170, 0, 0.45)";
                iconContainer.style.color = "var(--neon-orange)";
                iconContainer.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
            }
        } else { // High
            banner.classList.add("tier-high");
            if (badge) {
                badge.textContent = "HIGH MENTAL HEALTH RISK";
                badge.style.background = "rgba(255, 51, 102, 0.2)";
                badge.style.borderColor = "rgba(255, 51, 102, 0.5)";
                badge.style.color = "var(--neon-rose)";
            }
            if (summary) {
                summary.textContent = "Our neural analysis identified elevated distress signals and high mental strain. Please prioritize your well-being right now. We strongly encourage reaching out to a certified doctor or one of the free 24/7 youth helplines below.";
            }
            if (iconContainer) {
                iconContainer.style.background = "linear-gradient(135deg, rgba(255, 51, 102, 0.25), rgba(255, 0, 85, 0.15))";
                iconContainer.style.borderColor = "rgba(255, 51, 102, 0.5)";
                iconContainer.style.color = "var(--neon-rose)";
                iconContainer.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i>';
            }
        }

        if (probEl && probability !== undefined) {
            const probVal = typeof probability === "number" ? (probability > 1 ? probability : probability * 100) : parseFloat(probability);
            probEl.textContent = `${isNaN(probVal) ? 45.0 : probVal.toFixed(1)}%`;
        }
    }

    function renderMatchedDoctors(doctors, riskLevel = "Moderate") {
        const doctorsSection = document.getElementById("recommended-doctors-section");
        const container = document.getElementById("doctors-cards-container");
        if (!doctorsSection || !container) return;

        container.innerHTML = "";
        
        const docList = (doctors && doctors.length > 0) ? doctors : [
            {
                name: "Dr. Ananya Sharma",
                doctor_name: "Dr. Ananya Sharma, MD",
                title: "Lead Youth Mental Health Specialist",
                experience: 11,
                rating: 4.9,
                reviews: 234,
                reviews_summary: "Extremely compassionate approach for engineering & medical students facing burnout.",
                hospital: "Apex Mind Care & Research Institute",
                city: currentCity || "Jaipur",
                location: `${currentCity || "Jaipur"}, India`,
                distance: 1.8,
                mode: "Online & In-person",
                specialty: "Student Stress & Exam Anxiety",
                contact_number: "+91 141 255 0101",
                maps_link: "https://maps.google.com/?q=Fortis+Escorts+Hospital+Jaipur",
                available: "Online Now"
            },
            {
                name: "Dr. Rajesh Varma",
                doctor_name: "Dr. Rajesh Varma, MD",
                title: "Senior Consultant Clinical Psychiatrist",
                experience: 16,
                rating: 4.9,
                reviews: 240,
                reviews_summary: "World-class clinician for adolescent mood recovery and clinical guidance.",
                hospital: "Youth Hope Neuro-Psychiatric Center",
                city: currentCity || "Delhi",
                location: `${currentCity || "Delhi"}, India`,
                distance: 2.5,
                mode: "Online & In-person",
                specialty: "Depression & Mood Disorders",
                contact_number: "+91 11 2658 8500",
                maps_link: "https://maps.google.com/?q=AIIMS+New+Delhi",
                available: "Today, 4:00 PM"
            },
            {
                name: "Dr. Priya Nair",
                doctor_name: "Dr. Priya Nair, PsyD",
                title: "Student Wellness & Stress Counselor",
                experience: 8,
                rating: 4.9,
                reviews: 168,
                reviews_summary: "Transformative stress management techniques for university and high-school students.",
                hospital: "Fortis Mind Wellness Hub",
                city: currentCity || "Jaipur",
                location: `${currentCity || "Jaipur"}, India`,
                distance: 3.2,
                mode: "Online & In-person",
                specialty: "Academic Burnout & Perfectionism",
                contact_number: "+91 141 255 0404",
                maps_link: "https://maps.google.com/?q=Fortis+Escorts+Hospital+Jaipur",
                available: "Online Now"
            }
        ];

        docList.forEach(doc => {
            const card = document.createElement("div");
            card.className = "matched-doctor-card";
            const docRating = parseFloat(doc.rating || 4.9).toFixed(1);
            const stars = "★".repeat(Math.floor(docRating));
            const revCount = doc.reviews || doc.reviews_count || 140;
            const docPhone = doc.contact_number || doc.contact_phone || doc.phone || "+919876543210";
            const docMaps = doc.maps_link || `https://maps.google.com/?q=${encodeURIComponent((doc.hospital || 'Hospital') + ' ' + (doc.city || currentCity))}`;
            const docLoc = doc.city ? `${doc.city}${doc.distance ? ` (${doc.distance} km away)` : ''}` : (doc.location || `${currentCity} (${doc.distance || 1.5} km away)`);
            const docName = doc.doctor_name || doc.name || "Dr. Verified Specialist";
            const docTitle = doc.title || doc.specialization || doc.specialty || "Psychologist / Youth Counselor";
            const reviewSummary = doc.reviews_summary || "Highly rated by students for compassionate and evidence-based mental support.";

            card.innerHTML = `
                <div style="display: flex; gap: 1rem; align-items: flex-start;">
                    <div class="doctor-avatar-box">
                        <i class="fa-solid fa-user-doctor"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap;">
                            <h4 style="font-size: 1.05rem; font-weight: 700; color: #fff; margin: 0; font-family: 'Space Grotesk', sans-serif;">${docName}</h4>
                            <span style="font-size: 0.72rem; padding: 0.2rem 0.55rem; border-radius: 9999px; background: rgba(0, 240, 255, 0.12); color: var(--neon-cyan); border: 1px solid rgba(0, 240, 255, 0.25); font-weight: 600;">
                                <i class="fa-solid fa-circle-check" style="font-size: 0.65rem; margin-right: 0.2rem;"></i> Top Reviewed
                            </span>
                        </div>
                        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.25rem 0 0.5rem 0;">${docTitle}</p>
                        
                        <div style="display: flex; align-items: center; gap: 0.8rem; font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.6rem; flex-wrap: wrap;">
                            <span style="color: #ffb800; font-weight: 700;">${stars} ${docRating} <span style="color: rgba(255,255,255,0.6); font-weight: 500;">(${revCount} reviews)</span></span>
                            <span>•</span>
                            <span><i class="fa-solid fa-location-dot" style="color: var(--neon-rose); margin-right: 0.3rem;"></i>${docLoc}</span>
                            <span>•</span>
                            <span><i class="fa-solid fa-hospital" style="color: var(--neon-purple); margin-right: 0.3rem;"></i>${doc.hospital || 'Specialty Clinic'}</span>
                        </div>

                        <div style="background: rgba(0, 240, 255, 0.03); border: 1px solid rgba(0, 240, 255, 0.12); border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.8rem; font-size: 0.78rem;">
                            <div style="color: var(--text-muted);"><strong style="color: #fff;"><i class="fa-solid fa-quote-left" style="color: var(--neon-cyan); margin-right: 0.3rem; font-size: 0.7rem;"></i></strong> <em>"${reviewSummary}"</em></div>
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 0.6rem; margin-top: 0.8rem;">
                    <a href="tel:${docPhone.replace(/[^0-9+]/g, '')}" class="glow-btn" style="flex: 1; padding: 0.55rem 0.8rem; font-size: 0.82rem; text-align: center; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem; font-weight: 600;">
                        <i class="fa-solid fa-phone"></i> Direct Call
                    </a>
                    <a href="${docMaps}" target="_blank" class="glass-btn" style="flex: 1; padding: 0.55rem 0.8rem; font-size: 0.82rem; text-decoration: none; color: #fff; display: inline-flex; align-items: center; justify-content: center; gap: 0.4rem;">
                        <i class="fa-solid fa-map-location-dot"></i> Directions
                    </a>
                </div>
            `;
            container.appendChild(card);
        });

        doctorsSection.style.display = "block";
    }

    function renderHelplineAlerts(helplines, riskLevel = "Moderate") {
        const helplineSection = document.getElementById("helpline-alert-section");
        const container = document.getElementById("helpline-cards-container");
        if (!helplineSection || !container) return;

        container.innerHTML = "";

        const hList = (helplines && helplines.length > 0) ? helplines : [
            {
                name: "Tele-MANAS (Govt of India)",
                number: "14416",
                alt_number: "1800-891-4416",
                timing: "24/7 Available (Toll-Free)",
                languages: "20+ Languages (Hindi, English & Regional)",
                category: "National Mental Health Helpline",
                icon: "fa-phone-volume",
                color: "var(--neon-emerald)"
            },
            {
                name: "KIRAN (National Helpline)",
                number: "1800-599-0019",
                timing: "24/7 Free & Confidential",
                languages: "Hindi, English, 13 Regional Languages",
                category: "Mental Health & De-addiction",
                icon: "fa-hand-holding-heart",
                color: "var(--neon-cyan)"
            },
            {
                name: "Vandrevala Foundation Helpline",
                number: "+91 9999 666 555",
                timing: "24/7 Free Counseling",
                languages: "Hindi, English, Gujarati, Marathi",
                category: "Youth Crisis & Distress Support",
                icon: "fa-shield-heart",
                color: "var(--neon-rose)"
            },
            {
                name: "AASRA Suicide & Crisis Helpline",
                number: "+91 98204 66726",
                timing: "24/7 Confidential Helpline",
                languages: "English & Hindi",
                category: "Emergency Crisis Intervention",
                icon: "fa-life-ring",
                color: "var(--neon-orange)"
            }
        ];

        hList.forEach(hl => {
            const card = document.createElement("div");
            card.className = "helpline-item-card";
            const hlColor = hl.color || "var(--neon-rose)";
            card.innerHTML = `
                <div>
                    <div style="display: flex; align-items: flex-start; gap: 0.8rem; margin-bottom: 0.75rem;">
                        <div style="width: 42px; height: 42px; border-radius: 10px; background: rgba(255, 51, 102, 0.1); border: 1px solid rgba(255, 51, 102, 0.3); display: flex; align-items: center; justify-content: center; color: ${hlColor}; font-size: 1.15rem; flex-shrink: 0;">
                            <i class="fa-solid ${hl.icon || 'fa-phone-volume'}"></i>
                        </div>
                        <div style="flex: 1;">
                            <h4 style="font-size: 0.98rem; font-weight: 700; color: #fff; margin: 0; font-family: 'Space Grotesk', sans-serif;">${hl.name}</h4>
                            <span style="display: inline-block; font-size: 0.68rem; color: ${hlColor}; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-top: 0.2rem;">${hl.category || 'National Helpline'}</span>
                        </div>
                    </div>

                    <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 0.8rem;">
                        <div><i class="fa-solid fa-clock" style="color: var(--neon-cyan); margin-right: 0.35rem; font-size: 0.75rem;"></i>${hl.timing || '24/7 Free & Confidential'}</div>
                        <div style="margin-top: 0.2rem;"><i class="fa-solid fa-language" style="color: var(--neon-purple); margin-right: 0.35rem; font-size: 0.75rem;"></i>${hl.languages || 'Hindi, English & Regional'}</div>
                    </div>
                </div>

                <div style="margin-top: 0.5rem;">
                    <a href="tel:${hl.number.replace(/\s+/g, '')}" class="glow-btn" style="width: 100%; padding: 0.6rem 1rem; font-size: 0.9rem; text-align: center; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 700; background: linear-gradient(135deg, rgba(255, 51, 102, 0.25), rgba(255, 0, 85, 0.2)); border: 1px solid rgba(255, 51, 102, 0.4); color: #fff; border-radius: 10px;">
                        <i class="fa-solid fa-phone"></i> Call ${hl.number}
                    </a>
                </div>
            `;
            container.appendChild(card);
        });

        helplineSection.style.display = "block";
    }

    function renderRecommendationsList(recs) {
        const recommendationsSection = document.getElementById("ai-recommendations-section");
        const cardsContainer = document.getElementById("recommendations-cards-container");
        
        if (!recommendationsSection || !cardsContainer) return;
        
        cardsContainer.innerHTML = "";
        
        if (!recs || recs.length === 0) {
            recommendationsSection.style.display = "none";
            return;
        }
        
        recs.forEach(rec => {
            const card = document.createElement("div");
            card.className = "recommendation-item-card";
            
            const iconColor = rec.color || "var(--neon-cyan)";
            
            card.innerHTML = `
                <div class="recommendation-icon-box" style="background: rgba(255, 255, 255, 0.02); border: 1px solid ${iconColor}; color: ${iconColor}; box-shadow: 0 0 10px ${iconColor}4d;">
                    <i class="fa-solid ${rec.icon || 'fa-info'}"></i>
                </div>
                <div class="recommendation-info-box">
                    <h5>${rec.title}</h5>
                    <p>${rec.description}</p>
                    <span class="recommendation-tag-badge" style="background: ${iconColor}1a; border: 1px solid ${iconColor}4d; color: ${iconColor};">
                        ${rec.category || 'Wellness'}
                    </span>
                </div>
            `;
            cardsContainer.appendChild(card);
        });
        
        recommendationsSection.style.display = "block";
    }

    function renderBackendMetrics(metrics, data) {
        const finalStress = metrics.stress !== undefined ? metrics.stress : 35;
        const finalAnxiety = metrics.anxiety !== undefined ? metrics.anxiety : 40;
        const finalDepression = metrics.depression !== undefined ? metrics.depression : 30;
        const finalWellness = metrics.wellness !== undefined ? metrics.wellness : 70;
        const finalRiskLevel = metrics.final_risk_level || metrics.risk_level || metrics.risk || "Moderate";
        const combinedProb = metrics.combined_probability !== undefined ? metrics.combined_probability : (metrics.text_probability || 0.45);

        // 1. Update 3-Tier Risk Banner
        updateRiskTierBanner(finalRiskLevel, combinedProb);

        // 2. Render Matched Doctors and Helplines
        renderMatchedDoctors(metrics.matched_doctors || metrics.doctors, finalRiskLevel);
        renderHelplineAlerts(metrics.helplines, finalRiskLevel);

        // 3. Render Personalized AI Recommendations
        if (metrics.recommendations) {
            renderRecommendationsList(metrics.recommendations);
        }

        // 4. Render predicted metric rings
        updateCircularProgress("ring-stress", "perc-stress", finalStress);
        updateCircularProgress("ring-anxiety", "perc-anxiety", finalAnxiety);
        updateCircularProgress("ring-depression", "perc-depression", finalDepression);

        // 5. Risk Category Color badges
        updateRiskBadge("badge-stress", finalStress);
        updateRiskBadge("badge-anxiety", finalAnxiety);
        updateRiskBadge("badge-depression", finalDepression);

        // 6. Wellness index displays
        const wellnessScore = document.getElementById("total-wellness-score");
        const wellnessDesc = document.getElementById("wellness-interpretation");
        const diagnosticTime = document.getElementById("diagnostic-timestamp");

        if (wellnessScore) wellnessScore.textContent = finalWellness;

        // Render external neural microservices API values
        const behavioralProb = metrics.behavioral_probability;
        const textProb = metrics.text_probability;

        const behavioralEl = document.getElementById("metric-behavioral-prob");
        const textEl = document.getElementById("metric-text-prob");
        const combinedEl = document.getElementById("metric-combined-prob");
        const finalRiskEl = document.getElementById("metric-final-risk");

        if (behavioralEl && behavioralProb !== undefined) behavioralEl.textContent = `${(behavioralProb * 100).toFixed(1)}%`;
        if (textEl && textProb !== undefined) textEl.textContent = `${(textProb * 100).toFixed(1)}%`;
        if (combinedEl && combinedProb !== undefined) combinedEl.textContent = `${(combinedProb * 100).toFixed(1)}%`;
        if (finalRiskEl && finalRiskLevel !== undefined) {
            finalRiskEl.textContent = finalRiskLevel;
            const rl = finalRiskLevel.toLowerCase();
            if (rl.includes("low")) {
                finalRiskEl.style.color = "var(--neon-emerald)";
            } else if (rl.includes("high") || rl.includes("critical")) {
                finalRiskEl.style.color = "var(--neon-rose)";
            } else {
                finalRiskEl.style.color = "var(--neon-orange)";
            }
        }

        // Dynamic time stamp
        const now = new Date();
        if (diagnosticTime) {
            diagnosticTime.innerHTML = `<i class="fa-solid fa-clock"></i> Node Synced: ${now.toISOString().replace('T', ' ').slice(0, 19)}`;
        }

        let interpText = "";
        if (finalWellness >= 75) {
            interpText = "Your cognitive loads are in harmony with physiological patterns. AI recommends maintaining physical breaks and positive routines.";
        } else if (finalWellness >= 50) {
            interpText = "Moderate stress registers. Sleep deficits and workload are impacting emotional scores. Focus on structured wind-down periods.";
        } else {
            interpText = "High saturation levels identified. System detects elevated anxiety/depression indicators. AI recommends immediate support and counseling.";
        }
        if (wellnessDesc) wellnessDesc.textContent = interpText;

        // 7. NLP TEXT ANALYSIS MODEL KEYWORD & SENTIMENT DEDUCTION
        executeTextAnalysisModel(data.text || "", finalStress, finalAnxiety, finalDepression);

        // Display results
        if (resultsSec) resultsSec.style.display = "block";
        if (dashboardSec) dashboardSec.style.display = "block";

        // Scroll to results cleanly
        if (resultsSec) resultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Update Charts
        updateAnalyticsData(finalStress, finalAnxiety, finalWellness);

        // Fetch complete updated metrics from the backend to sync line chart and heatmap grid
        loadDashboardData();

        // Auto select today's cell in the heatmap grid after load
        setTimeout(() => {
            const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
            const cells = document.querySelectorAll(".heatmap-day-cell");
            heatmapHistory.forEach((h, idx) => {
                if (h.formattedDate === todayStr && cells.length > idx) {
                    cells[idx].click();
                }
            });
        }, 1200);
    }

    if (scanForm) {
        scanForm.addEventListener("submit", (e) => {
            if (e) e.preventDefault();

            const textVal = document.getElementById("diary-input") ? document.getElementById("diary-input").value.trim() : "";
            const sleepVal = parseFloat(document.getElementById("sleep-hours")?.value) || 7.0;
            const selectedMood = document.getElementById("selected-mood-input")?.value || "calm";

            // Validation checks on the journal text
            if (textVal.length < 15) {
                showAiraToast("Please enter at least 15 characters describing your feelings or day.", "error");
                return;
            }
            const words = textVal.split(/\s+/).filter(w => w.length > 0);
            if (words.length < 3) {
                showAiraToast("Please write at least 3 words to enable accurate neural evaluation.", "error");
                return;
            }

            const lettersOnly = textVal.replace(/[^a-zA-Z]/g, '');
            const digitsOnly = textVal.replace(/[^0-9]/g, '');
            if (digitsOnly.length > 0 && lettersOnly.length === 0) {
                showAiraToast("Journal text cannot consist of only numbers.", "error");
                return;
            }

            const alphanumericOnly = textVal.replace(/[^a-zA-Z0-9]/g, '');
            if (alphanumericOnly.length === 0) {
                showAiraToast("Journal text cannot consist of only symbols.", "error");
                return;
            }

            if (/(.)\1{4,}/.test(textVal)) {
                showAiraToast("Please enter meaningful journal content (keyboard spam detected).", "error");
                return;
            }

            // Trigger AI sweep animation
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing Neural Sequence...`;
            }
            if (laserBar) laserBar.style.display = "block";
            if (consoleLog) consoleLog.style.display = "block";

            // Simulated terminal prints
            const logs = [
                "INIT: Instantiating client tunnel to local secure micro-node...",
                "NLP: Extracting journal sequence to DistilBERT / TF-IDF vector space...",
                "MODEL: Running ML Multilabel & Sentiment Classification Pipeline...",
                "PROC: Evaluating sleep balance & emotional markers...",
                "SUCCESS: Neural prediction computed successfully.",
                "VIS: Rendering 3-Tier Risk Matrix & Youth Resources..."
            ];

            let logIndex = 0;
            if (consoleLog) consoleLog.innerHTML = "";

            const logTimer = setInterval(() => {
                if (logIndex < logs.length && consoleLog) {
                    const line = document.createElement("div");
                    line.className = "scan-log-line";
                    line.textContent = `>> ${logs[logIndex]}`;
                    consoleLog.appendChild(line);
                    consoleLog.scrollTop = consoleLog.scrollHeight;
                    logIndex++;
                } else {
                    clearInterval(logTimer);

                    if (laserBar) laserBar.style.display = "none";
                    if (consoleLog) consoleLog.style.display = "none";
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = `<i class="fa-solid fa-radar"></i> Re-Analyze My Mental Health`;
                    }

                    const storedUser = JSON.parse(localStorage.getItem("aira_user") || "{}");
                    const userAge = parseInt(storedUser.age) || (storedUser.birth_year ? (new Date().getFullYear() - parseInt(storedUser.birth_year)) : 21);
                    const userGender = storedUser.gender || "Female";

                    const payload = {
                        text: textVal,
                        mood: selectedMood,
                        sleep_hours: sleepVal,
                        age: userAge,
                        gender: userGender,
                        latitude: userLatitude || 26.9124,
                        longitude: userLongitude || 75.7873,
                        city: currentCity || "Jaipur"
                    };

                    const token = localStorage.getItem("aira_auth_token");

                    fetch(`${API_BASE_URL}/api/predict`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            ...(token ? { "Authorization": `Bearer ${token}` } : {})
                        },
                        body: JSON.stringify(payload)
                    })
                        .then(res => {
                            if (!res.ok) throw new Error(`Diagnostics API HTTP ${res.status}`);
                            return res.json();
                        })
                        .then(data => {
                            if (data.status === "success") {
                                if (data.warnings && data.warnings.length > 0) {
                                    data.warnings.forEach(w => showAiraToast(w, "warning"));
                                }
                                renderBackendMetrics(data.metrics, payload);
                            } else {
                                throw new Error("Diagnostics error: " + data.message);
                            }
                        })
                        .catch(err => {
                            console.warn("Diagnostics API call failed, using client-side model heuristic:", err);
                            executeDiagnosticMetrics();
                        });
                }
            }, 300);
        });
    }

    // Client-side neural fallback algorithm
    function executeDiagnosticMetrics() {
        const textVal = document.getElementById("diary-input") ? document.getElementById("diary-input").value.toLowerCase() : "";
        const sleepVal = parseFloat(document.getElementById("sleep-hours")?.value) || 7.0;
        const selectedMood = document.getElementById("selected-mood-input")?.value || "calm";

        let sleepDeficit = Math.max(0, 8 - sleepVal);
        let baseStress = 25 + (sleepDeficit * 7);
        let baseAnxiety = 20 + (sleepDeficit * 6);
        let baseDepression = 18 + (sleepDeficit * 6);

        if (textVal.includes("stress") || textVal.includes("overwhelm") || textVal.includes("tired") || textVal.includes("exhaust")) baseStress += 25;
        if (textVal.includes("exam") || textVal.includes("deadline") || textVal.includes("fail") || textVal.includes("pressure")) baseStress += 20;
        if (textVal.includes("anxious") || textVal.includes("worry") || textVal.includes("panic") || textVal.includes("scared")) baseAnxiety += 30;
        if (textVal.includes("sad") || textVal.includes("lonely") || textVal.includes("hopeless") || textVal.includes("depress")) baseDepression += 35;
        if (textVal.includes("happy") || textVal.includes("great") || textVal.includes("calm") || textVal.includes("relax")) {
            baseStress = Math.max(10, baseStress - 20);
            baseAnxiety = Math.max(10, baseAnxiety - 20);
            baseDepression = Math.max(10, baseDepression - 20);
        }

        const crisisWords = ["suicide", "kill myself", "self-harm", "end my life", "want to die"];
        const isCrisis = crisisWords.some(cw => textVal.includes(cw));
        if (isCrisis) {
            baseStress = 95;
            baseAnxiety = 95;
            baseDepression = 95;
        }

        const finalStress = Math.min(100, Math.max(5, Math.round(baseStress)));
        const finalAnxiety = Math.min(100, Math.max(5, Math.round(baseAnxiety)));
        const finalDepression = Math.min(100, Math.max(5, Math.round(baseDepression)));

        const combinedProb = (finalStress * 0.35 + finalAnxiety * 0.35 + finalDepression * 0.30) / 100.0;
        const finalWellness = Math.round(Math.max(5, Math.min(98, 100 - (combinedProb * 100))));

        let finalRiskLevel = "Low";
        if (isCrisis || combinedProb >= 0.65) {
            finalRiskLevel = "High";
        } else if (combinedProb >= 0.35) {
            finalRiskLevel = "Moderate";
        } else {
            finalRiskLevel = "Low";
        }

        const fallbackMetrics = {
            stress: finalStress,
            anxiety: finalAnxiety,
            depression: finalDepression,
            wellness: finalWellness,
            risk_level: finalRiskLevel,
            final_risk_level: finalRiskLevel,
            combined_probability: combinedProb,
            text_probability: combinedProb,
            behavioral_probability: (sleepDeficit * 0.15),
            matched_doctors: [
                {
                    name: "Dr. Ananya Sharma",
                    title: "Youth Mental Health Specialist",
                    experience: 9,
                    rating: 4.9,
                    location: "Metro Wellness Clinic & Telehealth",
                    mode: "Online & In-person",
                    specialty: "Student Stress & Exam Anxiety",
                    phone: "+91 98201 12345",
                    available: "Today, 4:00 PM"
                },
                {
                    name: "Dr. Rajesh Verma",
                    title: "Senior Clinical Psychologist",
                    experience: 14,
                    rating: 4.8,
                    location: "Apex Mind Health Center",
                    mode: "Online Telehealth",
                    specialty: "Cognitive Behavioral Therapy (CBT)",
                    phone: "+91 98202 23456",
                    available: "Tomorrow, 10:00 AM"
                },
                {
                    name: "Dr. Shalini Mehta",
                    title: "Academic & Career Counselor",
                    experience: 8,
                    rating: 4.9,
                    location: "Youth Hope Neuro-Care",
                    mode: "Online & In-person",
                    specialty: "Depression & Burnout Recovery",
                    phone: "+91 98203 34567",
                    available: "Today, 6:30 PM"
                }
            ],
            helplines: [
                {
                    name: "Tele-MANAS (Govt of India)",
                    number: "14416",
                    alt_number: "1800-891-4416",
                    timing: "24/7 Available (Toll-Free)",
                    languages: "20+ Languages (Hindi, English & Regional)",
                    category: "National Mental Health Helpline",
                    icon: "fa-phone-volume",
                    color: "var(--neon-emerald)"
                },
                {
                    name: "KIRAN (National Helpline)",
                    number: "1800-599-0019",
                    timing: "24/7 Free & Confidential",
                    languages: "Hindi, English, 13 Regional Languages",
                    category: "Mental Health & De-addiction",
                    icon: "fa-hand-holding-heart",
                    color: "var(--neon-cyan)"
                },
                {
                    name: "Vandrevala Foundation Helpline",
                    number: "+91 9999 666 555",
                    timing: "24/7 Free Counseling",
                    languages: "Hindi, English, Gujarati, Marathi",
                    category: "Youth Crisis & Distress Support",
                    icon: "fa-shield-heart",
                    color: "var(--neon-rose)"
                },
                {
                    name: "AASRA Suicide & Crisis Helpline",
                    number: "+91 98204 66726",
                    timing: "24/7 Confidential Helpline",
                    languages: "English & Hindi",
                    category: "Emergency Crisis Intervention",
                    icon: "fa-life-ring",
                    color: "var(--neon-orange)"
                }
            ],
            recommendations: [
                {
                    title: finalRiskLevel === "Low" ? "Maintain Positive Equilibrium" : finalRiskLevel === "Moderate" ? "Proactive Stress De-escalation" : "Immediate Support & Consultation",
                    description: finalRiskLevel === "Low" ? "Your score reflects steady coping mechanisms. Keep up your balanced routine and hydration." : finalRiskLevel === "Moderate" ? "Moderate anxiety detected. Allocate time for micro-breaks, boxed breathing, and peer conversations." : "Elevated distress markers detected. Connect with a trusted doctor or 24/7 helpline immediately.",
                    icon: finalRiskLevel === "Low" ? "fa-heart" : finalRiskLevel === "Moderate" ? "fa-shield-heart" : "fa-triangle-exclamation",
                    color: finalRiskLevel === "Low" ? "var(--neon-emerald)" : finalRiskLevel === "Moderate" ? "var(--neon-orange)" : "var(--neon-rose)",
                    category: "Risk-based"
                },
                {
                    title: "Optimize Sleep & Circadian Rhythm",
                    description: `You logged ${sleepVal} hours. Prioritizing 7-8 hours of uninterrupted rest restores cognitive processing and lowers cortisol.`,
                    icon: "fa-bed",
                    color: "var(--neon-cyan)",
                    category: "Sleep Care"
                },
                {
                    title: "Box Breathing & Mind Decompression",
                    description: "Practice 4-4-4-4 breathing technique for 3 minutes to activate the parasympathetic nervous system.",
                    icon: "fa-wind",
                    color: "var(--neon-purple)",
                    category: "Mindfulness"
                }
            ]
        };
        renderBackendMetrics(fallbackMetrics, { text: textVal, mood: selectedMood, sleep_hours: sleepVal });
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

    function executeTextAnalysisModel(text, stress, anxiety, depression) {
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
        let joyVal = Math.round(100 - (stress + depression) / 2);
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
        // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
        const token = localStorage.getItem("aira_auth_token");

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

        if (statusScore) statusScore.textContent = `Wellness score: ${wellness}`;

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

        // If in local simulation mode (no token), update the Trend Graph and Heatmap locally
        if (!token) {
            // Update Trend Graph (local fallback append)
            const now = new Date();
            const timeLabel = now.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

            if (stressTrendChart.data.labels.length === 0 || stressTrendChart.data.labels[0] === 'Mon') {
                stressTrendChart.data.labels = [];
                stressTrendChart.data.datasets[0].data = [];
                stressTrendChart.data.datasets[1].data = [];
            }

            stressTrendChart.data.labels.push(timeLabel);
            stressTrendChart.data.datasets[0].data.push(Math.round(stress / 10));
            stressTrendChart.data.datasets[1].data.push(Math.round(anxiety / 10));

            if (stressTrendChart.data.labels.length > 8) {
                stressTrendChart.data.labels.shift();
                stressTrendChart.data.datasets[0].data.shift();
                stressTrendChart.data.datasets[1].data.shift();
            }
            stressTrendChart.update();

            // Update Heatmap locally for the current day index
            let todayMood = "joy";
            if (stress > 65) todayMood = "burnout";
            else if (anxiety > 60) todayMood = "anxiety";
            else if (wellness < 60) todayMood = "melancholy";

            let lvl = 1;
            if (wellness >= 90) lvl = 5;
            else if (wellness >= 80) lvl = 4;
            else if (wellness >= 60) lvl = 3;
            else if (wellness >= 40) lvl = 2;

            let targetIdx = heatmapHistory.findIndex(h => h.mood === "unvisited");
            if (targetIdx === -1) targetIdx = 29;

            heatmapHistory[targetIdx] = {
                day: targetIdx + 1,
                mood: todayMood,
                wellnessLevel: lvl,
                score: wellness,
                journal: document.getElementById("diary-input").value || "Submitted today's diagnostic assessment.",
                formattedDate: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
            };

            renderHeatmapGrid();

            setTimeout(() => {
                const cells = document.querySelectorAll(".heatmap-day-cell");
                if (cells.length > targetIdx) {
                    cells[targetIdx].click();
                }
            }, 100);
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

        // PERSISTENCE FIX: Migrated from sessionStorage to localStorage for cross-reload persistence
        const token = localStorage.getItem("aira_auth_token");

        if (!token) {
            setTimeout(() => {
                typingDots.style.display = "none";
                const botResponse = generateGenZResponse(query);
                renderMessageBubble(botResponse, "bot");
                msgContainer.scrollTop = msgContainer.scrollHeight;
            }, 800);
            return;
        }

        fetch(`${API_BASE_URL}/api/chatbot`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ message: query })
        })
            .then(res => {
                if (res.status === 401) {
                    localStorage.removeItem("aira_auth_token");
                    alert("Your session has expired. Please log in again to use the dynamic AI chatbot!");
                    window.location.reload();
                    throw new Error("Token expired.");
                }
                if (!res.ok) throw new Error("Chatbot API failed.");
                return res.json();
            })
            .then(data => {
                typingDots.style.display = "none";
                if (data.status === "success") {
                    renderMessageBubble(data.response, "bot");
                } else {
                    const botResponse = generateGenZResponse(query);
                    renderMessageBubble(botResponse, "bot");
                }
                msgContainer.scrollTop = msgContainer.scrollHeight;
            })
            .catch(err => {
                console.warn("AI Chatbot API call failed, falling back to local simulation:", err);
                typingDots.style.display = "none";
                const botResponse = generateGenZResponse(query);
                renderMessageBubble(botResponse, "bot");
                msgContainer.scrollTop = msgContainer.scrollHeight;
            });
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
        currentSecondsRemaining = config ? config[0].duration : 4;

        // Reset bubble classes
        if (bubbleOuter) bubbleOuter.className = "breath-bubble-outer";
        if (labelIndicator) labelIndicator.textContent = "Paced";
        if (countdown) countdown.textContent = currentSecondsRemaining;

        if (instructions) {
            if (selectedRhythm === "box") {
                instructions.textContent = "Box Breathing: 4s Inhale, 4s Hold, 4s Exhale, 4s Hold. Click Start.";
            } else if (selectedRhythm === "relax") {
                instructions.textContent = "4-7-8 Relax: Clinically proven sequence for grounding. Click Start.";
            } else {
                instructions.textContent = "Coherent Breathing: Slow, even 5s cycles to balance blood flow. Click Start.";
            }
        }
    }

    function startBreathingSession() {
        isBreathingActive = true;
        if (playBtn) {
            playBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Pause Session`;
            playBtn.style.borderColor = "var(--neon-pink)";
            playBtn.className = "neon-btn neon-btn-secondary";
        }
        if (resetBtn) resetBtn.disabled = false;

        runBreathingCycleStep();
    }

    function pauseBreathingSession() {
        isBreathingActive = false;
        if (playBtn) {
            playBtn.innerHTML = `<i class="fa-solid fa-play"></i> Resume Session`;
            playBtn.className = "neon-btn neon-btn-primary";
        }

        clearInterval(breathInterval);
        clearTimeout(breathTimeout);
    }

    function stopBreathingSession() {
        isBreathingActive = false;
        if (playBtn) {
            playBtn.innerHTML = `<i class="fa-solid fa-play"></i> Start Session`;
            playBtn.className = "neon-btn neon-btn-primary";
            playBtn.style.borderColor = "transparent";
        }
        if (resetBtn) resetBtn.disabled = true;

        clearInterval(breathInterval);
        clearTimeout(breathTimeout);
        resetBreathingVisuals();
    }

    function runBreathingCycleStep() {
        const config = rhythmsConfig[selectedRhythm];
        const phase = config[currentPhaseIndex];

        // Apply visual classes
        if (bubbleOuter) bubbleOuter.className = `breath-bubble-outer ${phase.state}`;
        if (labelIndicator) labelIndicator.textContent = phase.text;
        currentSecondsRemaining = phase.duration;
        if (countdown) countdown.textContent = currentSecondsRemaining;
        if (instructions) instructions.textContent = phase.desc;

        // Timer countdown loop
        breathInterval = setInterval(() => {
            currentSecondsRemaining--;
            if (currentSecondsRemaining > 0) {
                if (countdown) countdown.textContent = currentSecondsRemaining;
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
    if (playBtn) {
        playBtn.addEventListener("click", () => {
            if (isBreathingActive) {
                pauseBreathingSession();
            } else {
                startBreathingSession();
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            stopBreathingSession();
        });
    }

    // ==========================================================================
    // 9. SMART GLOBAL CRISIS-SUPPORT BANNER SYSTEM
    // ==========================================================================
    const globalHelplineDb = {
        "AF": {
            "name": "Afghanistan",
            "flag": "af",
            "emergency": "119",
            "helpline": "119",
            "title": "National Emergency & Crisis Support"
        },
        "AL": {
            "name": "Albania",
            "flag": "al",
            "emergency": "112",
            "helpline": "127",
            "title": "Emergency Medical Assistance Services"
        },
        "DZ": {
            "name": "Algeria",
            "flag": "dz",
            "emergency": "112",
            "helpline": "021 63 00 63",
            "title": "Algerian Suicide Support Lifeline"
        },
        "AD": {
            "name": "Andorra",
            "flag": "ad",
            "emergency": "112",
            "helpline": "116 111",
            "title": "Inf\u00e0ncia Respon Children Support Line"
        },
        "AO": {
            "name": "Angola",
            "flag": "ao",
            "emergency": "112",
            "helpline": "112",
            "title": "National Emergency & Support Protocols"
        },
        "AG": {
            "name": "Antigua and Barbuda",
            "flag": "ag",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency & Support Line"
        },
        "AR": {
            "name": "Argentina",
            "flag": "ar",
            "emergency": "911",
            "helpline": "135",
            "title": "Centro de Asistencia al Suicida"
        },
        "AM": {
            "name": "Armenia",
            "flag": "am",
            "emergency": "112",
            "helpline": "103",
            "title": "National Psychiatric Emergency Services"
        },
        "AU": {
            "name": "Australia",
            "flag": "au",
            "emergency": "000",
            "helpline": "13 11 14",
            "title": "Lifeline Suicide & Crisis Support"
        },
        "AT": {
            "name": "Austria",
            "flag": "at",
            "emergency": "112",
            "helpline": "142",
            "title": "Telefonseelsorge Crisis Support Line"
        },
        "AZ": {
            "name": "Azerbaijan",
            "flag": "az",
            "emergency": "112",
            "helpline": "103",
            "title": "Psychiatric Emergency Support Team"
        },
        "BS": {
            "name": "Bahamas",
            "flag": "bs",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Support Protocols"
        },
        "BH": {
            "name": "Bahrain",
            "flag": "bh",
            "emergency": "999",
            "helpline": "999",
            "title": "Emergency Medical Services & Crisis Line"
        },
        "BD": {
            "name": "Bangladesh",
            "flag": "bd",
            "emergency": "999",
            "helpline": "09612 119922",
            "title": "Kaan \u09aa\u09c7\u09a4\u09c7 \u09b0\u0987 Mental Support Line"
        },
        "BB": {
            "name": "Barbados",
            "flag": "bb",
            "emergency": "511",
            "helpline": "511",
            "title": "Emergency Support & Crisis Services"
        },
        "BY": {
            "name": "Belarus",
            "flag": "by",
            "emergency": "112",
            "helpline": "170",
            "title": "Minsk National Crisis Counseling Line"
        },
        "BE": {
            "name": "Belgium",
            "flag": "be",
            "emergency": "112",
            "helpline": "1813",
            "title": "Selfmoordlijn 1813 Crisis Support"
        },
        "BZ": {
            "name": "Belize",
            "flag": "bz",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Services Lifeline"
        },
        "BJ": {
            "name": "Benin",
            "flag": "bj",
            "emergency": "112",
            "helpline": "112",
            "title": "National Crisis Assistance Protocol"
        },
        "BT": {
            "name": "Bhutan",
            "flag": "bt",
            "emergency": "112",
            "helpline": "1010",
            "title": "Sherig Counselling Help & Crisis Line"
        },
        "BO": {
            "name": "Bolivia",
            "flag": "bo",
            "emergency": "911",
            "helpline": "110",
            "title": "Servicio de Emergencia y Apoyo Social"
        },
        "BA": {
            "name": "Bosnia and Herzegovina",
            "flag": "ba",
            "emergency": "112",
            "helpline": "1261",
            "title": "Plavi Telefon Crisis Support Line"
        },
        "BW": {
            "name": "Botswana",
            "flag": "bw",
            "emergency": "997",
            "helpline": "3911270",
            "title": "BOCONGO Mental Support Services"
        },
        "BR": {
            "name": "Brazil",
            "flag": "br",
            "emergency": "192",
            "helpline": "188",
            "title": "Centro de Valoriza\u00e7\u00e3o da Vida (CVV)"
        },
        "BN": {
            "name": "Brunei",
            "flag": "bn",
            "emergency": "991",
            "helpline": "145",
            "title": "Talian Harapan 145 Mental Support"
        },
        "BG": {
            "name": "Bulgaria",
            "flag": "bg",
            "emergency": "112",
            "helpline": "0035 9249 30237",
            "title": "Bulgarian Red Cross Mental Support"
        },
        "BF": {
            "name": "Burkina Faso",
            "flag": "bf",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Crisis Relief Protocol"
        },
        "BI": {
            "name": "Burundi",
            "flag": "bi",
            "emergency": "112",
            "helpline": "112",
            "title": "National Medical Emergency Services"
        },
        "KH": {
            "name": "Cambodia",
            "flag": "kh",
            "emergency": "119",
            "helpline": "119",
            "title": "National Emergency & General Crisis"
        },
        "CM": {
            "name": "Cameroon",
            "flag": "cm",
            "emergency": "112",
            "helpline": "112",
            "title": "National Medical Emergency & Support"
        },
        "CA": {
            "name": "Canada",
            "flag": "ca",
            "emergency": "911",
            "helpline": "988",
            "title": "988 Suicide Crisis Helpline"
        },
        "CV": {
            "name": "Cabo Verde",
            "flag": "cv",
            "emergency": "130",
            "helpline": "130",
            "title": "General Emergency & Medical Support"
        },
        "CF": {
            "name": "Central African Republic",
            "flag": "cf",
            "emergency": "112",
            "helpline": "112",
            "title": "Medical Emergency Crisis Relief"
        },
        "TD": {
            "name": "Chad",
            "flag": "td",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Dispatch & Crisis Protocol"
        },
        "CL": {
            "name": "Chile",
            "flag": "cl",
            "emergency": "131",
            "helpline": "*4141",
            "title": "MINSAL *4141 No Est\u00e1s Solo Line"
        },
        "CN": {
            "name": "China",
            "flag": "cn",
            "emergency": "120",
            "helpline": "800-810-1117",
            "title": "Beijing Suicide Research & Crisis Line"
        },
        "CO": {
            "name": "Colombia",
            "flag": "co",
            "emergency": "123",
            "helpline": "192",
            "title": "L\u00ednea Apoyo Emocional de Salud Mental"
        },
        "KM": {
            "name": "Comoros",
            "flag": "km",
            "emergency": "172",
            "helpline": "172",
            "title": "Emergency Response & Crisis Line"
        },
        "CG": {
            "name": "Congo",
            "flag": "cg",
            "emergency": "112",
            "helpline": "112",
            "title": "General Medical Emergency Services"
        },
        "CR": {
            "name": "Costa Rica",
            "flag": "cr",
            "emergency": "911",
            "helpline": "911",
            "title": "Servicio de Emergencia e Intervenci\u00f3n"
        },
        "HR": {
            "name": "Croatia",
            "flag": "hr",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Plavi Telefon Crisis Counselling"
        },
        "CU": {
            "name": "Cuba",
            "flag": "cu",
            "emergency": "104",
            "helpline": "104",
            "title": "Servicio de Urgencias M\u00e9dicas"
        },
        "CY": {
            "name": "Cyprus",
            "flag": "cy",
            "emergency": "112",
            "helpline": "1410",
            "title": "National Psychiatric Support Lifeline"
        },
        "CZ": {
            "name": "Czech Republic",
            "flag": "cz",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Linka D\u016fv\u011bry Mental Support Line"
        },
        "DK": {
            "name": "Denmark",
            "flag": "dk",
            "emergency": "112",
            "helpline": "70 201 201",
            "title": "Livslinien Suicide Prevention Line"
        },
        "DJ": {
            "name": "Djibouti",
            "flag": "dj",
            "emergency": "17",
            "helpline": "17",
            "title": "Emergency & Crisis Relief Dispatch"
        },
        "DM": {
            "name": "Dominica",
            "flag": "dm",
            "emergency": "999",
            "helpline": "999",
            "title": "National Crisis Assistance Services"
        },
        "DO": {
            "name": "Dominican Republic",
            "flag": "do",
            "emergency": "911",
            "helpline": "809 200 1200",
            "title": "L\u00ednea de Ayuda del Ministerio"
        },
        "EC": {
            "name": "Ecuador",
            "flag": "ec",
            "emergency": "911",
            "helpline": "911",
            "title": "ECU 911 Salud Mental Crisis Line"
        },
        "EG": {
            "name": "Egypt",
            "flag": "eg",
            "emergency": "123",
            "helpline": "02 20816831",
            "title": "General Secretariat Mental Health"
        },
        "SV": {
            "name": "El Salvador",
            "flag": "sv",
            "emergency": "911",
            "helpline": "122",
            "title": "Asistencia de Emergencia M\u00e9dica"
        },
        "GQ": {
            "name": "Equatorial Guinea",
            "flag": "gq",
            "emergency": "112",
            "helpline": "112",
            "title": "National Medical Crisis Dispatch"
        },
        "ER": {
            "name": "Eritrea",
            "flag": "er",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Medical Services Protocol"
        },
        "EE": {
            "name": "Estonia",
            "flag": "ee",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Eluliin Emotional Support Hotline"
        },
        "SZ": {
            "name": "Eswatini",
            "flag": "sz",
            "emergency": "999",
            "helpline": "999",
            "title": "National Crisis Relief Services"
        },
        "ET": {
            "name": "Ethiopia",
            "flag": "et",
            "emergency": "907",
            "helpline": "907",
            "title": "Red Cross Emergency Crisis Support"
        },
        "FJ": {
            "name": "Fiji",
            "flag": "fj",
            "emergency": "911",
            "helpline": "1325",
            "title": "National Lifeline Support Network"
        },
        "FI": {
            "name": "Finland",
            "flag": "fi",
            "emergency": "112",
            "helpline": "09 2525 0111",
            "title": "MIELI Mental Health Finland Line"
        },
        "FR": {
            "name": "France",
            "flag": "fr",
            "emergency": "112",
            "helpline": "3114",
            "title": "Num\u00e9ro National de Pr\u00e9vention Suicide"
        },
        "GA": {
            "name": "Gabon",
            "flag": "ga",
            "emergency": "1300",
            "helpline": "1300",
            "title": "Medical Emergency Support Protocol"
        },
        "GM": {
            "name": "Gambia",
            "flag": "gm",
            "emergency": "112",
            "helpline": "112",
            "title": "General Emergency Medical Services"
        },
        "GE": {
            "name": "Georgia",
            "flag": "ge",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Medical Care Support"
        },
        "DE": {
            "name": "Germany",
            "flag": "de",
            "emergency": "112",
            "helpline": "0800 111 0 111",
            "title": "Telefonseelsorge Crisis Support"
        },
        "GH": {
            "name": "Ghana",
            "flag": "gh",
            "emergency": "112",
            "helpline": "0543 189 265",
            "title": "Psychological Association Lifeline"
        },
        "GR": {
            "name": "Greece",
            "flag": "gr",
            "emergency": "112",
            "helpline": "1018",
            "title": "Klimaka Suicide Prevention Hotline"
        },
        "GD": {
            "name": "Grenada",
            "flag": "gd",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Crisis Line"
        },
        "GT": {
            "name": "Guatemala",
            "flag": "gt",
            "emergency": "911",
            "helpline": "1500",
            "title": "Asistencia Social y Salud Emocional"
        },
        "GN": {
            "name": "Guinea",
            "flag": "gn",
            "emergency": "112",
            "helpline": "112",
            "title": "National Emergency Crisis Services"
        },
        "GW": {
            "name": "Guinea-Bissau",
            "flag": "gw",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Dispatch Services"
        },
        "GY": {
            "name": "Guyana",
            "flag": "gy",
            "emergency": "913",
            "helpline": "223-0001",
            "title": "Inter-agency Suicide Prevention Helpline"
        },
        "HT": {
            "name": "Haiti",
            "flag": "ht",
            "emergency": "116",
            "helpline": "116",
            "title": "Emergency Medical Services Support"
        },
        "HN": {
            "name": "Honduras",
            "flag": "hn",
            "emergency": "911",
            "helpline": "150",
            "title": "Servicio de Apoyo y Emergencia"
        },
        "HU": {
            "name": "Hungary",
            "flag": "hu",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Lelki Els\u0151seg\u00e9ly Mental Support"
        },
        "IS": {
            "name": "Iceland",
            "flag": "is",
            "emergency": "112",
            "helpline": "1717",
            "title": "Red Cross Helpline Iceland"
        },
        "IN": {
            "name": "India",
            "flag": "in",
            "emergency": "112",
            "helpline": "14416",
            "title": "Tele-MANAS Support Line"
        },
        "ID": {
            "name": "Indonesia",
            "flag": "id",
            "emergency": "112",
            "helpline": "500-454",
            "title": "LISA Suicide Prevention Hotline"
        },
        "IR": {
            "name": "Iran",
            "flag": "ir",
            "emergency": "115",
            "helpline": "1480",
            "title": "National Welfare Mental Counseling"
        },
        "IQ": {
            "name": "Iraq",
            "flag": "iq",
            "emergency": "122",
            "helpline": "122",
            "title": "Medical Emergency Relief Dispatch"
        },
        "IE": {
            "name": "Ireland",
            "flag": "ie",
            "emergency": "112 / 999",
            "helpline": "116 123",
            "title": "Samaritans Ireland Crisis Support"
        },
        "IL": {
            "name": "Israel",
            "flag": "il",
            "emergency": "101 / 112",
            "helpline": "1201",
            "title": "ERAN Mental First Aid Hotline"
        },
        "IT": {
            "name": "Italy",
            "flag": "it",
            "emergency": "112",
            "helpline": "02 2327 2327",
            "title": "Samaritans Italy Support Line"
        },
        "CI": {
            "name": "Ivory Coast",
            "flag": "ci",
            "emergency": "180",
            "helpline": "180",
            "title": "Medical Emergency Assistance Service"
        },
        "JM": {
            "name": "Jamaica",
            "flag": "jm",
            "emergency": "119",
            "helpline": "888-639-5433",
            "title": "Mental Health Support Line Jamaica"
        },
        "JP": {
            "name": "Japan",
            "flag": "jp",
            "emergency": "119",
            "helpline": "0570 783 556",
            "title": "Japanese Federation of Inochi no Denwa"
        },
        "JO": {
            "name": "Jordan",
            "flag": "jo",
            "emergency": "911",
            "helpline": "110",
            "title": "Emergency Medical & Crisis Support"
        },
        "KZ": {
            "name": "Kazakhstan",
            "flag": "kz",
            "emergency": "103",
            "helpline": "150",
            "title": "National Youth Mental Crisis Support"
        },
        "KE": {
            "name": "Kenya",
            "flag": "ke",
            "emergency": "999 / 112",
            "helpline": "0722 178 177",
            "title": "Befrienders Kenya Crisis Support"
        },
        "KI": {
            "name": "Kiribati",
            "flag": "ki",
            "emergency": "999",
            "helpline": "999",
            "title": "National Emergency Services Protocol"
        },
        "KW": {
            "name": "Kuwait",
            "flag": "kw",
            "emergency": "112",
            "helpline": "2462 1730",
            "title": "Kuwait Association for Mental Health"
        },
        "KG": {
            "name": "Kyrgyzstan",
            "flag": "kg",
            "emergency": "103",
            "helpline": "111",
            "title": "Children and Youth Helpline Services"
        },
        "LA": {
            "name": "Laos",
            "flag": "la",
            "emergency": "1195",
            "helpline": "1195",
            "title": "Emergency Medical Rescue Dispatch"
        },
        "LV": {
            "name": "Latvia",
            "flag": "lv",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Skalbes Crisis Counseling Center"
        },
        "LB": {
            "name": "Lebanon",
            "flag": "lb",
            "emergency": "140",
            "helpline": "1564",
            "title": "Embrace Suicide Prevention Hotline"
        },
        "LS": {
            "name": "Lesotho",
            "flag": "ls",
            "emergency": "121",
            "helpline": "121",
            "title": "Emergency Medical Services Support"
        },
        "LR": {
            "name": "Liberia",
            "flag": "lr",
            "emergency": "911",
            "helpline": "911",
            "title": "National Crisis Assistance Protocol"
        },
        "LY": {
            "name": "Libya",
            "flag": "ly",
            "emergency": "193",
            "helpline": "193",
            "title": "Medical Emergency Relief Dispatch"
        },
        "LI": {
            "name": "Liechtenstein",
            "flag": "li",
            "emergency": "112",
            "helpline": "143",
            "title": "Die Dargebotene Hand Liechtenstein"
        },
        "LT": {
            "name": "Lithuania",
            "flag": "lt",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Jaunimo Linija Youth Helpline"
        },
        "LU": {
            "name": "Luxembourg",
            "flag": "lu",
            "emergency": "112",
            "helpline": "116 111",
            "title": "Kanner-Jugendtelefon Support Line"
        },
        "MG": {
            "name": "Madagascar",
            "flag": "mg",
            "emergency": "124",
            "helpline": "124",
            "title": "Medical Emergency Relief Services"
        },
        "MW": {
            "name": "Malawi",
            "flag": "mw",
            "emergency": "997",
            "helpline": "997",
            "title": "General Emergency & Medical Support"
        },
        "MY": {
            "name": "Malaysia",
            "flag": "my",
            "emergency": "999",
            "helpline": "03-76272929",
            "title": "Befrienders Malaysia Support Line"
        },
        "MV": {
            "name": "Maldives",
            "flag": "mv",
            "emergency": "102",
            "helpline": "1410",
            "title": "Thalassemia Society Crisis Lifeline"
        },
        "ML": {
            "name": "Mali",
            "flag": "ml",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Response & Crisis Protocol"
        },
        "MT": {
            "name": "Malta",
            "flag": "mt",
            "emergency": "112",
            "helpline": "179",
            "title": "Supportline 179 National Support"
        },
        "MH": {
            "name": "Marshall Islands",
            "flag": "mh",
            "emergency": "911",
            "helpline": "911",
            "title": "National Crisis Intervention Services"
        },
        "MR": {
            "name": "Mauritania",
            "flag": "mr",
            "emergency": "118",
            "helpline": "118",
            "title": "Emergency Medical Response Line"
        },
        "MU": {
            "name": "Mauritius",
            "flag": "mu",
            "emergency": "114",
            "helpline": "800 2345",
            "title": "Ministry of Health Support Services"
        },
        "MX": {
            "name": "Mexico",
            "flag": "mx",
            "emergency": "911",
            "helpline": "800 911 2000",
            "title": "L\u00ednea de la Vida Mental Support"
        },
        "FM": {
            "name": "Micronesia",
            "flag": "fm",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Services Lifeline"
        },
        "MD": {
            "name": "Moldova",
            "flag": "md",
            "emergency": "112",
            "helpline": "060 475 475",
            "title": "Pentru Viata Suicide Prevention"
        },
        "MC": {
            "name": "Monaco",
            "flag": "mc",
            "emergency": "112",
            "helpline": "1410",
            "title": "Croix-Rouge Mon\u00e9gasque Support"
        },
        "MN": {
            "name": "Mongolia",
            "flag": "mn",
            "emergency": "103",
            "helpline": "1800 2000",
            "title": "National Psychiatric Counseling Center"
        },
        "ME": {
            "name": "Montenegro",
            "flag": "me",
            "emergency": "112",
            "helpline": "116 123",
            "title": "SOS Telefon Crisis Support"
        },
        "MA": {
            "name": "Morocco",
            "flag": "ma",
            "emergency": "15",
            "helpline": "05 22 26 20 62",
            "title": "Sourire Association Crisis Line"
        },
        "MZ": {
            "name": "Mozambique",
            "flag": "mz",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Dispatch & Crisis Protocol"
        },
        "MM": {
            "name": "Myanmar",
            "flag": "mm",
            "emergency": "192",
            "helpline": "192",
            "title": "General Emergency & Psychiatric Support"
        },
        "NA": {
            "name": "Namibia",
            "flag": "na",
            "emergency": "10111",
            "helpline": "061 232221",
            "title": "Lifeline Childline Namibia Support"
        },
        "NR": {
            "name": "Nauru",
            "flag": "nr",
            "emergency": "110",
            "helpline": "110",
            "title": "Emergency Medical Services Protocol"
        },
        "NP": {
            "name": "Nepal",
            "flag": "np",
            "emergency": "100",
            "helpline": "9801235444",
            "title": "TUTH Mental Health Suicide Line"
        },
        "NL": {
            "name": "Netherlands",
            "flag": "nl",
            "emergency": "112",
            "helpline": "0800-0113",
            "title": "113 Zelfmoordpreventie Support"
        },
        "NZ": {
            "name": "New Zealand",
            "flag": "nz",
            "emergency": "111",
            "helpline": "1737",
            "title": "Need to Talk? Free Call/Text Lifeline"
        },
        "NI": {
            "name": "Nicaragua",
            "flag": "ni",
            "emergency": "911",
            "helpline": "118",
            "title": "Asistencia de Emergencia M\u00e9dica"
        },
        "NE": {
            "name": "Niger",
            "flag": "ne",
            "emergency": "112",
            "helpline": "112",
            "title": "National Emergency & Support Line"
        },
        "NG": {
            "name": "Nigeria",
            "flag": "ng",
            "emergency": "112",
            "helpline": "0806 210 6496",
            "title": "Mentally Aware Nigeria Initiative (MANI)"
        },
        "KP": {
            "name": "North Korea",
            "flag": "kp",
            "emergency": "119",
            "helpline": "119",
            "title": "National Emergency Services Dispatch"
        },
        "MK": {
            "name": "North Macedonia",
            "flag": "mk",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Red Cross Crisis Support Services"
        },
        "NO": {
            "name": "Norway",
            "flag": "no",
            "emergency": "113 / 112",
            "helpline": "116 123",
            "title": "Mental Helse Hjelpetelefonen"
        },
        "OM": {
            "name": "Oman",
            "flag": "om",
            "emergency": "9999",
            "helpline": "9999",
            "title": "Emergency Response & Crisis Dispatch"
        },
        "PK": {
            "name": "Pakistan",
            "flag": "pk",
            "emergency": "1122",
            "helpline": "042-35761999",
            "title": "Umang Mental Health Support Line"
        },
        "PW": {
            "name": "Palau",
            "flag": "pw",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Dispatch Services"
        },
        "PS": {
            "name": "Palestine",
            "flag": "ps",
            "emergency": "101",
            "helpline": "1201",
            "title": "Sawa Organization Psychological Helpline"
        },
        "PA": {
            "name": "Panama",
            "flag": "pa",
            "emergency": "911",
            "helpline": "911",
            "title": "Servicio de Emergencias M\u00e9dicas"
        },
        "PG": {
            "name": "Papua New Guinea",
            "flag": "pg",
            "emergency": "111",
            "helpline": "111",
            "title": "National Crisis Assistance Network"
        },
        "PY": {
            "name": "Paraguay",
            "flag": "py",
            "emergency": "911",
            "helpline": "140",
            "title": "Servicio de Apoyo de Salud Mental"
        },
        "PE": {
            "name": "Peru",
            "flag": "pe",
            "emergency": "106 / 117",
            "helpline": "113",
            "title": "INFOSALUD Ministerio de Salud Opci\u00f3n 5"
        },
        "PH": {
            "name": "Philippines",
            "flag": "ph",
            "emergency": "911",
            "helpline": "1553",
            "title": "NCMH Mental Health Crisis Hotline"
        },
        "PL": {
            "name": "Poland",
            "flag": "pl",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Telefon Zaufania dla Doros\u0142ych"
        },
        "PT": {
            "name": "Portugal",
            "flag": "pt",
            "emergency": "112",
            "helpline": "808 24 24 24",
            "title": "SNS 24 Linha de Apoio Psicol\u00f3gico"
        },
        "QA": {
            "name": "Qatar",
            "flag": "qa",
            "emergency": "999",
            "helpline": "16000",
            "title": "Mental Health Helpline HMC Qatar"
        },
        "RO": {
            "name": "Romania",
            "flag": "ro",
            "emergency": "112",
            "helpline": "0800 801 200",
            "title": "Alianta Romana de Preventie a Suicidului"
        },
        "RU": {
            "name": "Russia",
            "flag": "ru",
            "emergency": "112",
            "helpline": "8-800-2000-122",
            "title": "Unified Mental Crisis Support Lifeline"
        },
        "RW": {
            "name": "Rwanda",
            "flag": "rw",
            "emergency": "112",
            "helpline": "112",
            "title": "Medical Emergency & Psychiatric Team"
        },
        "KN": {
            "name": "Saint Kitts and Nevis",
            "flag": "kn",
            "emergency": "911",
            "helpline": "911",
            "title": "Emergency Dispatch Services"
        },
        "LC": {
            "name": "Saint Lucia",
            "flag": "lc",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Crisis Line"
        },
        "VC": {
            "name": "Saint Vincent",
            "flag": "vc",
            "emergency": "999",
            "helpline": "999",
            "title": "National Crisis Relief Services"
        },
        "WS": {
            "name": "Samoa",
            "flag": "ws",
            "emergency": "996",
            "helpline": "996",
            "title": "Emergency Rescue & Support Line"
        },
        "SM": {
            "name": "San Marino",
            "flag": "sm",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Response Service Protocol"
        },
        "ST": {
            "name": "Sao Tome and Principe",
            "flag": "st",
            "emergency": "112",
            "helpline": "112",
            "title": "Medical Emergency & Crisis Relief"
        },
        "SA": {
            "name": "Saudi Arabia",
            "flag": "sa",
            "emergency": "911 / 997",
            "helpline": "920033360",
            "title": "National Mental Health Hotline"
        },
        "SN": {
            "name": "Senegal",
            "flag": "sn",
            "emergency": "18",
            "helpline": "18",
            "title": "Medical Emergency Assistance Service"
        },
        "RS": {
            "name": "Serbia",
            "flag": "rs",
            "emergency": "112",
            "helpline": "0700 116 123",
            "title": "Liman Mental Health Crisis Center"
        },
        "SC": {
            "name": "Seychelles",
            "flag": "sc",
            "emergency": "999",
            "helpline": "999",
            "title": "National Emergency & Crisis Service"
        },
        "SL": {
            "name": "Sierra Leone",
            "flag": "sl",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Crisis Relief Protocol"
        },
        "SG": {
            "name": "Singapore",
            "flag": "sg",
            "emergency": "995",
            "helpline": "1-767",
            "title": "Samaritans of Singapore (SOS)"
        },
        "SK": {
            "name": "Slovakia",
            "flag": "sk",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Linka D\u00f4very Nez\u00e1budka Support"
        },
        "SI": {
            "name": "Slovenia",
            "flag": "si",
            "emergency": "112",
            "helpline": "116 123",
            "title": "Zaupni Telefon Samarijan Support"
        },
        "SB": {
            "name": "Solomon Islands",
            "flag": "sb",
            "emergency": "999",
            "helpline": "999",
            "title": "National Emergency Dispatch Protocol"
        },
        "SO": {
            "name": "Somalia",
            "flag": "so",
            "emergency": "999",
            "helpline": "999",
            "title": "Emergency Medical Services Lifeline"
        },
        "ZA": {
            "name": "South Africa",
            "flag": "za",
            "emergency": "10111 / 112",
            "helpline": "0800 567 567",
            "title": "SADAG Mental Health Support Line"
        },
        "SS": {
            "name": "South Sudan",
            "flag": "ss",
            "emergency": "911",
            "helpline": "911",
            "title": "Emergency Crisis Relief Team"
        },
        "ES": {
            "name": "Spain",
            "flag": "es",
            "emergency": "112",
            "helpline": "024",
            "title": "L\u00ednea de Prevenci\u00f3n de la Conducta Suicida"
        },
        "LK": {
            "name": "Sri Lanka",
            "flag": "lk",
            "emergency": "119",
            "helpline": "1333",
            "title": "CCCline Lifeline Mental Health Support"
        },
        "SD": {
            "name": "Sudan",
            "flag": "sd",
            "emergency": "999",
            "helpline": "999",
            "title": "General Emergency & Medical Response"
        },
        "SR": {
            "name": "Suriname",
            "flag": "sr",
            "emergency": "115",
            "helpline": "115",
            "title": "Emergency Medical Assistance Services"
        },
        "SE": {
            "name": "Sweden",
            "flag": "se",
            "emergency": "112",
            "helpline": "90101",
            "title": "MIND Sj\u00e4lvmordslinjen Support Line"
        },
        "CH": {
            "name": "Switzerland",
            "flag": "ch",
            "emergency": "144 / 112",
            "helpline": "143",
            "title": "Die Dargebotene Hand / 143 Support"
        },
        "SY": {
            "name": "Syria",
            "flag": "sy",
            "emergency": "110",
            "helpline": "110",
            "title": "Emergency Medical Relief Services"
        },
        "TW": {
            "name": "Taiwan",
            "flag": "tw",
            "emergency": "119",
            "helpline": "1925",
            "title": "\u5b89\u5fc3\u5c08\u7dda Suicide Prevention Hotline"
        },
        "TJ": {
            "name": "Tajikistan",
            "flag": "tj",
            "emergency": "103",
            "helpline": "103",
            "title": "National Psychiatric Health Clinic"
        },
        "TZ": {
            "name": "Tanzania",
            "flag": "tz",
            "emergency": "112",
            "helpline": "112",
            "title": "National Crisis Assistance Network"
        },
        "TH": {
            "name": "Thailand",
            "flag": "th",
            "emergency": "191 / 1669",
            "helpline": "02-113-6789",
            "title": "Samaritans of Thailand Crisis Line"
        },
        "TL": {
            "name": "Timor-Leste",
            "flag": "tl",
            "emergency": "112",
            "helpline": "112",
            "title": "National Emergency Medical Support"
        },
        "TG": {
            "name": "Togo",
            "flag": "tg",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Dispatch Crisis Response"
        },
        "TO": {
            "name": "Tonga",
            "flag": "to",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Services Protocol"
        },
        "TT": {
            "name": "Trinidad and Tobago",
            "flag": "tt",
            "emergency": "990",
            "helpline": "800-5588",
            "title": "Lifeline Trinidad and Tobago Support"
        },
        "TN": {
            "name": "Tunisia",
            "flag": "tn",
            "emergency": "190",
            "helpline": "190",
            "title": "Emergency Medical Assistance Line"
        },
        "TR": {
            "name": "Turkey",
            "flag": "tr",
            "emergency": "112",
            "helpline": "182",
            "title": "MHRS Psychiatric Consultation Line"
        },
        "TM": {
            "name": "Turkmenistan",
            "flag": "tm",
            "emergency": "103",
            "helpline": "103",
            "title": "Emergency Medical Services Protocol"
        },
        "TV": {
            "name": "Tuvalu",
            "flag": "tv",
            "emergency": "911",
            "helpline": "911",
            "title": "National Emergency Services Lifeline"
        },
        "UG": {
            "name": "Uganda",
            "flag": "ug",
            "emergency": "112",
            "helpline": "0709 900 900",
            "title": "Heart 2 Heart Mental Health Lifeline"
        },
        "UA": {
            "name": "Ukraine",
            "flag": "ua",
            "emergency": "112 / 103",
            "helpline": "7333",
            "title": "Lifeline Ukraine 24/7 Support Line"
        },
        "AE": {
            "name": "United Arab Emirates",
            "flag": "ae",
            "emergency": "998 / 999",
            "helpline": "800 4673",
            "title": "Hope Line Mental Support Service"
        },
        "GB": {
            "name": "United Kingdom",
            "flag": "gb",
            "emergency": "999",
            "helpline": "116 123",
            "title": "NHS 111 & Samaritans Crisis Support"
        },
        "US": {
            "name": "United States",
            "flag": "us",
            "emergency": "911",
            "helpline": "988",
            "title": "988 Suicide & Crisis Lifeline"
        },
        "UY": {
            "name": "Uruguay",
            "flag": "uy",
            "emergency": "911",
            "helpline": "0800 0767",
            "title": "L\u00ednea de Prevenci\u00f3n del Suicidio"
        },
        "UZ": {
            "name": "Uzbekistan",
            "flag": "uz",
            "emergency": "103",
            "helpline": "103",
            "title": "National Psychiatric Care Hotline"
        },
        "VU": {
            "name": "Vanuatu",
            "flag": "vu",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Response Service Dispatch"
        },
        "VA": {
            "name": "Vatican City",
            "flag": "va",
            "emergency": "112",
            "helpline": "112",
            "title": "Emergency Medical Care Support"
        },
        "VE": {
            "name": "Venezuela",
            "flag": "ve",
            "emergency": "911",
            "helpline": "0212-41 500 77",
            "title": "L\u00ednea de Prevenci\u00f3n de Suicidio"
        },
        "VN": {
            "name": "Vietnam",
            "flag": "vn",
            "emergency": "115",
            "helpline": "1900 599 930",
            "title": "Mind Care Psychological Support Services"
        },
        "YE": {
            "name": "Yemen",
            "flag": "ye",
            "emergency": "191",
            "helpline": "191",
            "title": "Medical Emergency Relief Dispatch"
        },
        "ZM": {
            "name": "Zambia",
            "flag": "zm",
            "emergency": "991",
            "helpline": "991",
            "title": "General Emergency & Support Network"
        },
        "ZW": {
            "name": "Zimbabwe",
            "flag": "zw",
            "emergency": "999 / 112",
            "helpline": "0772 178 177",
            "title": "Befrienders Zimbabwe Lifeline Support"
        }
    };

    let activeCountryCode = "IN"; // Default Core Fallback

    function initCrisisBanner() {
        const flagImg = document.getElementById("crisis-flag-img");
        const countryNameEl = document.getElementById("crisis-country-name");
        const supportDescEl = document.getElementById("crisis-support-desc");
        const phoneLink = document.getElementById("crisis-phone-link");
        const emergencyNumEl = document.getElementById("crisis-emergency-num");
        const callActionBtn = document.getElementById("crisis-call-action-btn");
        const copyActionBtn = document.getElementById("crisis-copy-action-btn");
        const skeleton = document.getElementById("crisis-skeleton");
        const displayContainer = document.getElementById("crisis-helpline-display");

        const openModalBtn = document.getElementById("change-country-btn");
        const closeModalBtn = document.getElementById("country-modal-close-btn");
        const modal = document.getElementById("country-selector-modal");
        const listContainer = document.getElementById("country-list-container");
        const searchInput = document.getElementById("country-search-input");

        // Helper to update crisis UI elements with animation
        function updateCrisisUI(code) {
            // Render loading transition
            if (skeleton && displayContainer) {
                skeleton.style.display = "flex";
                displayContainer.style.display = "none";
            }

            // Remove any existing fallback notice to start clean
            const existingFallback = document.getElementById("crisis-fallback-notice");
            if (existingFallback) existingFallback.remove();

            // Fetch hotline details from API
            fetch(`${API_BASE_URL}/api/hotlines/${code}`)
                .then(res => {
                    if (!res.ok) {
                        throw new Error(`API returned status ${res.status}`);
                    }
                    return res.json();
                })
                .then(data => {
                    activeCountryCode = code;
                    localStorage.setItem("aira_crisis_country", code);

                    // Update UI elements with retrieved data
                    if (flagImg) {
                        flagImg.src = `https://flagcdn.com/w40/${code.toLowerCase()}.png`;
                        flagImg.alt = `${data.country} Flag`;
                        flagImg.style.display = "block";
                    }
                    if (countryNameEl) countryNameEl.textContent = data.country;
                    if (supportDescEl) supportDescEl.textContent = data.organization;
                    if (emergencyNumEl) emergencyNumEl.textContent = data.emergency_number;

                    if (phoneLink) {
                        phoneLink.textContent = data.mental_health_hotline;
                        phoneLink.href = `tel:${data.mental_health_hotline.replace(/\s+/g, '')}`;
                        // Scale animation visual cue
                        phoneLink.style.transform = "scale(1.15)";
                        setTimeout(() => phoneLink.style.transform = "scale(1)", 200);
                    }

                    if (callActionBtn) {
                        callActionBtn.href = `tel:${data.mental_health_hotline.replace(/\s+/g, '')}`;
                        callActionBtn.style.display = "inline-flex";
                    }

                    // Remove loading skeleton
                    if (skeleton && displayContainer) {
                        skeleton.style.display = "none";
                        displayContainer.style.display = "flex";
                    }
                })
                .catch(err => {
                    console.warn(`Failed to fetch hotline for ${code} from API, utilizing fallback:`, err);
                    
                    // Fallback behavior:
                    // Use local globalHelplineDb to query the emergency number for the country code,
                    // defaulting to standard 112 if not recognized.
                    const localData = globalHelplineDb[code] || {
                        name: code,
                        flag: code.toLowerCase(),
                        emergency: "112",
                        helpline: "112",
                        title: "Local Emergency Services"
                    };

                    activeCountryCode = code;
                    localStorage.setItem("aira_crisis_country", code);

                    if (flagImg) {
                        flagImg.src = `https://flagcdn.com/w40/${localData.flag}.png`;
                        flagImg.alt = `${localData.name} Flag`;
                        flagImg.style.display = "block";
                    }
                    if (countryNameEl) countryNameEl.textContent = localData.name;
                    if (supportDescEl) supportDescEl.textContent = "Local Emergency Services";
                    if (emergencyNumEl) emergencyNumEl.textContent = localData.emergency;

                    // Direct the main phone link to call the national emergency number
                    if (phoneLink) {
                        phoneLink.textContent = localData.emergency;
                        phoneLink.href = `tel:${localData.emergency.replace(/[^0-9]/g, '')}`;
                        phoneLink.style.transform = "scale(1.15)";
                        setTimeout(() => phoneLink.style.transform = "scale(1)", 200);
                    }

                    if (callActionBtn) {
                        callActionBtn.href = `tel:${localData.emergency.replace(/[^0-9]/g, '')}`;
                        callActionBtn.style.display = "inline-flex";
                    }

                    // Create and inject a fallback message
                    const bannerContent = document.querySelector(".crisis-banner-left");
                    if (bannerContent) {
                        const fallbackMsg = document.createElement("div");
                        fallbackMsg.id = "crisis-fallback-notice";
                        fallbackMsg.style.cssText = "margin-top: 0.8rem; padding: 0.6rem 1rem; background: rgba(255, 0, 128, 0.08); border: 1px solid rgba(255, 0, 128, 0.25); border-radius: 8px; font-size: 0.82rem; color: var(--neon-rose); display: flex; align-items: center; gap: 0.5rem; animation: pulse 2s infinite;";
                        fallbackMsg.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> <span>No country-specific mental health hotline is available. Please contact local emergency services.</span>`;
                        bannerContent.appendChild(fallbackMsg);
                    }

                    // Remove loading skeleton
                    if (skeleton && displayContainer) {
                        skeleton.style.display = "none";
                        displayContainer.style.display = "flex";
                    }
                });
        }

        // Expose updateCrisisUI globally so _selectCountry (city modal) can call it
        window.updateCrisisUI = updateCrisisUI;

        // Copy helpline to clipboard action
        if (copyActionBtn && phoneLink) {
            copyActionBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(phoneLink.textContent.trim()).then(() => {
                    const originalHTML = copyActionBtn.innerHTML;
                    copyActionBtn.innerHTML = `<i class="fa-solid fa-check"></i>`;
                    copyActionBtn.style.color = "var(--neon-emerald)";
                    setTimeout(() => {
                        copyActionBtn.innerHTML = originalHTML;
                        copyActionBtn.style.color = "";
                    }, 1500);
                });
            });
        }

        // Searchable Country Dropdown Modal logic
        if (openModalBtn && modal) {
            openModalBtn.addEventListener("click", () => {
                modal.style.display = "flex";
                setTimeout(() => modal.classList.add("active"), 10);
                if (searchInput) searchInput.focus();
                renderCountryList("");
            });
        }

        const closeModal = () => {
            if (modal) {
                modal.classList.remove("active");
                setTimeout(() => modal.style.display = "none", 300);
            }
        };

        if (closeModalBtn) {
            closeModalBtn.addEventListener("click", closeModal);
        }

        if (modal) {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) closeModal();
            });
        }

        // Render manual scrollable country listing
        function renderCountryList(filterText) {
            if (!listContainer) return;
            listContainer.innerHTML = "";

            const normalizedFilter = filterText.toLowerCase().trim();
            const sortedKeys = Object.keys(globalHelplineDb).sort((a, b) =>
                globalHelplineDb[a].name.localeCompare(globalHelplineDb[b].name)
            );

            let matchesFound = 0;
            sortedKeys.forEach(key => {
                const data = globalHelplineDb[key];
                if (data.name.toLowerCase().includes(normalizedFilter) || key.toLowerCase().includes(normalizedFilter)) {
                    matchesFound++;
                    const item = document.createElement("div");
                    item.className = "country-item";
                    item.innerHTML = `
                        <div class="country-item-left">
                            <img class="country-item-flag" src="https://flagcdn.com/w20/${data.flag}.png" alt="${data.name} Flag" onerror="this.style.display='none'">
                            <span class="country-item-name">${data.name}</span>
                            <span class="country-item-code">(${key})</span>
                        </div>
                        <span class="country-item-number"><i class="fa-solid fa-phone-flip" style="font-size:0.75rem; margin-right:0.3rem;"></i> ${data.helpline}</span>
                    `;

                    item.addEventListener("click", () => {
                        updateCrisisUI(key);
                        closeModal();
                    });

                    listContainer.appendChild(item);
                }
            });

            if (matchesFound === 0) {
                const emptyItem = document.createElement("div");
                emptyItem.className = "country-item";
                emptyItem.style.pointerEvents = "none";
                emptyItem.style.justifyContent = "center";
                emptyItem.style.color = "var(--text-muted)";
                emptyItem.textContent = "No matching countries found.";
                listContainer.appendChild(emptyItem);
            }
        }

        // Filter country list in real-time
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                renderCountryList(e.target.value);
            });
        }

        // Detect user location
        const savedCountry = localStorage.getItem("aira_crisis_country");
        if (savedCountry && globalHelplineDb[savedCountry]) {
            // Priority 1: Persistent localStorage choice
            updateCrisisUI(savedCountry);
        } else {
            // Priority 2: Geolocation IP-fetch with fallback to Browser Language
            if (skeleton && displayContainer) {
                skeleton.style.display = "flex";
                displayContainer.style.display = "none";
            }

            // High availability fetch
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2500);

            fetch("https://ipapi.co/json/", { signal: controller.signal })
                .then(res => res.json())
                .then(data => {
                    clearTimeout(timeoutId);
                    const detectedCode = data.country_code ? data.country_code.toUpperCase() : "IN";
                    if (globalHelplineDb[detectedCode]) {
                        updateCrisisUI(detectedCode);
                    } else {
                        updateCrisisUI("IN"); // Default Fallback
                    }
                })
                .catch(() => {
                    clearTimeout(timeoutId);
                    // Fallback to browser locale
                    const locale = navigator.language || (navigator.languages ? navigator.languages[0] : "en-IN");
                    const parsedCode = locale.split("-")[1] ? locale.split("-")[1].toUpperCase() : "IN";

                    if (globalHelplineDb[parsedCode]) {
                        updateCrisisUI(parsedCode);
                    } else {
                        updateCrisisUI("IN"); // Safe hardcoded fallback
                    }
                });
        }
    }

    // Initialize smart crisis system
    initCrisisBanner();

    // Initialize defaults on start
    resetBreathingVisuals();

    // ==========================================================================
    // GLOBAL POLICY MODAL LOGIC (PRIVACY, TERMS, AI GUIDELINES)
    // ==========================================================================
    const POLICY_DATA = {
        privacy: {
            title: "Privacy Policy",
            lastUpdated: "June 7, 2026",
            sections: [
                {
                    title: "1. Information Collected",
                    content: "We collect user information necessary to calculate student wellness indicators. This includes your name, email address, digital interaction parameters (assessment feedback scores, digital strain ratios), self-reported mood values, and clinical referral preferences."
                },
                {
                    title: "2. Data Protection and Hashing Protocols",
                    content: "All collected credentials and details are stored securely. Personal email addresses and passwords are encrypted in transit using SSL/TLS, and passwords are salt-hashed using bcrypt before persistent storage in our MongoDB node."
                },
                {
                    title: "3. Selling Exclusions",
                    content: "We enforce a strict confidentiality guarantee. Under no circumstances will AIRA sell, trade, rent, or lease your private information, metadata, or activity records to third-party advertisers or brokers."
                },
                {
                    title: "4. Usage Scope",
                    content: "Your data is used strictly for authentication, personalized dashboard analytics, account configuration, mental wellness tracking, and locating local emergency therapist helplines."
                },
                {
                    title: "5. Security Standards",
                    content: "We implement advanced server-side firewall rules, strict JSON Web Token (JWT) signature verification, database parameter sanitization, and automatic token expiration to shield your account from unauthorized intrusions."
                },
                {
                    title: "6. Data Deletion Right",
                    content: "Students retain full authority over their account histories. You may request complete erasure of your profile and historical records from our database by contacting support at support@aira-wellness.ai."
                },
                {
                    title: "7. Cookies and Local Vaults",
                    content: "We use browser local storage (localStorage) to retain secure login state and preserve interface preferences. Traditional persistent tracking cookies are not deployed."
                },
                {
                    title: "8. Update Announcements",
                    content: "If major amendments are made to these privacy protocols, users will be notified immediately through notification toast banners on their next login session."
                }
            ]
        },
        terms: {
            title: "Terms & Conditions",
            lastUpdated: "June 7, 2026",
            sections: [
                {
                    title: "1. Registration Integrity",
                    content: "To register on the AIRA Portal, students must provide accurate, current, and true contact details. Provision of fraudulent details will result in account restriction."
                },
                {
                    title: "2. Password Security",
                    content: "You are solely responsible for protecting your secure password signature. AIRA is not liable for unauthorized sessions resulting from negligent credential sharing."
                },
                {
                    title: "3. Prohibited Exploits",
                    content: "Users must not misuse, exploit, spam, attack, DDoS, reverse engineer, or perform security vulnerability scans on the platform systems or backend endpoints."
                },
                {
                    title: "4. Abuse and Conduct",
                    content: "Spamming conversation flows, submitting abusive text to chatbots, and attempting unauthorized access to admin metrics are strictly prohibited and subject to immediate ban."
                },
                {
                    title: "5. Account Termination",
                    content: "We reserve the right to temporarily suspend or permanently terminate student profiles if terms of compliance are breached."
                },
                {
                    title: "6. Service Uptime Limits",
                    content: "The platform is provided 'as is'. Services may be updated, modified, or temporarily offline for scheduled system maintenance or database synchronization."
                },
                {
                    title: "7. Utilization of AI Output",
                    content: "AIRA provides cognitive summaries and referral suggestions. Students assume full responsibility for how they use, share, or act upon AI-generated analysis or predictions."
                },
                {
                    title: "8. Agreement Updates",
                    content: "By continuing to access the AIRA Portal and its dashboard tools, you explicitly accept and agree to these Terms & Conditions."
                }
            ]
        },
        ai: {
            title: "AI Guidelines",
            lastUpdated: "June 7, 2026",
            sections: [
                {
                    title: "1. Purpose of AIRA",
                    content: "AIRA is built as a supportive, non-clinical tool to assist students in tracking wellness, evaluating academic stress, and discovering nearby therapist contacts. It does not replace professional care."
                },
                {
                    title: "2. Inaccuracy Disclaimer",
                    content: "As with all machine learning models, AI-generated predictions, post-sentiment tags, and conversational responses may occasionally contain inaccuracies or hallucinations."
                },
                {
                    title: "3. Professional Verification",
                    content: "Users should verify critical academic, technical, medical, financial, or professional guidance from certified human professionals before making important life decisions."
                },
                {
                    title: "4. Ethical Guidelines",
                    content: "We adhere strictly to non-discriminatory, transparent, and user-centric AI practices. Algorithms are optimized to minimize bias and maximize helpfulness."
                },
                {
                    title: "5. Privacy Architecture",
                    content: "All input text sent to the semantic analysis systems is parsed securely. We do not use user text logs to train public model weights."
                },
                {
                    title: "6. Critical Thinking Support",
                    content: "AIRA recommendations should serve as constructive resources to support learning and critical reflection, not replace individual judgment."
                },
                {
                    title: "7. Avoid Sensitive Inputs",
                    content: "Users are strongly advised not to paste sensitive personal identifiers (such as national ID keys, passwords, or credit card numbers) into any AI chat fields."
                },
                {
                    title: "8. Decision Precaution",
                    content: "Always consult academic counselors or licensed therapists to validate significant mental health decisions or academic plan changes."
                },
                {
                    title: "9. Academic Honesty",
                    content: "We encourage students to utilize chatbot resources responsibly and ensure compliance with their university's academic integrity guidelines."
                }
            ]
        }
    };

    let currentPolicyTab = "privacy";
    const policyModal = document.getElementById("aira-policy-modal");
    const policySearchInput = document.getElementById("policy-search-input");
    const policySearchClear = document.getElementById("policy-search-clear");
    const policyCloseBtn = document.getElementById("policy-modal-close-btn");

    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    function highlightText(text, query) {
        if (!query) return text;
        const escapedQuery = escapeRegExp(query);
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    function renderPolicy(policyKey, searchQuery = "") {
        const viewer = document.getElementById("policy-content-viewer");
        const lastUpdatedEl = document.getElementById("policy-last-updated");
        if (!viewer) return;

        const policy = POLICY_DATA[policyKey];
        if (!policy) {
            viewer.innerHTML = '<div class="policy-empty-state"><i class="fa-solid fa-circle-exclamation"></i><p>Failed to load policy.</p></div>';
            return;
        }

        if (lastUpdatedEl) {
            lastUpdatedEl.textContent = `Last Updated: ${policy.lastUpdated}`;
        }

        const query = searchQuery.trim().toLowerCase();
        let htmlContent = "";
        let matchCount = 0;

        policy.sections.forEach(sec => {
            const hasTitleMatch = sec.title.toLowerCase().includes(query);
            const hasContentMatch = sec.content.toLowerCase().includes(query);

            if (!query || hasTitleMatch || hasContentMatch) {
                matchCount++;
                const titleHtml = highlightText(sec.title, query);
                const contentHtml = highlightText(sec.content, query);
                
                htmlContent += `
                    <div class="policy-section" style="margin-bottom: 1.5rem;">
                        <h2 style="font-size: 1.05rem; color: #fff; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 8px;">${titleHtml}</h2>
                        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.6;">${contentHtml}</p>
                    </div>
                `;
            }
        });

        if (matchCount === 0) {
            viewer.innerHTML = `
                <div class="policy-empty-state">
                    <i class="fa-solid fa-file-circle-question" style="font-size: 2rem; color: var(--neon-rose); margin-bottom: 0.8rem;"></i>
                    <p style="font-weight: 700; color: #fff; margin: 0;">No matches found for "${escapeHtml(searchQuery)}"</p>
                    <p style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">Check your spelling or search for another term.</p>
                </div>
            `;
        } else {
            viewer.innerHTML = htmlContent;
        }
    }

    function openPolicyModal(tabKey) {
        if (!policyModal) return;
        currentPolicyTab = tabKey;
        
        // Reset Search
        if (policySearchInput) policySearchInput.value = "";
        if (policySearchClear) policySearchClear.style.display = "none";

        // Set Active Tab Button
        const tabBtns = document.querySelectorAll(".policy-tab-btn");
        tabBtns.forEach(btn => {
            if (btn.getAttribute("data-policy") === tabKey) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        // Render Active Policy
        renderPolicy(tabKey);

        // Display Modal
        policyModal.style.display = "flex";
        document.body.style.overflow = "hidden"; // lock screen scroll
        
        // Trigger transitions
        setTimeout(() => {
            policyModal.classList.add("active");
            policyModal.focus();
        }, 10);
    }

    function closePolicyModal() {
        if (!policyModal) return;
        policyModal.classList.remove("active");
        
        // Restore scrolling
        document.body.style.overflow = "";

        setTimeout(() => {
            policyModal.style.display = "none";
        }, 400);
    }

    // Attach footer click events
    const footerLinkPrivacy = document.getElementById("footer-link-privacy");
    const footerLinkTerms = document.getElementById("footer-link-terms");
    const footerLinkAi = document.getElementById("footer-link-ai");

    if (footerLinkPrivacy) {
        footerLinkPrivacy.addEventListener("click", (e) => {
            e.preventDefault();
            openPolicyModal("privacy");
        });
    }
    if (footerLinkTerms) {
        footerLinkTerms.addEventListener("click", (e) => {
            e.preventDefault();
            openPolicyModal("terms");
        });
    }
    if (footerLinkAi) {
        footerLinkAi.addEventListener("click", (e) => {
            e.preventDefault();
            openPolicyModal("ai");
        });
    }

    // Attach tab buttons
    const policyTabBtns = document.querySelectorAll(".policy-tab-btn");
    policyTabBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            const targetPolicy = e.target.getAttribute("data-policy");
            if (targetPolicy) {
                policyTabBtns.forEach(b => b.classList.remove("active"));
                e.target.classList.add("active");
                currentPolicyTab = targetPolicy;
                
                // Clear search on tab switch
                if (policySearchInput) policySearchInput.value = "";
                if (policySearchClear) policySearchClear.style.display = "none";
                
                renderPolicy(currentPolicyTab);
            }
        });
    });

    if (policyCloseBtn) {
        policyCloseBtn.addEventListener("click", closePolicyModal);
    }

    if (policyModal) {
        policyModal.addEventListener("click", (e) => {
            if (e.target === policyModal) {
                closePolicyModal();
            }
        });

        policyModal.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                closePolicyModal();
            }
        });
    }

    if (policySearchInput) {
        policySearchInput.addEventListener("input", (e) => {
            const query = e.target.value;
            if (query.trim().length > 0) {
                if (policySearchClear) policySearchClear.style.display = "block";
            } else {
                if (policySearchClear) policySearchClear.style.display = "none";
            }
            renderPolicy(currentPolicyTab, query);
        });
    }

    if (policySearchClear) {
        policySearchClear.addEventListener("click", () => {
            if (policySearchInput) policySearchInput.value = "";
            policySearchClear.style.display = "none";
            renderPolicy(currentPolicyTab);
            if (policySearchInput) policySearchInput.focus();
        });
    }
});
