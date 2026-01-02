"""
Enhanced Image Prompt Generator for Carousel Images

This module generates premium, visually connected image prompts that create
stunning carousel slides with flowing design elements and brand color integration.
"""

import random
import hashlib
from colorsys import rgb_to_hls, hls_to_rgb


# ==================== DESIGN STYLE TEMPLATES ====================

# Focus on LIGHT, AIRY templates only
DESIGN_TEMPLATES = {
    'cream_lifestyle': {
        'name': 'Cream Lifestyle',
        'description': 'Warm cream and beige tones with lifestyle objects, cozy and inviting',
        'visual_elements': [
            'Soft cream to warm beige gradient background',
            'Lifestyle objects arranged artistically (laptop, planner, coffee, plants)',
            'Natural wood textures and warm lighting',
            'Subtle sparkle or star accents for elegance'
        ],
        'flow_element': 'A subtle warm-toned curved line or shadow',
        'accent_style': 'warm golden highlights',
        'mood': 'cozy, warm, and inviting',
        'font_color': '#5D4E37'  # Warm brown
    },
    'soft_beige': {
        'name': 'Soft Beige',
        'description': 'Light beige and off-white with clean minimalist objects',
        'visual_elements': [
            'Clean off-white to light beige background',
            'Minimalist desk setup with modern devices',
            'Soft shadows and clean lines',
            'Subtle geometric accents'
        ],
        'flow_element': 'A thin elegant dividing line',
        'accent_style': 'clean shadow effects',
        'mood': 'clean, modern, and professional',
        'font_color': '#3D3D3D'  # Charcoal gray
    },
    'warm_ivory': {
        'name': 'Warm Ivory',
        'description': 'Ivory and pale peach with elegant illustrated people',
        'visual_elements': [
            'Ivory to pale peach gradient background',
            'Stylized illustrated person working or presenting',
            'Elegant furniture and workspace elements',
            'Soft ambient lighting effects'
        ],
        'flow_element': 'Flowing illustration that extends across slides',
        'accent_style': 'soft peachy highlights',
        'mood': 'elegant and aspirational',
        'font_color': '#6B4423'  # Rich brown
    },
    'light_gray_minimal': {
        'name': 'Light Gray Minimal',
        'description': 'Soft gray with clean professional flat illustrations',
        'visual_elements': [
            'Light gray to white gradient background',
            'Flat-style illustrated person in business context',
            'Clean charts, graphs, or business icons',
            'Minimalist city skyline or office window'
        ],
        'flow_element': 'A clean horizontal accent line',
        'accent_style': 'subtle blue-gray accents',
        'mood': 'professional and trustworthy',
        'font_color': '#2C3E50'  # Dark blue-gray
    },
    'pastel_blush': {
        'name': 'Pastel Blush',
        'description': 'Very light pink and cream with feminine elegance',
        'visual_elements': [
            'Pale blush pink to cream gradient',
            'Beauty or lifestyle products arranged elegantly',
            'Soft floral or abstract organic shapes',
            'Delicate sparkle and shimmer effects'
        ],
        'flow_element': 'A soft curved pastel ribbon',
        'accent_style': 'delicate rose gold accents',
        'mood': 'feminine, soft, and elegant',
        'font_color': '#8B5A5A'  # Dusty rose brown
    },
    'clean_white': {
        'name': 'Clean White',
        'description': 'Crisp white with strategic pops of objects and color',
        'visual_elements': [
            'Bright white to very light gray background',
            'Flat-lay style arrangement of topic-relevant objects',
            'Strategic negative space for text',
            'Minimal accent colors only on objects'
        ],
        'flow_element': 'A simple connecting line or shape',
        'accent_style': 'clean object placement',
        'mood': 'fresh, clean, and modern',
        'font_color': '#333333'  # Almost black
    },
    'sand_neutral': {
        'name': 'Sand Neutral',
        'description': 'Sandy beige and taupe with earthy warmth',
        'visual_elements': [
            'Warm sand to taupe gradient background',
            'Natural materials like notebooks, leather, wood',
            'Earthy textures and organic shapes',
            'Warm ambient lighting'
        ],
        'flow_element': 'An organic curved shape or wave',
        'accent_style': 'warm earthy accents',
        'mood': 'grounded, natural, and authentic',
        'font_color': '#4A3728'  # Dark brown
    },
    'pearl_elegant': {
        'name': 'Pearl Elegant',
        'description': 'Pearlescent white and soft gray with luxury feel',
        'visual_elements': [
            'Pearl white to soft silver gradient',
            'Elegant illustrated professional or lifestyle scene',
            'Subtle shimmer and light effects',
            'Premium minimalist design elements'
        ],
        'flow_element': 'A subtle gradient transition',
        'accent_style': 'pearlescent sheen',
        'mood': 'luxurious and premium',
        'font_color': '#2F2F2F'  # Dark charcoal
    }
}

