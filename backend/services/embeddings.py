import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Singleton model
_encoder = None

def get_encoder():
    """Get or create encoder (singleton)"""
    global _encoder
    if _encoder is None:
        logger.info("Loading sentence transformer model...")
        _encoder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    return _encoder

def create_embedding(client_data):
    """
    Create 384-dim embedding from client data
    
    Args:
        client_data: dict or Series with keys:
            - archetype
            - debt_ratio
            - years_active
            - income_stability
            - payment_regularity
            - monthly_income (optional)
    
    Returns:
        numpy array of shape (384,) - L2 normalized
    """
    encoder = get_encoder()
    
    # Extract features with defaults
    archetype = str(client_data.get('archetype', 'unknown'))
    debt_ratio = float(client_data.get('debt_ratio', 0.5))
    years_active = float(client_data.get('years_active', 5))
    income_stability = float(client_data.get('income_stability', 0.7))
    payment_regularity = float(client_data.get('payment_regularity', 0.8))
    monthly_income = float(client_data.get('monthly_income', 1500))
    
    # Part 1: Text embedding (128 dims)
    text = f"{archetype} business"
    text_emb = encoder.encode(text)
    text_features = text_emb[:128]
    
    # Part 2: Financial features (128 dims)
    financial = np.array([
        debt_ratio,
        years_active / 20,  # Normalize to [0,1]
        income_stability,
        monthly_income / 5000,  # Normalize
        payment_regularity
    ])
    financial_padded = np.pad(financial, (0, 128 - len(financial)))
    
    # Part 3: Behavioral features (128 dims)
    behavioral = np.zeros(128)
    behavioral[0] = calculate_risk_score(client_data)
    behavioral[1] = income_stability * payment_regularity  # Combined metric
    
    # Combine all parts
    full_vector = np.concatenate([
        text_features,
        financial_padded,
        behavioral
    ])
    
    # CRITICAL: L2 normalize
    norm = np.linalg.norm(full_vector)
    if norm > 0:
        normalized = full_vector / norm
    else:
        normalized = full_vector
    
    logger.debug(f"Created embedding with norm: {np.linalg.norm(normalized):.4f}")
    
    return normalized

def calculate_risk_score(client_data):
    """Calculate simple risk score [0,1]"""
    debt_ratio = float(client_data.get('debt_ratio', 0.5))
    income_stability = float(client_data.get('income_stability', 0.7))
    payment_regularity = float(client_data.get('payment_regularity', 0.8))
    
    risk = (
        debt_ratio * 0.4 +
        (1 - income_stability) * 0.3 +
        (1 - payment_regularity) * 0.3
    )
    
    return min(1.0, max(0.0, risk))

# Backward compatibility
def create_client_embedding(client_data):
    """Alias for create_embedding"""
    return create_embedding(client_data)
# ===== MULTIMODAL: CLIP Image Embeddings =====

try:
    from transformers import CLIPProcessor, CLIPModel
    from PIL import Image
    import torch
    import cv2
    import numpy as np
    
    _clip_model = None
    _clip_processor = None
    
    def get_clip_model():
        """Get or create CLIP model (singleton)"""
        global _clip_model, _clip_processor
        if _clip_model is None:
            logger.info("Loading CLIP model (openai/clip-vit-base-patch32)...")
            _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            logger.info("✅ CLIP model loaded successfully")
        return _clip_model, _clip_processor
    
    def preprocess_document_image(image_path):
        """
        Preprocess document image for better CLIP embedding
        
        - Convert to grayscale if needed
        - Enhance contrast
        - Resize to optimal dimensions
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to RGB (CLIP expects RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Enhance contrast
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(enhanced)
        
        return pil_img
    
    def create_image_embedding(image_path):
        """
        Create CLIP embedding from document image
        
        Args:
            image_path: Path to document image file
        
        Returns:
            numpy array of shape (512,) - CLIP image embedding (L2 normalized)
        """
        model, processor = get_clip_model()
        
        # Preprocess and load image
        image = preprocess_document_image(image_path)
        
        # Process image for CLIP
        inputs = processor(images=image, return_tensors="pt")
        
        # Get embedding (no gradient needed)
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        # Convert to numpy
        embedding = image_features.squeeze().cpu().numpy()
        
        # L2 normalize
        normalized = embedding / np.linalg.norm(embedding)
        
        logger.debug(f"Created image embedding: shape={normalized.shape}, norm={np.linalg.norm(normalized):.4f}")
        
        return normalized
    
    def create_multimodal_embedding(client_data, image_paths=None):
        """
        Create combined embedding from client data + document images
        
        Args:
            client_data: Dict with client profile
            image_paths: List of document image paths (optional)
        
        Returns:
            numpy array - Combined multimodal embedding
            - If no images: [client_embedding (384)] + [zeros (512)] = 896 dims
            - With images: [client_embedding (384)] + [avg_image_embedding (512)] = 896 dims
        """
        # Base embedding from client data (384 dims)
        base_embedding = create_embedding(client_data)
        
        if not image_paths or len(image_paths) == 0:
            # No images - pad with zeros
            padding = np.zeros(512)
            combined = np.concatenate([base_embedding, padding])
            normalized = combined / np.linalg.norm(combined)
            logger.info(f"Created embedding (no images): {normalized.shape}")
            return normalized
        
        # Process image embeddings (512 dims each)
        image_embeddings = []
        
        for img_path in image_paths[:5]:  # Max 5 images to avoid over-weighting
            try:
                img_emb = create_image_embedding(img_path)
                image_embeddings.append(img_emb)
                logger.info(f"Processed image: {img_path}")
            except Exception as e:
                logger.warning(f"Failed to process image {img_path}: {e}")
                continue
        
        # Average image embeddings if multiple
        if image_embeddings:
            avg_image_embedding = np.mean(image_embeddings, axis=0)
            logger.info(f"Averaged {len(image_embeddings)} image embeddings")
        else:
            # All images failed - use zeros
            avg_image_embedding = np.zeros(512)
            logger.warning("No images processed successfully - using zero padding")
        
        # Combine: [client_data: 384] + [images: 512] = 896 dims
        combined = np.concatenate([base_embedding, avg_image_embedding])
        
        # L2 normalize the combined embedding
        normalized = combined / np.linalg.norm(combined)
        
        logger.info(f"Created multimodal embedding: shape={normalized.shape}, norm={np.linalg.norm(normalized):.4f}")
        
        return normalized
    
    # Mark multimodal as available
    MULTIMODAL_AVAILABLE = True
    logger.info("✅ Multimodal capabilities enabled (CLIP)")

except ImportError as e:
    logger.warning(f"⚠️  Multimodal features disabled: {e}")
    logger.warning("   Install: pip install transformers torch pillow opencv-python-headless")
    
    MULTIMODAL_AVAILABLE = False
    
    def create_image_embedding(image_path):
        raise NotImplementedError("CLIP not installed. Multimodal features unavailable.")
    
    def create_multimodal_embedding(client_data, image_paths=None):
        # Fallback to standard embedding
        logger.warning("Multimodal requested but not available - using standard embedding")
        base = create_embedding(client_data)
        padding = np.zeros(512)
        combined = np.concatenate([base, padding])
        return combined / np.linalg.norm(combined)