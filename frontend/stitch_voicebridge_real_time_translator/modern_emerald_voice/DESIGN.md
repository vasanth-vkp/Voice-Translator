---
name: Modern Emerald Voice
colors:
  surface: '#0c1512'
  surface-dim: '#0c1512'
  surface-bright: '#313b37'
  surface-container-lowest: '#07100d'
  surface-container-low: '#141d1a'
  surface-container: '#18221e'
  surface-container-high: '#222c28'
  surface-container-highest: '#2d3733'
  on-surface: '#dae5df'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dae5df'
  inverse-on-surface: '#29322f'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#45dfa4'
  on-secondary: '#003825'
  secondary-container: '#00bd85'
  on-secondary-container: '#00452e'
  tertiary: '#68dba9'
  on-tertiary: '#003825'
  tertiary-container: '#3eb686'
  on-tertiary-container: '#00422c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#0c1512'
  on-background: '#dae5df'
  surface-variant: '#2d3733'
  mint-highlight: '#6ee7b7'
  forest-depth: '#030806'
  forest-surface: '#0a1713'
  forest-elevated: '#12251f'
  forest-border: '#1b382e'
  crisp-white: '#f9fcfb'
  mint-text: '#a7f3d0'
  muted-emerald: '#6b9385'
  danger-red: '#f87171'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-md:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.03em
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
The design system pairs an organic, high-energy acoustic presence with pristine computational precision. Built for real-time speech processing, continuous conversation flows, and spatial audio telemetry, the interface evokes the vitality of living systems while sustaining intense focus.

Visual principles:
- **Bio-Digital Energy:** Vibrancy is anchored by vivid emerald and mint emissions emerging from deep, velvety forest foundations. Telemetry and capture signals feel alive and natural rather than sterile.
- **Nocturnal Clarity:** Deep, light-absorbing forest backdrops eliminate visual noise and optical fatigue, maximizing legibility in field environments, conference rooms, and dimly lit settings.
- **Ergonomic Organicism:** Generous curvature, touch-first pill form factors, and fluid tactile responses emulate high-end acoustic hardware.

## Colors
The palette abandons synthetic blues in favor of an energetic, modern emerald ecosystem that prioritizes WCAG AAA compliance across all critical interactive surfaces:

- **Deep Forest Foundations:** The viewport canvas utilizes `#060F0C` (forest-depth), creating a light-sink foundation. Intermediate container surfaces use `#0A1713`, stepping up to `#12251F` for cards, flyouts, and elevated modal panels. Structural borders and dividers use `#1B382E` to maintain gentle, organic separation.
- **Emerald & Mint Energy:** Interactive actions, primary signals, and active voice telemetries utilize `#10B981` (emerald-500) and `#34D399` (mint). Highlights, focus rings, and real-time capture bursts surface in `#6EE7B7`. Deep anchors and pressed states draw on `#059669`.
- **Text & Contrast Ratios (WCAG AAA):**
  - High-emphasis labels and transcription typography use `#F9FCFB` (crisp white), achieving an ultra-crisp 17.8:1 contrast ratio against base forest surfaces.
  - Secondary details and speech metadata utilize `#A7F3D0` (light mint, 11.2:1 against surface) or `#6B9385` (muted emerald, maintaining 4.8:1+ for non-body elements).
  - Reverse interaction states leverage deep forest `#030806` on luminous mint capsules.

## Typography
The typographic architecture blends three harmonized typefaces to balance character, operational legibility, and technical precision:

- **Display & Headlines (Plus Jakarta Sans):** Brings soft, geometric warmth to major viewport anchors, system headers, and status titles. Slightly tighter negative tracking (`-0.01em` to `-0.03em`) creates a polished display cadence.
- **Reading & Transcripts (Inter):** Serves as the high-legibility engine for continuous speech bubbles, multi-language transcriptions, and conversational playback. Its neutral metrics guarantee seamless character rendering across varied scripts.
- **Controls & Data Telemetry (Outfit):** Delivers clean, contemporary geometric punch to button labels, time-stamps, bitrates, and language tags, benefiting from slightly expanded letter spacing (`0.02em` to `0.03em`).