# ==================== COLOR PALETTES ====================
# VIBRANT yet light palettes - each topic gets its OWN distinctive color scheme!

TOPIC_COLOR_PALETTES = {
    'business': {
        'background': '#F0F4F8',
        'background_alt': '#E8EEF4',
        'accent_bg': '#E3F2FD',
        'font_color': '#1A365D',
        'accent': '#3182CE',
        'highlight': '#63B3ED',
        'light': '#F7FAFC',
        'objects': 'laptop, business charts, coffee cup, notebook, pen, smartphone, office desk, glass wall office, floating UI panels, minimal desk accessories, digital clock, leather chair, desk plant, sticky notes, tablet stand, wireless mouse, presentation screen, business documents, clipboard, file folders',
        'creative_elements': 'business infographics, statistics icons, growth charts, professional person in suit, abstract geometric shapes, subtle shadows, corporate illustration style, layered depth, soft reflections, modern gradients, isometric elements, corporate icons, workflow arrows, clean grid layout'
    },
    'marketing': {
        'background': '#FFF0F5',
        'background_alt': '#FFE4EC',
        'accent_bg': '#FED7E2',
        'font_color': '#702459',
        'accent': '#ED64A6',
        'highlight': '#F687B3',
        'light': '#FFF5F7',
        'objects': 'phone with instagram, ring light, camera, pink laptop, content calendar, floating emojis, aesthetic props, neon frame, tripod, mic, story stickers, analytics dashboard, brand mood board, marketing funnel chart',
        'creative_elements': 'social media icons, heart icons, like buttons, influencer aesthetic, pink neon signs, gradient overlays, viral reel UI, sparkles, glow effects, motion arrows, floating reactions, swipe indicators, CTA buttons'
    },
    'technology': {
        'background': '#EBF4FF',
        'background_alt': '#E2E8F0',
        'accent_bg': '#C3DAFE',
        'font_color': '#2D3748',
        'accent': '#667EEA',
        'highlight': '#7F9CF5',
        'light': '#F0F5FF',
        'objects': 'modern laptop, smartphone, tablet, headphones, smart devices, code on screen, holographic screen, glowing keyboard, server racks, VR headset, robotic arm, digital assistant orb, microchips, circuit boards',
        'creative_elements': 'circuit patterns, data visualization, tech icons, futuristic UI elements, neon lines, AI brain illustration, cyber grid, HUD overlays, sci-fi lighting, volumetric glow, matrix style code rain'
    },
    'health': {
        'background': '#F0FFF4',
        'background_alt': '#E6FFED',
        'accent_bg': '#C6F6D5',
        'font_color': '#22543D',
        'accent': '#48BB78',
        'highlight': '#68D391',
        'light': '#F7FFF9',
        'objects': 'yoga mat, water bottle, fresh fruits, plants, fitness equipment, smoothie, smart watch, resistance bands, dumbbells, foam roller, gym towel, protein shaker',
        'creative_elements': 'leaves, wellness icons, heart rate graphics, healthy food flat-lay, calm gradients, sunlight rays, zen symbols, breathing patterns, organic shapes, mindfulness icons'
    },
    'lifestyle': {
        'background': '#FFFAF0',
        'background_alt': '#FFF5EB',
        'accent_bg': '#FEEBC8',
        'font_color': '#744210',
        'accent': '#ED8936',
        'highlight': '#F6AD55',
        'light': '#FFFCF5',
        'objects': 'planner, coffee, cozy blanket, candles, books, plants, aesthetic desk, ceramic mug, fairy lights, incense, journal, wooden tray, cushions, home decor items',
        'creative_elements': 'lifestyle flat-lay, cozy room aesthetic, morning routine items, self-care products, warm shadows, soft textures, lifestyle vignette, ambient lighting, neutral tones'
    },
    'education': {
        'background': '#EDF2F7',
        'background_alt': '#E2E8F0',
        'accent_bg': '#BEE3F8',
        'font_color': '#2A4365',
        'accent': '#4299E1',
        'highlight': '#63B3ED',
        'light': '#F7FAFC',
        'objects': 'books, notebook, pencils, glasses, desk lamp, apple, graduation cap, sticky notes, digital tablet, chalk, ruler, school bag, whiteboard',
        'creative_elements': 'study desk setup, lightbulb ideas, brain icons, learning graphics, doodle arrows, chalkboard texture, mind maps, academic diagrams, educational symbols'
    },
    'creative': {
        'background': '#FAF5FF',
        'background_alt': '#F3E8FF',
        'accent_bg': '#E9D8FD',
        'font_color': '#44337A',
        'accent': '#9F7AEA',
        'highlight': '#B794F4',
        'light': '#FDFAFF',
        'objects': 'camera, art supplies, sketchbook, color palette, iPad with stylus, paint tubes, creative props, scissors, brushes, markers, canvas board, glue tape',
        'creative_elements': 'paint splashes, creative tools, artistic workspace, colorful illustrations, abstract blobs, brush strokes, layered collage, surreal elements, mixed media textures'
    },
    'travel': {
        'background': '#E6FFFA',
        'background_alt': '#B2F5EA',
        'accent_bg': '#81E6D9',
        'font_color': '#234E52',
        'accent': '#38B2AC',
        'highlight': '#4FD1C5',
        'light': '#F0FFFC',
        'objects': 'passport, boarding pass, camera, suitcase, vintage map, sunglasses, airplane, travel stickers, compass, backpack, travel journal, map pins',
        'creative_elements': 'world map, destination pins, travel icons, adventure aesthetic, clouds, motion trails, paper cutouts, postcard style, travel doodles'
    },
    'finance': {
        'background': '#F0FFF4',
        'background_alt': '#E6FFED',
        'accent_bg': '#C6F6D5',
        'font_color': '#1C4532',
        'accent': '#38A169',
        'highlight': '#68D391',
        'light': '#F7FFF9',
        'objects': 'calculator, coins, money graphics, financial charts, piggy bank, laptop with graphs, credit cards, wallet, receipt slips, budget notebook',
        'creative_elements': 'money icons, growth arrows, financial infographics, investment graphics, glowing bars, stock tickers, upward graphs, profit indicators'
    },
    'fashion': {
        'background': '#FFF0F5',
        'background_alt': '#FFE4EC',
        'accent_bg': '#FED7E2',
        'font_color': '#702459',
        'accent': '#D53F8C',
        'highlight': '#ED64A6',
        'light': '#FFF5F8',
        'objects': 'clothing rack, fashion accessories, sunglasses, handbag, stylish outfits, mirror, heels, perfume bottle, jewelry, fabric swatches',
        'creative_elements': 'fashion sketches, runway aesthetic, style icons, trendy flat-lay, editorial lighting, magazine layout, fashion grids'
    },
    'food': {
        'background': '#FFFAF0',
        'background_alt': '#FFF5E6',
        'accent_bg': '#FEEBC8',
        'font_color': '#7B341E',
        'accent': '#DD6B20',
        'highlight': '#ED8936',
        'light': '#FFFCF5',
        'objects': 'beautiful food flat-lay, coffee, cooking ingredients, elegant plates, wooden table, herbs, napkin, cutlery, spices, sauce bowls',
        'creative_elements': 'food photography, recipe cards, kitchen aesthetic, chef icons, steam effects, rustic textures, overhead composition'
    },
    'default': {
        'background': '#F7FAFC',
        'background_alt': '#EDF2F7',
        'accent_bg': '#E2E8F0',
        'font_color': '#2D3748',
        'accent': '#4A5568',
        'highlight': '#718096',
        'light': '#FFFFFF',
        'objects': 'laptop, notebook, smartphone, coffee cup, modern desk items, ambient props, minimal decor, clean surfaces, neutral accessories',
        'creative_elements': 'clean minimalist aesthetic, professional workspace, modern design elements, soft gradients, depth layering, balanced composition'
    }
}

