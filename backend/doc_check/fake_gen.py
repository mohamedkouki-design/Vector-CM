import os
import random
from datetime import datetime
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
from pdf2image import convert_from_path

# --- CONFIGURATION ---
INPUT_FILES = ["Releve_Bancaire.pdf", "Releve_Bancaire1.pdf"]
OUTPUT_DIR = "dataset/fakes"
FONT_PATH = "arial.ttf"  # Ensure this file exists, or use absolute path
# If you don't have Arial, try "DejaVuSans.ttf" on Linux
# ---------------------

# Initialize Faker
fake = Faker('fr_FR')

# --- CONSTANTS FROM C CODE (Do not change) ---
# These are the dimensions defined in your HPDF setup
PDF_W = 595
PDF_H = 841
MARGIN = 40

# Coordinate Mapping based on your C Code logic:
# y starts at 841 - 40 = 801
# "HISTORIQUE" (Header) is at y-24 = 777
# Text loop follows:
C_LAYOUT = {
    'titulaire': {
        'pdf_x': MARGIN, 
        'pdf_y': 750,  # (777 - 50)
        'c_size': 10,
        'label': "Titulaire : "
    },
    'date': {
        'pdf_x': MARGIN, 
        'pdf_y': 732,  # (727 - 15)
        'c_size': 10,
        'label': "Date Edition : "
    },
    'solde': {
        'pdf_x': MARGIN, 
        'pdf_y': 710,  # (712 - 30)
        'c_size': 12,
        'label': "SOLDE ACTUEL : "
    }
}

def get_calibrated_font(c_size, scale, font_path):
    """
    Calculates the exact pixel font size based on the image scale.
    No arbitrary multipliers.
    """
    # PDF Point size -> Pixel size
    pixel_size = int(c_size * scale)
    
    try:
        return ImageFont.truetype(font_path, pixel_size)
    except IOError:
        print(f"Warning: Could not load {font_path}. Using default (size will be wrong).")
        return ImageFont.load_default()

def pdf_point_to_pixel(pdf_x, pdf_y, scale_x, scale_y):
    """
    Converts C code (Bottom-Left origin) to PIL (Top-Left origin).
    """
    # X is simple scaling
    img_x = int(pdf_x * scale_x)
    
    # Y is inverted (Height - Y) then scaled
    # We subtract a small amount because PDF coords are often 'Baseline' 
    # while PIL coords are 'Top-Left'.
    img_y = int((PDF_H - pdf_y) * scale_y)
    
    return img_x, img_y

def create_fakes(count=50):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Calculate relative path to poppler in the same directory
    poppler_path = os.path.join(os.path.dirname(__file__), "poppler-25.12.0", "Library", "bin")

    print(f"--- Starting Generation of {count} documents ---")

    for i in range(count):
        # 1. Pick a random template
        template_file = random.choice(INPUT_FILES)
        
        # 2. Convert PDF to Image
        # We assume the PDF is in the same folder. If not, add path logic.
        try:
            images = convert_from_path(template_file, poppler_path=poppler_path)
            img = images[0] # Page 1
        except Exception as e:
            print(f"Error reading {template_file}: {e}")
            continue

        draw = ImageDraw.Draw(img)
        w, h = img.size

        # Calculate Scale Factors (Image Pixels / PDF Points)
        # Example: If image is 1654px wide, scale is 2.78
        scale_x = w / PDF_W
        scale_y = h / PDF_H
        scale_avg = (scale_x + scale_y) / 2

        # 3. Generate Fake Data
        fake_name = f"{fake.last_name().upper()} {fake.first_name()}"
        fake_id = random.randint(1, 150)
        fake_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        fake_balance = f"{random.uniform(50.0, 50000.0):.2f}"

        # Data map
        data_map = {
            'titulaire': f"{fake_name} (ID: {fake_id})",
            'date': fake_date,
            'solde': f"{fake_balance} TND"
        }

        # 4. Overwrite Fields
        for field_key, config in C_LAYOUT.items():
            # Get coords
            x, y = pdf_point_to_pixel(config['pdf_x'], config['pdf_y'], scale_x, scale_y)
            
            # Get Font
            font = get_calibrated_font(config['c_size'], scale_avg, FONT_PATH)
            
            # Prepare Text
            full_text = config['label'] + data_map[field_key]
            
            # --- WHITE OUT ---
            # Calculate text size to know how much to erase
            # bbox returns (left, top, right, bottom) relative to (0,0)
            bbox = font.getbbox(full_text) 
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            # Draw white rectangle. 
            # Adjustment: y in PDF is baseline, so in PIL (Top-Left), 
            # the text starts roughly at y - text_h. 
            # We draw a box slightly larger to be safe.
            rect_x = x
            rect_y = y - text_h - int(5 * scale_avg) # Move up to cover ascenders
            rect_w = text_w + int(50 * scale_avg)    # Extra width to cover long old names
            rect_h = text_h + int(10 * scale_avg)
            
            draw.rectangle(
                [rect_x, rect_y, rect_x + rect_w, rect_y + rect_h], 
                fill="white", 
                outline=None
            )

            # --- WRITE NEW TEXT ---
            # We draw at the same calculated position, shifting Y up by font height
            # to mimic the PDF baseline behavior
            draw.text((x, rect_y), full_text, font=font, fill="black")

        # 5. Save
        output_filename = f"fake_doc_{i}_{random.randint(1000,9999)}.jpg"
        save_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(save_path, "JPEG", quality=95)
        
        if i % 10 == 0:
            print(f"Generated {i}/{count}...")

    print(f"Done! Images saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    create_fakes(1)