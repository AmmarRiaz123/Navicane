# Haptic Feedback System

## Overview

The vibration motor provides dynamic haptic feedback that increases in intensity and frequency as obstacles get closer. This creates an intuitive, natural warning system.

## Feedback Zones

### 🔴 CRITICAL (0-30cm)
**Distance:** 0-30cm  
**Intensity:** 100% constant  
**Pattern:** Continuous vibration  
**Urgency:** Maximum - immediate action required  
**Use case:** Object very close, stop immediately

---

### 🟠 DANGER (30-60cm)
**Distance:** 30-60cm  
**Intensity:** 70-100% (decreases with distance)  
**Pattern:** Fast pulses at 5Hz (5 times per second)  
**Urgency:** High - slow down and prepare to stop  
**Use case:** Object approaching, heightened awareness needed

---

### 🟡 WARNING (60-100cm)
**Distance:** 60-100cm  
**Intensity:** 40-70% (decreases with distance)  
**Pattern:** Medium pulses at 2Hz (2 times per second)  
**Urgency:** Medium - obstacle nearby  
**Use case:** Be cautious, plan path adjustment

---

### 🟢 CAUTION (100-150cm)
**Distance:** 100-150cm  
**Intensity:** 20-40% (decreases with distance)  
**Pattern:** Slow pulses at 1Hz (once per second)  
**Urgency:** Low - early warning  
**Use case:** Object detected at distance, stay alert

---

### ⚪ CLEAR (150cm+)
**Distance:** 150cm and beyond  
**Intensity:** 0% (off)  
**Pattern:** No vibration  
**Urgency:** None - path is clear  
**Use case:** Safe to proceed

## Intensity Calculation

The system uses **linear interpolation** within each zone:

