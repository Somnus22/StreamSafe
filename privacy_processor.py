import cv2
import numpy as np
import re
import os
import warnings

# Suppress warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
cv2.setLogLevel(0)
warnings.filterwarnings('ignore')

# Environment setup
os.environ['TORCH_SERIALIZATION_WEIGHTS_ONLY'] = 'False'
os.environ['OMP_NUM_THREADS'] = '4'
cv2.setNumThreads(4)

# Fix PIL compatibility
import PIL.Image
try:
    from pkg_resources import parse_version
    if parse_version(PIL.__version__) >= parse_version("10.0.0"):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
except:
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Check YOLO availability
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class RobustOCRBlockDetector:
    def __init__(self):
        """Initialize EasyOCR for Singapore block number detection"""
        self.reader = None
        self.initialized = False
        try:
            import easyocr
            self.reader = easyocr.Reader(
                ['en'], 
                gpu=False,
                model_storage_directory='./easyocr_models',
                download_enabled=True,
                verbose=False
            )
            self.initialized = True
            print("✅ EasyOCR initialized successfully")
        except Exception as e:
            print(f"❌ EasyOCR initialization failed: {e}")
            self.reader = None
    
    def detect_singapore_block_numbers(self, frame):
        """Ultra-robust Singapore block number detection"""
        if self.reader is None:
            return []
        
        try:
            # Preprocess frame for better OCR
            processed_frame = self._preprocess_frame(frame)
            
            # Run OCR with safe parameters
            results = self.reader.readtext(
                processed_frame, 
                paragraph=False, 
                width_ths=0.7, 
                height_ths=0.7,
                allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            )
            
            if not results:
                return []
            
            block_regions = []
            
            for detection in results:
                try:
                    if not detection or len(detection) < 3:
                        continue
                    
                    bbox, text, confidence = detection[0], detection[1], detection[2]
                    
                    if not self._is_valid_bbox(bbox):
                        continue
                    
                    if confidence > 0.4:
                        cleaned_text = self._clean_text(text)
                        
                        if self._is_singapore_block_number(cleaned_text):
                            coords = self._extract_bbox_safely(bbox, frame.shape)
                            
                            if coords:
                                x1, y1, x2, y2 = coords
                                block_regions.append((x1, y1, x2, y2))
                                
                except Exception:
                    continue
            
            return block_regions[:4]
            
        except Exception:
            return []
    
    def _is_valid_bbox(self, bbox):
        """Validate bbox format and content"""
        try:
            if bbox is None or not isinstance(bbox, (list, tuple, np.ndarray)):
                return False
            if len(bbox) != 4:
                return False
            
            for point in bbox:
                if not isinstance(point, (list, tuple, np.ndarray)) or len(point) != 2:
                    return False
                try:
                    float(point[0])
                    float(point[1])
                except (ValueError, TypeError):
                    return False
            
            return True
        except Exception:
            return False
    
    def _extract_bbox_safely(self, bbox, frame_shape):
        """Extract bounding box coordinates with full error protection"""
        try:
            if not self._is_valid_bbox(bbox):
                return None
            
            x_coords = []
            y_coords = []
            
            for point in bbox:
                try:
                    x, y = float(point[0]), float(point[1])
                    x_coords.append(x)
                    y_coords.append(y)
                except (ValueError, TypeError, IndexError):
                    return None
            
            if len(x_coords) != 4 or len(y_coords) != 4:
                return None
            
            x1, x2 = int(min(x_coords)), int(max(x_coords))
            y1, y2 = int(min(y_coords)), int(max(y_coords))
            
            frame_height, frame_width = frame_shape[:2]
            
            # Clamp to frame bounds
            x1 = max(0, min(x1, frame_width - 1))
            y1 = max(0, min(y1, frame_height - 1))
            x2 = max(x1 + 1, min(x2, frame_width))
            y2 = max(y1 + 1, min(y2, frame_height))
            
            # Add padding
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(frame_width, x2 + padding)
            y2 = min(frame_height, y2 + padding)
            
            return (x1, y1, x2, y2)
            
        except Exception:
            return None
    
    def _preprocess_frame(self, frame):
        """Preprocess frame for better OCR results"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            return thresh
        except Exception:
            return frame
    
    def _clean_text(self, text):
        """Clean OCR text for block number validation"""
        try:
            if not text:
                return ""
            
            cleaned = re.sub(r'[^\w]', '', str(text).strip().upper())
            
            # Handle common OCR misreads
            replacements = {
                'O': '0', 'I': '1', 'S': '5', 'G': '6', 'Z': '2', 'B': '8'
            }
            
            for old, new in replacements.items():
                cleaned = cleaned.replace(old, new)
            
            return cleaned
        except:
            return ""
    
    def _is_singapore_block_number(self, text):
        """Check if text matches Singapore block number pattern"""
        try:
            if not text or len(text) < 1 or len(text) > 4:
                return False
            
            # Pattern 1: Pure digits (1-3 digits)
            if re.match(r'^\d{1,3}$', text):
                return True
            
            # Pattern 2: 1-3 digits + single letter
            if re.match(r'^\d{1,3}[A-Z]$', text):
                return True
            
            return False
        except:
            return False


class StreamSafeProcessor:
    """Main processor class for privacy protection"""
    
    def __init__(self):
        # Initialize YOLO for license plates with your specific model
        self.license_plate_model = None
        if YOLO_AVAILABLE:
            try:
                # Updated to use your specific license plate model
                self.license_plate_model = YOLO('license-plate-finetune-v1l.pt')
                print("✅ License plate model loaded: license-plate-finetune-v1l.pt")
            except Exception as e:
                print(f"❌ License plate model loading failed: {e}")
                print("💡 Make sure 'license-plate-finetune-v1l.pt' is in the project directory")
                self.license_plate_model = None

        # Initialize robust OCR detector
        self.ocr_detector = RobustOCRBlockDetector()
        
        # Caching variables for performance
        self.block_counter = 0
        self.cached_block_regions = []
        self.sign_frame_counter = 0
        self.cached_sign_regions = []
        
        print("✅ StreamSafe processor initialized")
    
    def process_frame(self, frame, detection_settings):
        """Main frame processing function"""
        img = frame.copy()
        
        # Apply privacy protections based on settings
        if detection_settings.get('license_plates', False):
            img = self.blur_license_plates(img)
        
        if detection_settings.get('block_numbers', False):
            img = self.blur_address_numbers(img)
        
        if detection_settings.get('street_signs', False):
            img = self.blur_street_signs(img)
        
        return img
    
    def blur_license_plates(self, frame):
        """Detect and blur vehicle license plates"""
        if self.license_plate_model is None:
            # Demo blur for common license plate locations
            height, width = frame.shape[:2]
            
            demo_regions = [
                (int(width * 0.1), int(height * 0.8), 120, 30),   # Bottom left
                (int(width * 0.7), int(height * 0.75), 120, 30),  # Bottom right
            ]
            
            for x, y, w, h in demo_regions:
                if x + w < width and y + h < height:
                    plate_roi = frame[y:y+h, x:x+w]
                    if plate_roi.size > 0:
                        blurred_plate = cv2.GaussianBlur(plate_roi, (51, 51), 0)
                        frame[y:y+h, x:x+w] = blurred_plate
            return frame
        
        try:
            results = self.license_plate_model.predict(
                source=frame, device='cpu', verbose=False,
                conf=0.65, imgsz=416, half=False, max_det=3, agnostic_nms=True
            )
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                for i, box in enumerate(boxes):
                    if confidences[i] > 0.65:
                        x1, y1, x2, y2 = map(int, box)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2 = min(x2, frame.shape[1])
                        y2 = min(y2, frame.shape[0])
                        if x2 > x1 and y2 > y1:
                            plate_roi = frame[y1:y2, x1:x2]
                            if plate_roi.size > 0:
                                blurred_plate = cv2.GaussianBlur(plate_roi, (51, 51), 0)
                                frame[y1:y2, x1:x2] = blurred_plate
        except Exception:
            pass
        
        return frame

    def blur_address_numbers(self, frame):
        """Ultra-robust OCR block number detection"""
        self.block_counter += 1
        
        # Run OCR every 30 frames for performance
        if self.block_counter % 30 == 0:
            try:
                self.cached_block_regions = self.ocr_detector.detect_singapore_block_numbers(frame)
            except Exception:
                self.cached_block_regions = []
        
        # Apply blur to cached regions
        try:
            for x1, y1, x2, y2 in self.cached_block_regions:
                if x2 > x1 and y2 > y1:
                    block_roi = frame[y1:y2, x1:x2]
                    if block_roi.size > 0:
                        blurred_block = cv2.blur(block_roi, (51, 51))
                        frame[y1:y2, x1:x2] = blurred_block
        except Exception:
            pass
        
        return frame

    def blur_street_signs(self, frame):
        """Singapore street sign detection"""
        self.sign_frame_counter += 1
        
        if self.sign_frame_counter % 15 == 0:
            try:
                self.cached_sign_regions = self._detect_signs_singapore(frame)
            except Exception:
                self.cached_sign_regions = []
        
        try:
            for x1, y1, x2, y2 in self.cached_sign_regions:
                if x2 > x1 and y2 > y1:
                    sign_roi = frame[y1:y2, x1:x2]
                    if sign_roi.size > 0:
                        blurred_sign = cv2.blur(sign_roi, (21, 21))
                        frame[y1:y2, x1:x2] = blurred_sign
        except Exception:
            pass
        
        return frame

    def _detect_signs_singapore(self, frame):
        """Singapore street sign detection using HSV color detection"""
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            detected_regions = []
            
            # Green signs detection
            mask = cv2.inRange(hsv, np.array([40, 60, 60]), np.array([80, 255, 200]))
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 800 < area < 25000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 1.5 < aspect_ratio < 6.5:
                        detected_regions.append((x, y, x+w, y+h))
            
            return detected_regions[:3]  # Limit for performance
            
        except Exception:
            return []