# Topic keywords for detection - expanded for better matching
TOPIC_KEYWORDS = {
    'business': ['business', 'startup', 'entrepreneur', 'company', 'finance', 'money', 'investment', 'sales', 'profit', 'ceo', 'success'],
    'marketing': ['marketing', 'social media', 'instagram', 'content', 'brand', 'audience', 'engagement', 'viral', 'followers', 'influencer', 'tiktok', 'reels'],
    'technology': ['tech', 'technology', 'ai', 'software', 'app', 'digital', 'computer', 'data', 'automation', 'code', 'programming', 'developer'],
    'health': ['health', 'fitness', 'wellness', 'diet', 'exercise', 'mental', 'meditation', 'yoga', 'nutrition', 'workout', 'gym'],
    'lifestyle': ['lifestyle', 'life', 'daily', 'routine', 'productivity', 'habits', 'morning', 'self-care', 'home'],
    'education': ['learn', 'education', 'course', 'study', 'teach', 'training', 'skill', 'tips', 'how to', 'guide', 'tutorial'],
    'creative': ['art', 'design', 'creative', 'photography', 'video', 'music', 'writing', 'craft', 'artist'],
    'travel': ['travel', 'trip', 'vacation', 'adventure', 'destination', 'explore', 'tourism', 'journey'],
    'finance': ['finance', 'investing', 'stocks', 'crypto', 'wealth', 'budget', 'savings', 'financial'],
    'fashion': ['fashion', 'style', 'outfit', 'clothing', 'beauty', 'makeup', 'skincare', 'trends'],
    'food': ['food', 'recipe', 'cooking', 'chef', 'restaurant', 'baking', 'cuisine', 'meal']
}