## Layout & Spacing
The layout centers around ergonomic handheld audio interactions, scaling into multi-pane translation streams on wider surfaces:

- **Breakpoints:**
  - `Mobile` (< 768px): Single-column conversational feed with persistent bottom-pinned floating control console. Page margin sits at `1rem`.
  - `Tablet` (768px - 1024px): 8-column layout featuring an anchored interaction rail and expanded margin of `2rem`.
  - `Desktop` (> 1024px): 12-column dual-lane conversation layout, rendering simultaneous source and translated audio streams side-by-side with centralized waveform controls. Margin expands to `3rem`.
- **Vertical Rhythm:** Interactive audio elements and quick-action chips observe a strict 56px minimum hit-zone, preserving rapid touch accuracy during active speech.

## Elevation & Depth
Elevation eschews heavy shadows in favor of luminous tonal stratification, emerald glow diffusion, and fine structural rim lighting:

- **Stacking Layers:**
  - *Base Surface:* Deep void forest `#060F0C`.
  - *Resting Surfaces:* `#0A1713` with a 1px border of `#1B382E` at 70% opacity.
  - *Floating Sheets & Modals:* `#12251F` with a 16px background blur and an inner ambient rim light (`inset 0 1px 0 rgba(110, 231, 183, 0.12)`).
- **Acoustic Halo Glows:** Active voice interactions emit energetic radial glows:
  - Active Listening State: `0 0 36px -4px rgba(16, 185, 129, 0.45)`.
  - Peak Input / Speech Synthesizing: `0 0 44px -2px rgba(110, 231, 183, 0.5)`.
  - Resting Focus State: `0 0 0 3px rgba(52, 211, 153, 0.35)`.

## Shapes
A roundedness hierarchy of `3` (pill-shaped) provides smooth, friendly tactile ergonomics:

- **Interactive Nodes:** Audio action buttons, language pills, recording toggles, and state badges employ full pill geometries (`9999px` radius).
- **Structural Containers:** Conversation message bubbles, transcription cards, and acoustic visualization boxes use `rounded-lg` (2rem) and `rounded-xl` (3rem), avoiding acute corners to maintain an organic, fluid contour across every viewport.

## Components

- **Voice Control Capsule (Hero Component):** Circular floating pill button (80px minimum on mobile). Idle state rests in `#12251F` with a crisp `#34D399` outline. Active capture pulses with an outer concentric radial glow in `#10B981`, featuring dynamic SVG waveform amplitude bars that dance to input decibels.
- **Buttons:**
  - *Primary Action:* Full pill radius, solid `#10B981` fill, crisp `#030806` text for maximum AAA contrast, subtle upward specular highlight, shifting to `#34D399` on hover.
  - *Secondary / Outlined:* Transparent fill, 1.5px border in `#1B382E`, `#F9FCFB` text, shifting to a 10% `#10B981` tint on press.
  - *Ghost:* Pill radius, clear fill, `#A7F3D0` text, transitioning to `#12251F` background on interaction.
- **Language Switcher Chips:** Capsule-shaped dual-state toggles. Active language segment is filled with `#12251F`, bordered in `#34D399`, displaying crisp white text with a small emerald status indicator dot.
- **Conversational Bubbles:**
  - *Inbound Translation:* Deep container `#0A1713`, left-aligned, bordered in `#1B382E`, with `#F9FCFB` transcription text and `#34D399` playback metadata.
  - *Outbound Voice:* Elevated container `#12251F`, right-aligned, bordered in `#10B981` at 40% alpha, with crisp white typography and embedded waveform scrubber.
- **Audio Waveform Scrubber:** Visualizer bars measuring 3px width with 3px gaps, rendered in `#1B382E` (unplayed) and animated `#6EE7B7` (played/active).
- **Input Fields & Selectors:** Inset pill containers using `#0A1713` fill, `#1B382E` borders, `#F9FCFB` input text, and `#6B9385` placeholders, illuminating with an emerald rim when focused.
- **Selection Controls (Checkboxes & Radios):** Pill-rounded rings in `#1B382E`; active state fills with `#10B981` featuring a crisp `#030806` checkmark.