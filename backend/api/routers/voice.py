"""
Voice processing endpoints for speech-to-structured-data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class VoiceExtractionRequest(BaseModel):
    transcript: str
    language: str = 'ar-TN'


class VoiceExtractionResponse(BaseModel):
    archetype: str
    years_active: int
    monthly_income: int
    confidence: float
    raw_transcript: str
    extracted_entities: dict


@router.post("/voice/extract", response_model=VoiceExtractionResponse)
async def extract_from_speech(request: VoiceExtractionRequest):
    """
    Extract structured credit application data from voice transcript
    
    Uses NLP and pattern matching to identify:
    - Business type
    - Years in operation
    - Income estimates
    - Other relevant financial information
    """
    
    try:
        transcript = request.transcript.lower()
        
        # Extract business type
        archetype = extract_business_type(transcript, request.language)
        
        # Extract years active
        years = extract_years_active(transcript)
        
        # Extract income
        income = extract_income(transcript)
        
        # Calculate confidence based on how many fields we extracted
        confidence = calculate_confidence(transcript, archetype, years, income)
        
        return VoiceExtractionResponse(
            archetype=archetype,
            years_active=years,
            monthly_income=income,
            confidence=confidence,
            raw_transcript=request.transcript,
            extracted_entities={
                'business_keywords': extract_keywords(transcript, archetype),
                'numbers_found': re.findall(r'\d+', transcript),
                'language': request.language
            }
        )
    
    except Exception as e:
        logger.error(f"Voice extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def extract_business_type(text: str, language: str) -> str:
    """Extract business type from transcript"""
    
    # Keywords for different business types (multilingual)
    keywords = {
        'market_vendor': [
            'market', 'vendor', 'sell vegetables', 'sell fruits',
            'سوق', 'بائع', 'خضار', 'فواكه',  # Arabic
            'marché', 'vendeur', 'légumes', 'fruits'  # French
        ],
        'craftsman': [
            'artisan', 'craftsman', 'handmade', 'handicraft',
            'حرفي', 'صانع', 'يدوي',  # Arabic
            'artisan', 'fabrication', 'manuel'  # French
        ],
        'gig_worker': [
            'taxi', 'driver', 'delivery', 'uber', 'louage',
            'سائق', 'توصيل', 'تاكسي',  # Arabic
            'chauffeur', 'livraison', 'taxi'  # French
        ],
        'shop_owner': [
            'shop', 'store', 'boutique', 'retail',
            'دكان', 'متجر', 'محل',  # Arabic
            'magasin', 'boutique', 'commerce'  # French
        ],
        'home_business': [
            'home', 'house', 'from home', 'catering', 'tutoring',
            'بيت', 'منزل', 'من البيت',  # Arabic
            'maison', 'domicile', 'à la maison'  # French
        ]
    }
    
    # Count keyword matches
    scores = {}
    for business_type, words in keywords.items():
        score = sum(1 for word in words if word in text)
        scores[business_type] = score
    
    # Return type with highest score
    best_match = max(scores, key=scores.get)
    
    # Default to market_vendor if no clear match
    if scores[best_match] == 0:
        return 'market_vendor'
    
    return best_match


def extract_years_active(text: str) -> int:
    """Extract years in business from transcript"""
    
    # Look for year patterns
    patterns = [
        r'(\d+)\s*(?:years?|سنوات?|ans?)',
        r'(?:for|since|منذ|depuis)\s*(\d+)',
        r'(\d+)\s*(?:year|سنة|année)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            years = int(match.group(1))
            # Clamp to reasonable range
            return max(1, min(years, 40))
    
    # Default: extract first number as years (if reasonable)
    numbers = re.findall(r'\d+', text)
    if numbers:
        first_num = int(numbers[0])
        if 1 <= first_num <= 40:
            return first_num
    
    # Default value
    return 5


def extract_income(text: str) -> int:
    """Extract monthly income from transcript"""
    
    # Look for income patterns
    patterns = [
        r'(\d+)\s*(?:TND|dinar|دينار)',
        r'(?:earn|make|income|دخل|revenu)\s*(\d+)',
        r'(\d+)\s*(?:per month|monthly|شهريا|par mois)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            income = int(match.group(1))
            # Clamp to reasonable range
            return max(100, min(income, 50000))
    
    # Look for any large number (likely income)
    numbers = re.findall(r'\d+', text)
    if numbers:
        large_numbers = [int(n) for n in numbers if 500 <= int(n) <= 20000]
        if large_numbers:
            return large_numbers[0]
    
    # Default value
    return 1500


def extract_keywords(text: str, archetype: str) -> list:
    """Extract relevant keywords from transcript"""
    
    # Common financial keywords
    keywords = [
        'business', 'income', 'expenses', 'profit', 'debt', 'loan',
        'عمل', 'دخل', 'مصاريف', 'ربح', 'دين', 'قرض',
        'entreprise', 'revenu', 'dépenses', 'profit', 'dette', 'prêt'
    ]
    
    found = [word for word in keywords if word in text]
    return found


def calculate_confidence(text: str, archetype: str, years: int, income: int) -> float:
    """Calculate extraction confidence score"""
    
    confidence = 0.5  # Base confidence
    
    # Boost if business type clearly identified
    if archetype in ['craftsman', 'shop_owner', 'gig_worker']:
        confidence += 0.2
    
    # Boost if years seem reasonable
    if 2 <= years <= 30:
        confidence += 0.15
    
    # Boost if income seems reasonable
    if 500 <= income <= 10000:
        confidence += 0.15
    
    # Boost if transcript is detailed (longer)
    if len(text) > 100:
        confidence += 0.1
    
    # Cap at 0.95
    return min(0.95, confidence)