# ==================== HELPER FUNCTIONS ====================

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def generate_pastel_variant(hex_color, lightness_boost=0.25):
    """Generate a lighter pastel version of a color."""
    try:
        r, g, b = hex_to_rgb(hex_color)
        # Normalize to 0-1 range
        r, g, b = r/255.0, g/255.0, b/255.0
        # Convert to HLS
        h, l, s = rgb_to_hls(r, g, b)
        # Increase lightness and reduce saturation for pastel effect
        l = min(1.0, l + lightness_boost)
        s = max(0.3, s * 0.6)  # Reduce saturation
        # Convert back to RGB
        r, g, b = hls_to_rgb(h, l, s)
        return rgb_to_hex((r*255, g*255, b*255))
    except Exception:
        return '#FFE4EC'  # Default light pink


def generate_complementary_color(hex_color):
    """Generate a complementary/contrasting color."""
    try:
        r, g, b = hex_to_rgb(hex_color)
        # Simple complementary: rotate hue by 180 degrees
        r, g, b = r/255.0, g/255.0, b/255.0
        h, l, s = rgb_to_hls(r, g, b)
        h = (h + 0.5) % 1.0  # Rotate hue by 180 degrees
        r, g, b = hls_to_rgb(h, l, s)
        return rgb_to_hex((r*255, g*255, b*255))
    except Exception:
        return '#A29BFE'  # Default lavender


def get_topic_category(topic):
    """
    Determine topic category for color palette selection using TOPIC_KEYWORDS.
    Uses a SCORING system - category with most keyword matches wins.
    This prevents false matches like 'audience' triggering 'marketing' for travel content.
    """
    topic_lower = topic.lower()
    
    # Score each category based on keyword matches
    category_scores = {}
    for category, words in TOPIC_KEYWORDS.items():
        score = sum(1 for word in words if word in topic_lower)
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score, or 'default' if no matches
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        print(f"🔍 Topic detection scores: {category_scores} -> Best: {best_category}")
        return best_category
    
    return 'default'


def get_topic_color_palette(topic, brand_colors=None):
    """
    Get a color palette appropriate for the topic.
    If brand_colors provided, integrate them into the palette.
    """
    category = get_topic_category(topic)
    base_palette = TOPIC_COLOR_PALETTES.get(category, TOPIC_COLOR_PALETTES['default']).copy()
    
    # If brand colors are provided, incorporate them
    if brand_colors and len(brand_colors) > 0:
        base_palette['accent'] = brand_colors[0]
        base_palette['pastel'] = generate_pastel_variant(brand_colors[0])
        if len(brand_colors) > 1:
            base_palette['secondary'] = brand_colors[1]
    
    return base_palette


