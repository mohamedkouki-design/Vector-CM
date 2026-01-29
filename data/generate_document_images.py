from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
from datetime import datetime

# Create output directory
os.makedirs('sample_documents', exist_ok=True)

def add_noise(image, intensity=10):
    """Add realistic noise/aging to document"""
    pixels = image.load()
    width, height = image.size
    
    for _ in range(intensity * 100):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        noise = random.randint(-20, 20)
        try:
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
        except:
            pass
    
    return image

def create_invoice(client_name, amount, invoice_num, filename):
    """Generate realistic invoice image"""
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to load font
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header bar
    draw.rectangle([0, 0, 800, 80], fill='#2a3562')
    draw.text((40, 25), "FACTURE / INVOICE", fill='white', font=title_font)
    
    # Invoice details
    y = 120
    draw.text((40, y), f"Client: {client_name}", fill='black', font=text_font)
    y += 40
    draw.text((40, y), f"Montant: {amount} TND", fill='black', font=text_font)
    y += 40
    draw.text((40, y), f"Date: {datetime.now().strftime('%d/%m/%Y')}", fill='black', font=text_font)
    y += 40
    draw.text((40, y), f"N° Facture: {invoice_num}", fill='black', font=small_font)
    
    # Add company stamp (circle)
    draw.ellipse([600, 400, 700, 500], outline='#2a3562', width=3)
    draw.text((615, 440), "STAMP", fill='#2a3562', font=small_font)
    
    # Add some wear
    img = add_noise(img, intensity=5)
    
    # Slight blur to simulate scan
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    img.save(filename, quality=85)

def create_receipt(amount, receipt_num, filename):
    """Generate realistic receipt image"""
    img = Image.new('RGB', (400, 600), '#f5f5dc')  # Beige paper
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    
    # Title
    draw.text((120, 40), "REÇU / RECEIPT", fill='black', font=font)
    draw.line([(50, 70), (350, 70)], fill='black', width=2)
    
    # Details
    y = 100
    draw.text((50, y), f"Montant: {amount} TND", fill='black', font=font)
    y += 50
    draw.text((50, y), f"Date: {datetime.now().strftime('%d/%m/%Y')}", fill='black', font=small)
    y += 40
    draw.text((50, y), f"N° Reçu: {receipt_num}", fill='black', font=small)
    
    # Signature line
    draw.line([(50, 400), (350, 400)], fill='black', width=1)
    draw.text((130, 410), "Signature", fill='gray', font=small)
    
    # Add wear
    img = add_noise(img, intensity=8)
    
    img.save(filename, quality=80)

def create_id_card(name, id_number, filename):
    """Generate realistic ID card image"""
    img = Image.new('RGB', (800, 500), 'white')
    draw = ImageDraw.Draw(img)
    
    # Tunisia flag colors - red background with white center
    draw.rectangle([0, 0, 800, 500], fill='#E70013')
    draw.rectangle([200, 80, 600, 420], fill='white')
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Card text
    draw.text((220, 100), "RÉPUBLIQUE TUNISIENNE", fill='black', font=title_font)
    draw.text((250, 150), "CARTE D'IDENTITÉ", fill='black', font=title_font)
    
    y = 220
    draw.text((240, y), name, fill='black', font=text_font)
    y += 50
    draw.text((240, y), f"N°: {id_number}", fill='black', font=text_font)
    y += 50
    draw.text((240, y), f"Date: {datetime.now().strftime('%d/%m/%Y')}", fill='black', font=text_font)
    
    # Photo placeholder
    draw.rectangle([240, 320, 320, 400], fill='#cccccc')
    draw.text((255, 350), "PHOTO", fill='gray')
    
    # Add slight wear
    img = add_noise(img, intensity=3)
    
    img.save(filename, quality=90)

# Generate documents
print("🖼️  Generating sample document images...")
print("=" * 60)

# 30 invoices
print("\n📄 Generating invoices...")
for i in range(30):
    create_invoice(
        client_name=f"Client {i+1}",
        amount=random.randint(500, 5000),
        invoice_num=f"INV-{2024000 + i}",
        filename=f'sample_documents/invoice_{i:03d}.jpg'
    )
    if (i + 1) % 10 == 0:
        print(f"  Generated {i + 1}/30 invoices...")

# 30 receipts
print("\n🧾 Generating receipts...")
for i in range(30):
    create_receipt(
        amount=random.randint(100, 2000),
        receipt_num=f"REC-{2024000 + i}",
        filename=f'sample_documents/receipt_{i:03d}.jpg'
    )
    if (i + 1) % 10 == 0:
        print(f"  Generated {i + 1}/30 receipts...")

# 30 ID cards
print("\n🪪  Generating ID cards...")
for i in range(30):
    create_id_card(
        name=f"Person {i+1}",
        id_number=f"{random.randint(10000000, 99999999)}",
        filename=f'sample_documents/id_card_{i:03d}.jpg'
    )
    if (i + 1) % 10 == 0:
        print(f"  Generated {i + 1}/30 ID cards...")

print("\n" + "=" * 60)
print("✅ Generated 90 sample documents!")
print("=" * 60)
print(f"\nLocation: data/sample_documents/")
print("  - 30 invoices")
print("  - 30 receipts")
print("  - 30 ID cards")