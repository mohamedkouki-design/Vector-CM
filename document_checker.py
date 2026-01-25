import numpy as np
from PIL import Image
import io

class SimpleDocumentChecker:
    """Simplified document authenticity checker"""
    
    def __init__(self):
        # Store hashes of known fake documents
        self.known_fakes = set()
    
    def image_to_hash(self, image_file):
        """Simple perceptual hash of image"""
        img = Image.open(image_file).convert('L')  # Grayscale
        img = img.resize((8, 8), Image.Resampling.LANCZOS)
        pixels = np.array(img)
        avg = pixels.mean()
        hash_value = ''.join(['1' if p > avg else '0' for p in pixels.flatten()])
        return hash_value
    
    def hamming_distance(self, hash1, hash2):
        """Calculate similarity between hashes"""
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    
    def check_document(self, image_file, threshold=10):
        """Check if document is suspicious"""
        doc_hash = self.image_to_hash(image_file)
        
        # Check against known fakes
        for fake_hash in self.known_fakes:
            distance = self.hamming_distance(doc_hash, fake_hash)
            if distance < threshold:
                return True, f"Similar to known fake (distance: {distance})"
        
        return False, "Document appears authentic"
    
    def add_fake(self, image_file):
        """Register a document as fake"""
        fake_hash = self.image_to_hash(image_file)
        self.known_fakes.add(fake_hash)