def generate_carousel_flow_seed(project_id, topic):
    """
    Generate a unique seed for carousel visual flow consistency.
    This ensures all slides in a carousel share the same design DNA.
    """
    seed_string = f"{project_id}-{topic}"
    return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)


def select_design_template(seed=None, style_hint=None):
    """
    Select a design template for the carousel.
    Uses seed for consistency across slides.
    All templates now use light colors only.
    """
    templates = list(DESIGN_TEMPLATES.keys())
    
    # Map style hints to preferred light-themed templates
    style_preferences = {
        'modern': ['light_gray_minimal', 'clean_white', 'soft_beige'],
        'minimal': ['clean_white', 'soft_beige', 'pearl_elegant'],
        'playful': ['pastel_blush', 'cream_lifestyle', 'warm_ivory'],
        'professional': ['light_gray_minimal', 'soft_beige', 'pearl_elegant'],
        'creative': ['warm_ivory', 'cream_lifestyle', 'pastel_blush'],
        'elegant': ['pearl_elegant', 'warm_ivory', 'cream_lifestyle']
    }
    
    if style_hint and style_hint.lower() in style_preferences:
        preferred = style_preferences[style_hint.lower()]
        # Filter to only templates that exist
        valid_preferred = [t for t in preferred if t in templates]
        if valid_preferred:
            if seed is not None:
                random.seed(seed)
            return random.choice(valid_preferred)
    
    if seed is not None:
        random.seed(seed)
    
    return random.choice(templates)


# ==================== FLOW POSITION DESCRIPTIONS ====================

def get_slide_flow_description(slide_number, total_slides, flow_element):
    """
    Generate position-specific flow description for visual connectivity.
    """
    if slide_number == 1:
        # First slide: Element enters from left or originates
        return f"""
VISUAL FLOW POSITION: OPENING SLIDE (1 of {total_slides})
- {flow_element} ORIGINATES from the LEFT edge of the composition
- The element should flow gracefully toward the RIGHT edge
- Create a sense of beginning - the visual journey starts here
- Element should EXIT toward the right edge, inviting viewers to swipe
- Include a subtle "swipe" visual cue in bottom area"""
    
    elif slide_number == total_slides:
        # Last slide: Element concludes, call-to-action zone
        return f"""
VISUAL FLOW POSITION: CLOSING SLIDE ({slide_number} of {total_slides})
- {flow_element} ENTERS from the LEFT edge (continuing from previous slide)
- The element should CONCLUDE gracefully in the center or right area
- Create a sense of completion and resolution
- Include visual space for a call-to-action message
- Design should feel like a satisfying ending to the visual journey"""
    
    else:
        # Middle slides: Element flows through
        return f"""
VISUAL FLOW POSITION: MIDDLE SLIDE ({slide_number} of {total_slides})
- {flow_element} ENTERS from the LEFT edge (continuing from previous slide)
- The element should flow ACROSS the composition
- Element EXITS toward the RIGHT edge (continuing to next slide)
- Maintain visual rhythm and momentum
- Keep the flowing element at roughly the same vertical position for continuity"""


# ==================== MAIN PROMPT GENERATOR ====================

