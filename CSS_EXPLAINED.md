# CSS_EXPLAINED.md — Glowing Neon & Glassmorphic Style Manual

This document provides a line-by-line stylistic breakdown of **`style.css`**, detailing the variable tokens, typography rules, glassmorphic formulas, fixed overlays, and custom keyframe animations.

---

## Section 1: Color Tokens & Theme Variables (Lines 1 - 38)

```css
:root {
    /* Color Palette - Glowing Neons */
    --bg-base: #060813;
    --bg-card: rgba(13, 20, 38, 0.65);
    --bg-card-hover: rgba(20, 30, 58, 0.85);
    --bg-nav: rgba(6, 8, 19, 0.75);
    
    --neon-cyan: #00f2fe;
    --neon-blue: #4facfe;
    --neon-purple: #7f00ff;
    --neon-pink: #e100ff;
    --neon-emerald: #00ff87;
    --neon-orange: #ff9f43;
    --neon-rose: #ff0055;
    
    --text-main: #f3f4f6;
    --text-muted: #9ca3af;
    --text-cyan: #a5f3fc;
    
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-glow: rgba(0, 242, 254, 0.15);
    
    --glow-cyan: 0 0 15px rgba(0, 242, 254, 0.35);
    --glow-purple: 0 0 15px rgba(127, 0, 255, 0.35);
    --glow-emerald: 0 0 15px rgba(0, 255, 135, 0.35);
    --glow-rose: 0 0 15px rgba(255, 0, 85, 0.35);
    
    --transition-smooth: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    --transition-fast: all 0.2s ease-out;
}
```

### Key Rules Explained:
* **`--bg-base`**: Enforces a solid, low-frequency base color (#060813) to maximize the contrast ratio of glowing elements.
* **`--bg-card`**: A semi-transparent dark shade. Formulates the base for glass panel backdrops.
* **`--glow-*` shadows**: Tailored HSL shadows casting soft vector overlays. Emulates neon reflections.
* **`--transition-smooth`**: Implements a standard custom cubic-bezier formula (`cubic-bezier(0.16, 1, 0.3, 1)`) to ensure decelerated, fluid transition profiles on hovers and modal entries.

---

## Section 2: Glass Panels & Border-Glow Classes (Lines 94 - 106)

```css
.glass-panel {
    background: var(--bg-card);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid var(--border-glass);
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: var(--transition-smooth);
}
.glass-panel:hover {
    border-color: rgba(0, 242, 254, 0.25);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5), var(--border-glow);
}
```

### Key Rules Explained:
* **`backdrop-filter: blur(16px)`**: Emulates premium frosted glass by blending pixel colors behind the panel boundaries.
* **`-webkit-backdrop-filter`**: Hardware-accelerated Safari browser fallback.
* **`border: 1px solid var(--border-glass)`**: Casts a fine, high-frequency border highlight. Creates edge refraction.
* **`transition: var(--transition-smooth)`**: Smooths out hover glows, preventing jarring color flashes.

---

## Section 3: Diagnostic Mood Selectors (Lines 676 - 709)

```css
.mood-selector {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
}
.mood-option {
    flex: 1;
    min-width: 60px;
    text-align: center;
    padding: 0.6rem 0.2rem;
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    cursor: pointer;
    transition: var(--transition-fast);
}
.mood-option:hover, .mood-option.active {
    background: rgba(0, 242, 254, 0.1);
    border-color: var(--neon-cyan);
    transform: translateY(-2px);
}
```

### Key Rules Explained:
* **`flex-wrap: wrap`**: Responsive container wrapping. Adapts cleanly to narrow mobile viewports.
* **`transform: translateY(-2px)`**: Interactive card lift on hover. Emulates organic responsive physics.
* **`.active` border glows**: Uses `--neon-cyan` to frame the user's current selection.

---

## Section 4: Floating Chatbot Overlay Fix (Lines 2372 - 2394)

```css
.chatbot-widget {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 999;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    pointer-events: none;
}

.chatbot-toggle-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 100%);
    box-shadow: 0 5px 25px rgba(0, 242, 254, 0.4), var(--glow-cyan);
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: var(--transition-smooth);
    pointer-events: auto;
}
```

### Key Rules Explained:
* **`pointer-events: none` on `.chatbot-widget`**: The crucial overlay fix. Ensures the large invisible bounding box of the chatbot container doesn't intercept clicks, leaving the underlying elements (like the **Melancholy** card) fully clickable.
* **`pointer-events: auto` on `.chatbot-toggle-btn`**: Selectively restores interactivity to active children. The toggle button remains responsive.

---

## Section 5: Startup Preloader & Biometric Verification Gates (Lines 3009 - 3308)

```css
#aira-preloader {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    background-color: #060813 !important;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.8s;
}

#aira-login-portal {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    background-color: #060813 !important;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.8s;
}
```

### Key Rules Explained:
* **`background-color: #060813 !important`**: Sets a completely opaque backdrop. Prevents visual leaks during start-up or logout.
* **`inset: 0`**: Absolute alignment stretching across the entire width and height of the window viewport.
* **`z-index: 10000 / 9999`**: The highest levels in the stacking context, layering loader masks safely over navigation panels.
* **`@keyframes shake`**:
  Casts a horizontal offset animation to represent incorrect password submissions:
  ```css
  @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-6px); }
      40%, 80% { transform: translateX(6px); }
  }
  ```
