---
name: VoiceBridge Audio Experience
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#bdc2ff'
  on-tertiary: '#131e8c'
  tertiary-container: '#7c87f3'
  on-tertiary-container: '#081486'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e0e0ff'
  tertiary-fixed-dim: '#bdc2ff'
  on-tertiary-fixed: '#000767'
  on-tertiary-fixed-variant: '#2f3aa3'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  margin: 1rem
  margin-tablet: 2rem
  margin-desktop: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
The design system embodies a calm, precise, and unobtrusive audio-first aesthetic engineered for real-time AI translation. It addresses global communicators, bilingual teams, and travelers who require immediate clarity without cognitive friction.

Visual principles:
- **Atmospheric Clarity:** Deep nocturnal backgrounds eliminate visual glare, focusing all perceptual bandwidth on spoken exchanges and live transcripts.
- **Luminescent Telemetry:** Vivid indigo and cyan signals act as functional bioluminescence, indicating capture state, voice detection, and synthetic speech playback without overwhelming the viewport.
- **Tactile Ergonomics:** Over-indexed tap targets, balanced pill geometries, and fluid interactive rings simulate refined physical acoustics hardware.

## Colors
The palette balances low-light optical comfort with focused luminescence:

- **Canvas & Surfaces:** Root viewport renders in deep charcoal-slate `#0B0F19`. Resting container cards use `#131B2E`, while elevated flyouts, modals, and active sheets rise into `#1E293B`. Perimeter boundaries and micro-separators employ `#2E3A52` at low opacity to retain soft definition without harsh dividing lines.
- **Accents & State Telemetry:** `#6366F1` (Indigo Glow) represents system intelligence, active streaming channels, and standard interactive triggers. `#06B6D4` (Cyan Resonance) represents user input, live audio capture, and microphone status. `#818CF8` serves as an interactive highlight for focused states and text selections.
- **Functional Contrast:** Primary typographic layers default to high-contrast crisp white (`#F8FAFC`), secondary metadata rests at `#94A3B8`, and muted structural details drop to `#475569`. Critical errors use `#F43F5E` paired with soft red back-glows.

## Typography
Typography is executed purely in Inter to maintain technical neutrality and immediate legibility across dense script transliterations and dynamic spoken captions.

- **Dynamic Transcription Scaling:** Real-time spoken text defaults to `body-lg` (18px) for maximum legibility at arm's length, transitioning to `headline-md` when the app is placed in hands-free presentation mode.
- **Optical Adjustments:** Negative tracking is applied strictly across titles and displays (`-0.01em` to `-0.03em`) to anchor floating voice panels. Labels and time-stamped telemetry feature slightly relaxed tracking (`0.01em` to `0.02em`) to avoid character collapse on dark canvases.

## Layout & Spacing
The layout model employs a flexible, fluid vertical stack optimized for handheld usage, transitioning into a symmetrical split-pane layout on larger viewports:

- **Breakpoints:**
  - `Mobile` (< 768px): Single-column conversational stream with a sticky bottom interactive audio console. Content margins rest at `1rem`.
  - `Tablet` (768px - 1024px): 8-column layout with pinned conversation control rail and `2rem` outer padding.
  - `Desktop` (> 1024px): 12-column dual-stream layout allowing both parties' transcribed languages to sit side-by-side with synchronized audio playback markers.
- **Rhythm & Touch Areas:** All key interaction zones enforce an expanded minimum clearance of 56px to ensure mis-taps do not occur during live spoken exchanges.

## Elevation & Depth
Depth is constructed through luminous layering and tonal stacking rather than conventional harsh drop shadows:

- **Surface Tiers:**
  - *Base:* `#0B0F19` void canvas.
  - *Resting Cards:* `#131B2E` with a 1px border of `#2E3A52` at 60% alpha.
  - *Overlays & Floating Sheets:* `#1E293B` featuring backdrop blur (`blur(16px)`) with subtle inward specular edge lighting (`inset 0 1px 0 rgba(255, 255, 255, 0.08)`).
- **Luminescent Halo Rings:** Active translation controls project a soft ambient radial glow:
  - Cyan State (Listening): `0 0 32px -4px rgba(6, 182, 212, 0.35)`
  - Indigo State (Processing/Speaking): `0 0 32px -4px rgba(99, 102, 241, 0.35)`
- Outlines remain low-contrast (`#2E3A52`), preserving clean separation without visually severing the interface.

## Shapes
A pill-shaped curvature hierarchy (`roundedness: 3`) underpins the physical feel of the system:

- **Primary Interactive Targets:** Audio action buttons, language toggle switchers, and dynamic floating status bars use full pill bounds (`9999px` radius) to convey softness and ergonomic comfort.
- **Containers & Surfaces:** Information panels, conversational bubbles, and audio telemetry viewports use `rounded-lg` (2rem) and `rounded-xl` (3rem) geometries, removing sharp structural apexes to maintain an organic, fluid tool aesthetic.

## Components

- **Voice Control Ring (Hero Component):** Circular pill button (80px minimum on mobile) suspended above the canvas. Features an outer concentric pulse ring driven by input decibels. Idle state rests in `#1E293B` with an Indigo highlight; active state transitions to glowing cyan with dynamic CSS waveform amplitude nodes.
- **Buttons:**
  - *Primary:* Fully rounded pill, `#6366F1` background, `#FFFFFF` text, subtle upward inner shadow, accompanied by an interactive focus ring.
  - *Secondary / Ghost:* Transparent fill, `#2E3A52` outline, `#F8FAFC` label, transitioning to a low-alpha tint of `#818CF8` on press.
- **Language Switcher Chips:** Dual-state pill capsules housing ISO country/language identifiers. Displays distinct active speaker highlighting with a sliding background glow pill.
- **Conversational Cards:** Asymmetric pill-rounded panels. Outbound speech aligns right in `#1E293B` with Cyan indicator dots; inbound translations align left in `#131B2E` with Indigo indicator dots. Both include inline real-time audio playback waveform scrubbers.
- **Waveform Indicators:** Audio scrubbers and visualizers render as rounded vertical bars (3px wide, 4px gaps) that animate dynamically via normalized amplitude vectors.
- **Inputs & Dropdowns:** Inset pill fields styled with `#131B2E` backgrounds, `#2E3A52` borders, and high-contrast `#F8FAFC` placeholder and entered text.