def generate_enhanced_image_prompt(
    topic,
    slide_number,
    total_slides,
    platform='instagram',
    style='modern',
    brand_colors=None,
    project_id=None
):
    """
    Generate an enhanced, premium image prompt for carousel slide generation.
    Uses MINIMAL objects/elements - only 1-2 unique items per slide.
    Each slide gets different elements to avoid repetition across the carousel.
    """
    
    # Generate consistent seed for this carousel
    seed = generate_carousel_flow_seed(project_id or 0, topic)
    
    # Select design template
    template_key = select_design_template(seed, style)
    template = DESIGN_TEMPLATES[template_key]
    
    # Get color palette based on topic
    color_palette = get_topic_color_palette(topic, brand_colors)
    
    # Get topic category for context
    topic_category = get_topic_category(topic)
    
    # Use topic-specific background colors
    bg_color = color_palette.get('background', '#F7FAFC')
    bg_alt = color_palette.get('background_alt', '#EDF2F7')
    accent_bg = color_palette.get('accent_bg', '#E2E8F0')
    accent_color = color_palette.get('accent', '#4A5568')
    font_color = color_palette.get('font_color', '#2D3748')
    
    # Get topic-relevant objects and creative elements as lists
    objects_str = color_palette.get('objects', 'laptop, notebook, coffee cup, smartphone')
    creative_str = color_palette.get('creative_elements', 'modern minimalist aesthetic, clean design elements')
    
    # Split into individual items
    all_objects = [obj.strip() for obj in objects_str.split(',')]
    all_creative = [elem.strip() for elem in creative_str.split(',')]
    
    # Select 2-3 UNIQUE objects for this slide (cycling through to avoid repetition)
    object_index = (slide_number - 1) % len(all_objects)
    # Get 2-3 objects, starting from the slide's index
    selected_objects = []
    for i in range(3):  # Get up to 3 objects
        idx = (object_index + i) % len(all_objects)
        if all_objects[idx] not in selected_objects:
            selected_objects.append(all_objects[idx])
    selected_objects_str = ', '.join(selected_objects[:3])
    
    # Select UNIQUE creative element for this slide
    creative_index = (slide_number - 1) % len(all_creative)
    selected_creative = all_creative[creative_index]
    
    # Get flow description
    flow_desc = get_slide_flow_description(
        slide_number, 
        total_slides, 
        template['flow_element']
    )
    
    # Select only 1 visual element for this slide (minimal approach)
    visual_elements = template['visual_elements']
    visual_index = (slide_number - 1) % len(visual_elements)
    selected_visual = visual_elements[visual_index]
    
    # Determine if topic is detailed enough for dynamic object extraction
    # If topic is short (< 30 chars), use predefined objects as fallback
    topic_is_detailed = len(topic) >= 30
    
    if topic_is_detailed:
        # For detailed topics, let AI derive objects from the topic itself
        objects_instruction = f"""
🎯 DYNAMIC OBJECTS - EXTRACT FROM TOPIC:
Analyze the topic "{topic}" and CREATE illustrations of objects that DIRECTLY relate to it:
- If about PIZZA → draw pizza slices, toppings (pepperoni, olives, cheese), pizza box, oven
- If about BURGER → draw burgers, buns, patties, lettuce, fries, ketchup bottle
- If about TRAVEL → draw suitcases, planes, landmarks, passports, maps
- If about FITNESS → draw dumbbells, yoga mat, running shoes, water bottle
- If about COFFEE → draw coffee cups, beans, steam, latte art, coffee maker

IMPORTANT: Create objects that are SPECIFIC to "{topic}" - NOT generic laptops/phones!
Think: What objects would you SEE if you searched for "{topic}" on Pinterest?"""
    else:
        # For short/generic topics, use category-based fallback
        objects_instruction = f"""
🎯 TOPIC-RELATED OBJECTS:
Create illustrated objects related to {topic_category} theme:
- Suggested: {selected_objects_str}
- Creative accent: {selected_creative}
- Make them relevant to "{topic}" """
    
    # Build the enhanced prompt - DYNAMIC TOPIC-BASED ILLUSTRATION approach
    prompt = f"""⚠️ NO TEXT IN IMAGE. Keep 50-55% CENTER AREA completely CLEAR for text overlay.

CREATE: A STUNNING, DESIGNER-QUALITY carousel slide with TOPIC-SPECIFIC illustrations.

═══════════════════════════════════════════════════════════════
📌 USER'S TOPIC: "{topic}"
🎯 SLIDE {slide_number} OF {total_slides}
═══════════════════════════════════════════════════════════════

{flow_desc}

{objects_instruction}

🎨 AESTHETIC DESIGN:
- Soft, premium gradient background from {bg_color} to {bg_alt}
- Position ALL illustrated objects at CORNERS and EDGES ONLY
- Modern, trendy Instagram aesthetic
- Objects should be DIRECTLY RELATED to the topic content!

🖼️ COMPOSITION - CRITICAL:
┌─────────────────────────────────────────┐
│ [Topic object]       [Related item]     │
│                                         │
│         50-55% CLEAR CENTER             │
│         (for user's text)               │
│                                         │
│ [Decorative]         [Topic object]     │
└─────────────────────────────────────────┘

- Place 2-3 TOPIC-SPECIFIC illustrated objects in CORNERS
- Add small decorative elements along EDGES
- CENTER 50-55% must be COMPLETELY EMPTY for text

🔗 CONNECTING FLOW:
- Subtle curved ribbon or wave in {accent_color} along edges
- Creates visual continuity across carousel slides

✨ STYLE DETAILS:
- {selected_visual}
- Beautiful {accent_color} accent colors
- Soft sparkles (✦), gradient orbs near edges
- Elegant shadows and depth effects

🎭 PREMIUM QUALITY:
- Instagram influencer / Canva Pro aesthetic
- Looks EXPENSIVE and professionally designed
- User needs NO design skills - ready to post!

⚠️ AVOID:
- Generic objects unrelated to the topic
- Objects placed in the center
- Crowded compositions
- Flat, boring backgrounds

Create a design that perfectly represents "{topic}" with topic-specific illustrations!"""
    
    return prompt


