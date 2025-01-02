import os
import cv2
from concurrent.futures import ThreadPoolExecutor
from Modules.OCR.ocr import detect_radar_from_image

def process_image(file_path, radar_template_path):
    try:
        # Run OCR detection
        radar_top_left, radar_bottom_right = detect_radar_from_image(file_path, radar_template_path, 0.8, True)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_images_in_folder(folder_path, radar_template_path):
    with ThreadPoolExecutor() as executor:
        futures = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg"):
                file_path = os.path.join(folder_path, filename)
                futures.append(executor.submit(process_image, file_path, radar_template_path))
        for future in futures:
            future.result()  # Wait for all threads to complete

if __name__ == "__main__":
    folder_path = "../../Assets/20"
    test_image_path = "../../Assets/test.jpg"
    radar_template_path = "../../Assets/radar_template.png"
    # detect_radar_with_transparency(test_image_path, radar_template_path)
    process_images_in_folder(folder_path, radar_template_path)