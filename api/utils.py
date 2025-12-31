"""
Utility functions for saystory Carousel Generator
"""
import re
import os
import uuid
import requests
from django.conf import settings
import openai

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def validate_hex_color(color):
    """Validate and format hex color"""
    if not color:
        return '#FFFFFF'
    
    color = str(color).strip().upper()
    
    # Add # if missing
    if not color.startswith('#'):
        color = '#' + color
    
    # Validate format
    if re.match(r'^#[0-9A-F]{6}$', color):
        return color
    elif re.match(r'^#[0-9A-F]{3}$', color):
        # Expand shorthand
        return f'#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}'
    else:
        return '#405DE6'

def save_image_from_url(image_url, filename_prefix="slide"):
    """Download and save image from URL"""
    try:
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Generate filename
        filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filename
        
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return None

def generate_simple_slides(topic, slide_count):
    """Generate simple slides without OpenAI (fallback)"""
    slides = []
    for i in range(slide_count):
        slides.append({
            'title': f"{topic} - Part {i+1}",
            'description': f"Learn about {topic} in this comprehensive guide.",
            'image_prompt': f"saystory template background for {topic}",
            'background_color': '#405DE6',
            'font_color': '#FFFFFF'
        })
    return slides

def check_openai_connection():
    """Check if OpenAI API is working"""
    try:
        client.models.list()
        return True
    except:
        return False

def get_color_palette(platform):
    """Get color palette for specific platform"""
    palettes = {
        'instagram': ['#405DE6', '#8A2BE2', '#FF6B6B', '#4ECDC4', '#FFD166'],
        'linkedin': ['#0A66C2', '#333333', '#666666', '#999999', '#CCCCCC'],
        'twitter': ['#1DA1F2', '#14171A', '#657786', '#AAB8C2', '#E1E8ED'],
        'presentation': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6BAA75']
    }
    return palettes.get(platform, palettes['instagram'])

def create_slide_image_url(filename):
    """Create full URL for slide image"""
    if not filename:
        return None
    return f"{settings.MEDIA_URL}{filename}"

def generate_saystory_background_svg(width, height, platform="instagram", style="modern"):
    """Generate a clean saystory-style SVG background"""
    import random
    
    # Platform-based color schemes
    color_schemes = {
        'instagram': {
            'gradients': [
                ['#667eea', '#764ba2'],
                ['#f093fb', '#f5576c'],
                ['#4facfe', '#00f2fe'],
                ['#43e97b', '#38f9d7'],
                ['#fa709a', '#fee140']
            ],
            'shapes': ['circle', 'ellipse', 'rectangle']
        },
        'linkedin': {
            'gradients': [
                ['#0A66C2', '#0077B5'],
                ['#333333', '#666666'],
                ['#4CAF50', '#81C784'],
                ['#FF9800', '#FFB74D'],
                ['#9C27B0', '#BA68C8']
            ],
            'shapes': ['rectangle', 'circle']
        }
    }
    
    scheme = color_schemes.get(platform, color_schemes['instagram'])
    gradient = random.choice(scheme['gradients'])
    shape_type = random.choice(scheme['shapes'])
    
    # Generate SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{gradient[0]};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{gradient[1]};stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Background gradient -->
        <rect width="{width}" height="{height}" fill="url(#bgGradient)" />
        
        <!-- Subtle abstract shapes -->
        <g opacity="0.1">
'''
    
    # Add random shapes
    for i in range(random.randint(3, 6)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(50, 200)
        
        if shape_type == 'circle':
            svg += f'            <circle cx="{x}" cy="{y}" r="{size//2}" fill="white" />'
        elif shape_type == 'ellipse':
            rx = random.randint(25, 100)
            ry = random.randint(25, 100)
            svg += f'            <ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="white" />'
        else:  # rectangle
            w = random.randint(50, 150)
            h = random.randint(50, 150)
            svg += f'            <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" rx="10" />'
    
    svg += '''
        </g>
    </svg>'''
    
    return svg

def get_platform_dimensions(platform, format_type="square"):
    """Get platform-specific saystorys dimensions"""
    dimensions = {
        'instagram': {
            'square': (1080, 1080),
            'portrait': (1080, 1350),
            'story': (1080, 1920),
            'landscape': (1080, 608)
        },
        'linkedin': {
            'square': (1080, 1080),
            'portrait': (1080, 1350),
            'story': (1080, 1920),
            'landscape': (1200, 627)
        }
    }
    
    platform_dims = dimensions.get(platform, dimensions['instagram'])
    return platform_dims.get(format_type, platform_dims['square'])