def generate_slide_content_prompt(topic, slide_count, platform, style):
    """
    Generate an enhanced prompt for slide content generation.
    Uses TOPIC-SPECIFIC backgrounds and font colors that match the theme.
    """
    
    # Get the topic-specific color palette
    topic_category = get_topic_category(topic)
    palette = TOPIC_COLOR_PALETTES.get(topic_category, TOPIC_COLOR_PALETTES['default'])
    
    # Extract colors from palette
    bg_color = palette.get('background', '#F7FAFC')
    font_color = palette.get('font_color', '#2D3748')
    accent_color = palette.get('accent', '#4A5568')
    
    prompt = f"""Create {slide_count} carousel slides for "{topic}" that will go VIRAL on {platform}.

===== MANDATORY COLOR SCHEME FOR {topic_category.upper()} TOPIC =====
This is a {topic_category} carousel. Use these EXACT colors for ALL slides:
- background_color: "{bg_color}" (this is the {topic_category} theme background)
- font_color: "{font_color}" (this dark color matches the {topic_category} theme)
- accent_color: "{accent_color}" (for highlighted words)

DO NOT deviate from these colors - they are specifically designed for {topic_category} content!

===== CONTENT REQUIREMENTS =====
For each slide, provide:
- title: Compelling title (5-8 words) with ONE power word to emphasize
- highlight_word: The single most impactful word from the title
- description: Clear, valuable description (1-2 sentences)
- image_prompt: Description for background (NO TEXT in image, just objects/illustrations)
- background_color: "{bg_color}" (SAME for ALL slides)
- font_color: "{font_color}" (SAME for ALL slides)
- accent_color: "{accent_color}" (for highlighted word)

===== SLIDE STRUCTURE =====
- Slide 1: Hook/Attention grabber - Make them curious
- Slides 2-{slide_count-1}: Value delivery - Each with ONE key insight  
- Slide {slide_count}: Call to action - What should they do next?

===== IMAGE PROMPT GUIDELINES =====
Each image_prompt should describe:
1. {topic_category}-themed light background
2. Topic-relevant objects at edges/corners (flat-lay style)
3. OR a stylized illustrated person relevant to the topic
4. CLEAR center area for text (NO TEXT in image itself!)
5. Same visual theme across all slides

Return ONLY a JSON array with {slide_count} objects. No explanations.
CRITICAL: Use "{bg_color}" for background_color and "{font_color}" for font_color in ALL slides!"""
    
    return prompt


def get_topic_font_color(topic):
    """
    Get the appropriate dark font color for a topic.
    Returns a color that contrasts well with the topic's background.
    """
    topic_category = get_topic_category(topic)
    palette = TOPIC_COLOR_PALETTES.get(topic_category, TOPIC_COLOR_PALETTES['default'])
    return palette.get('font_color', '#2D3748')


def get_topic_background_color(topic):
    """
    Get the appropriate background color for a topic.
    """
    topic_category = get_topic_category(topic)
    palette = TOPIC_COLOR_PALETTES.get(topic_category, TOPIC_COLOR_PALETTES['default'])
    return palette.get('background', '#F7FAFC')


def get_topic_accent_color(topic):
    """
    Get the appropriate accent color for a topic.
    """
    topic_category = get_topic_category(topic)
    palette = TOPIC_COLOR_PALETTES.get(topic_category, TOPIC_COLOR_PALETTES['default'])
    return palette.get('accent', '#4A5568')


# ==================== UTILITY EXPORTS ====================

def get_all_design_templates():
    """Return all available design templates."""
    return {key: val['name'] for key, val in DESIGN_TEMPLATES.items()}


def get_all_topic_categories():
    """Return all topic categories with their palettes."""
    return list(TOPIC_COLOR_PALETTES.keys())

