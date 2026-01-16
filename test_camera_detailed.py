"""
Detailed camera diagnostics
Tests camera capture and model loading separately
"""

import cv2
import os
import subprocess
import time
from pathlib import Path

def test_rpicam_capture():
    """Test if rpicam-still can capture"""
    print("=" * 70)
    print("TEST 1: rpicam-still capture")
    print("=" * 70)
    
    test_file = "/tmp/test_capture.jpg"
    
    try:
        print("\nCapturing test image...")
        result = subprocess.run(
            ['rpicam-still', '-o', test_file, '--width', '640', '--height', '480', 
             '--nopreview', '--timeout', '1', '--immediate'],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        if result.returncode == 0:
            if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                print(f"✓ Capture successful: {os.path.getsize(test_file)} bytes")
                
                # Try to load with OpenCV
                img = cv2.imread(test_file)
                if img is not None:
                    print(f"✓ OpenCV can read image: {img.shape}")
                    os.remove(test_file)
                    return True
                else:
                    print("✗ OpenCV cannot read captured image")
                    return False
            else:
                print("✗ File not created or empty")
                return False
        else:
            print(f"✗ rpicam-still failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_model_files():
    """Test if model files exist and are readable"""
    print("\n" + "=" * 70)
    print("TEST 2: Model files")
    print("=" * 70)
    
    user_home = str(Path.home())
    model_path = os.path.join(user_home, 'models/yolov4-tiny.weights')
    cfg_path = os.path.join(user_home, 'models/yolov4-tiny.cfg')
    names_path = os.path.join(user_home, 'models/coco.names')
    
    all_good = True
    
    # Check weights
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Weights file: {size_mb:.1f}MB")
    else:
        print(f"✗ Weights not found: {model_path}")
        all_good = False
    
    # Check config
    if os.path.exists(cfg_path):
        print(f"✓ Config file exists")
    else:
        print(f"✗ Config not found: {cfg_path}")
        all_good = False
    
    # Check names
    if os.path.exists(names_path):
        with open(names_path, 'r') as f:
            classes = [line.strip() for line in f.readlines()]
        print(f"✓ Class names file: {len(classes)} classes")
    else:
        print(f"⚠ coco.names not found (optional)")
    
    return all_good

def test_model_loading():
    """Test if OpenCV can load the model"""
    print("\n" + "=" * 70)
    print("TEST 3: Model loading")
    print("=" * 70)
    
    try:
        user_home = str(Path.home())
        model_path = os.path.join(user_home, 'models/yolov4-tiny.weights')
        cfg_path = os.path.join(user_home, 'models/yolov4-tiny.cfg')
        
        print("\nLoading YOLO model...")
        net = cv2.dnn.readNetFromDarknet(cfg_path, model_path)
        
        if net is None:
            print("✗ Model is None")
            return False
        
        print("✓ Model loaded successfully")
        
        # Get layer names
        layer_names = net.getLayerNames()
        print(f"✓ Model has {len(layer_names)} layers")
        
        # Get output layers
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        print(f"✓ Output layers: {len(output_layers)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False

def test_detection():
    """Test actual object detection"""
    print("\n" + "=" * 70)
    print("TEST 4: Object detection")
    print("=" * 70)
    
    try:
        # Capture image
        test_file = "/tmp/detection_test.jpg"
        print("\n1. Capturing image...")
        
        result = subprocess.run(
            ['rpicam-still', '-o', test_file, '--width', '640', '--height', '480',
             '--nopreview', '--timeout', '1', '--immediate'],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("✗ Capture failed")
            return False
        
        print("✓ Image captured")
        
        # Load image
        print("\n2. Loading image with OpenCV...")
        frame = cv2.imread(test_file)
        
        if frame is None:
            print("✗ Cannot load image")
            return False
        
        print(f"✓ Image loaded: {frame.shape}")
        
        # Load model
        print("\n3. Loading YOLO model...")
        user_home = str(Path.home())
        model_path = os.path.join(user_home, 'models/yolov4-tiny.weights')
        cfg_path = os.path.join(user_home, 'models/yolov4-tiny.cfg')
        
        net = cv2.dnn.readNetFromDarknet(cfg_path, model_path)
        print("✓ Model loaded")
        
        # Prepare blob
        print("\n4. Running detection...")
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Get output layer names
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        
        # Forward pass
        outputs = net.forward(output_layers)
        print("✓ Detection completed")
        
        # Parse results
        print("\n5. Parsing detections...")
        (h, w) = frame.shape[:2]
        detections_found = 0
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = int(scores.argmax())
                confidence = float(scores[class_id])
                
                if confidence > 0.3:  # Low threshold for testing
                    detections_found += 1
                    print(f"   Detection: class_id={class_id}, confidence={confidence:.2f}")
        
        print(f"\n✓ Found {detections_found} detections (threshold=0.3)")
        
        if detections_found == 0:
            print("\n⚠ No objects detected - possible reasons:")
            print("   1. Nothing in camera view")
            print("   2. Confidence threshold too high")
            print("   3. Model needs better lighting")
            print("   4. Camera not pointing at objects")
            print("\nTry pointing camera at a person, chair, or car and run again")
        
        # Cleanup
        os.remove(test_file)
        return True
        
    except Exception as e:
        print(f"✗ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("█" * 70)
    print("CAMERA MODULE DIAGNOSTICS")
    print("█" * 70)
    
    results = {}
    
    # Run tests
    results['rpicam'] = test_rpicam_capture()
    time.sleep(1)
    
    results['model_files'] = test_model_files()
    time.sleep(1)
    
    if results['model_files']:
        results['model_loading'] = test_model_loading()
        time.sleep(1)
        
        if results['model_loading']:
            results['detection'] = test_detection()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test}")
    
    print("\n")
    
    if all(results.values()):
        print("✓ All tests passed! Camera system is working.")
        print("\nIf main.py still doesn't detect objects:")
        print("  1. Check CONFIDENCE_THRESHOLD in config.py (try 0.3)")
        print("  2. Point camera at common objects (person, chair, car)")
        print("  3. Ensure good lighting")
    else:
        print("✗ Some tests failed. Fix the issues above.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
