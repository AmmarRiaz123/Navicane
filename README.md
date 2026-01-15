

# 🦯 Smart Cane for the Visually Impaired

**Raspberry Pi–Based Assistive Navigation System**

## 🌟 Overview

This project is a smart assistive cane designed to help visually impaired users navigate their surroundings safely and independently. Built around a **Raspberry Pi 4**, the system combines **ultrasonic distance sensors**, a **camera for object recognition**, **vibration feedback**, and **bone-conduction audio** to provide real-time awareness of obstacles and objects in front of the user.

The system continuously monitors the environment, detects nearby obstacles and recognized objects, and communicates this information through **gentle vibration patterns** and **spoken feedback**, allowing the user to make informed navigation decisions without blocking environmental sounds.

---

## 🎯 Project Goals

The main purpose of this project is to create an affordable, portable, and real-world usable mobility aid that:

* Detects obstacles in front of the user
* Identifies common objects (people, doors, vehicles, stairs, etc.)
* Provides intuitive feedback through vibration and voice
* Works automatically when powered on
* Is modular, testable, and easy to extend

This is intended to function as a **true mobility assistant**, not just a technical demo.

---

## 🧠 System Architecture

The system is divided into independent modules that all run under one main controller:

### 1. Ultrasonic Distance Sensing

Three **HC-SR04 sensors** are used to measure distances in front, left, and right directions.
They provide fast and accurate detection of nearby obstacles.

Their data is used to:

* Trigger vibration feedback when obstacles are close
* Warn of walls, furniture, or people even if the camera cannot see them

---

### 2. Camera-Based Object Detection

A **Raspberry Pi Camera Module v1.3 (OV5647)** provides live video to an AI object detection model (SSD MobileNet / YOLO).
The model identifies objects such as:

* People
* Doors
* Chairs
* Vehicles
* Stairs
* Bags, tables, etc

Detected objects are filtered to avoid repetition and only important changes are spoken.

---

### 3. Audio Feedback

Using **bone-conduction Bluetooth headphones**, the Pi speaks short, simple phrases such as:

* “Person ahead”
* “Wall in front”
* “Door on the left”

This keeps the ears open to the environment while still delivering clear guidance.

---

### 4. Vibration Feedback

Three vibration motors provide silent, intuitive alerts:

* Stronger vibration = closer obstacle
* Left / right motors indicate direction

This allows the user to react instantly without waiting for speech.

---

### 5. Automatic Startup

The system is designed to run automatically when the Raspberry Pi boots.
Once powered:

* Camera starts
* Sensors activate
* Detection loop begins
* Audio and vibration feedback are live

No keyboard or screen is needed in real use.

---

## 🧩 Modular Design

Each subsystem is implemented as a separate Python module so it can be tested individually:

| Module          | Purpose                      |
| --------------- | ---------------------------- |
| `camera.py`     | Tests and streams the camera |
| `ultrasonic.py` | Reads distance sensors       |
| `vibration.py`  | Controls vibration motors    |
| `audio.py`      | Handles text-to-speech       |
| `detection.py`  | Runs object recognition      |
| `main.py`       | Coordinates all systems      |

This makes debugging and future upgrades much easier.

---

## ⚙️ Hardware Used

* Raspberry Pi 4 Model B (8GB RAM)
* Raspberry Pi Camera Module v1.3 (OV5647)
* 3 × HC-SR04 Ultrasonic Sensors
* 3 × 3–5V Vibration Motors
* Bone-Conduction Bluetooth Headphones
* SanDisk Ultra 32GB MicroSD

---

## 💖 Final Vision

This project is built to be more than a prototype — it is meant to become a **real assistive device** that improves independence, safety, and confidence for visually impaired users.

Every design choice focuses on:

* Simplicity
* Reliability
* Comfort
* Real-world usability

And most of all… dignity and freedom of movement for the person holding the cane.
