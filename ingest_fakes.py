import os
import sys
import glob
import torch
from PIL import Image
from qdrant_client.models import Distance, VectorParams, PointStruct
from transformers import CLIPProcessor, CLIPModel

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.services.qdrant_manager import QdrantManager

# --- CONFIGURATION ---
FAKE_DIR = "backend/doc_check/dataset/fakes"
COLLECTION_NAME = "document_risk_engine"
# ---------------------

def main():
    print("--- 1. Initializing Models ---")
    # Load CLIP (The "Eye" that turns images into vectors)
    model_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_id)
    processor = CLIPProcessor.from_pretrained(model_id)
    
    # Initialize Qdrant Manager
    qdrant_manager = QdrantManager()
    client = qdrant_manager.client   
    # --- 2. Create Collection (Reset if exists) ---
    print(f"--- 2. Creating Collection: {COLLECTION_NAME} ---")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=512,  # CLIP output dimension
            distance=Distance.COSINE
        )
    )

    # --- 3. Processing Images ---
    image_paths = glob.glob(os.path.join(FAKE_DIR, "*.jpg"))
    
    if not image_paths:
        print(f"ERROR: No images found in {FAKE_DIR}. Did you run the generator?")
        return

    print(f"Found {len(image_paths)} fake documents. Processing...")

    points = []
    
    for idx, img_path in enumerate(image_paths):
        try:
            filename = os.path.basename(img_path)
            
            # A. Open Image
            image = Image.open(img_path)
            
            # B. Generate Vector (Embedding)
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                output = model.get_image_features(**inputs)
            
            # Extract tensor from output object if needed
            image_features = output.pooler_output if hasattr(output, 'pooler_output') else output
            
            # Ensure it's a tensor and normalize
            if not isinstance(image_features, torch.Tensor):
                image_features = torch.tensor(image_features)
            
            embeddings = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            vector = embeddings[0].tolist()

            # C. Create Qdrant Point
            # We explicitly label this as "fake" in the metadata
            point = PointStruct(
                id=idx + 1,  # Simple Integer ID
                vector=vector,
                payload={
                    "filename": filename,
                    "label": "fake",
                    "type": "generated_fraud_template",
                    "risk_score": 1.0
                }
            )
            points.append(point)
            
            if (idx + 1) % 10 == 0:
                print(f"   Processed {idx + 1} images...")

        except Exception as e:
            print(f"Skipping {img_path} due to error: {e}")

    # --- 4. Upload to Qdrant ---
    if points:
        print(f"--- 4. Uploading {len(points)} vectors to Qdrant ---")
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print("✅ SUCCESS: Database represents a 'Memory of Known Frauds'.")
    else:
        print("❌ No points to upload.")

if __name__ == "__main__":
    main()