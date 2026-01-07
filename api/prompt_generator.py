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
        'background': '#E8F4FD',   # Bright sky blue
        'background_alt': '#D0E8FF',  # Vibrant light blue
        'accent_bg': '#B8DCFF',    # Eye-catching blue wash
        'font_color': '#1A365D',   # Deep navy
        'accent': '#0066FF',       # BRIGHT electric blue
        'highlight': '#3399FF',    # Vibrant sky blue
        'light': '#F0F8FF',        # Alice blue
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
        'background': '#E8E0FF',   # Bright lavender
        'background_alt': '#D4C4FF',  # Vibrant purple-blue
        'accent_bg': '#C5B3FF',    # Eye-catching purple wash
        'font_color': '#2D1B69',   # Deep purple
        'accent': '#7C3AED',       # BRIGHT violet/purple
        'highlight': '#A855F7',    # Vibrant purple
        'light': '#F5F0FF',        # Light purple tint
        'objects': 'modern laptop, smartphone, tablet, headphones, smart devices, code on screen, holographic screen, glowing keyboard, server racks, VR headset, robotic arm, digital assistant orb, microchips, circuit boards',
        'creative_elements': 'circuit patterns, data visualization, tech icons, futuristic UI elements, neon lines, AI brain illustration, cyber grid, HUD overlays, sci-fi lighting, volumetric glow, matrix style code rain'
    },
    'health': {
        'background': '#CCFBF1',   # Bright teal-mint
        'background_alt': '#99F6E4',  # Vibrant turquoise
        'accent_bg': '#5EEAD4',    # Eye-catching teal wash
        'font_color': '#134E4A',   # Deep teal
        'accent': '#14B8A6',       # BRIGHT teal
        'highlight': '#2DD4BF',    # Vibrant cyan-teal
        'light': '#F0FDFA',        # Light teal tint
        'objects': 'yoga mat, water bottle, fresh fruits, plants, fitness equipment, smoothie, smart watch, resistance bands, dumbbells, foam roller, gym towel, protein shaker',
        'creative_elements': 'leaves, wellness icons, heart rate graphics, healthy food flat-lay, calm gradients, sunlight rays, zen symbols, breathing patterns, organic shapes, mindfulness icons'
    },
    'lifestyle': {
        'background': '#FEF3C7',   # Bright golden yellow
        'background_alt': '#FDE68A',  # Vibrant amber
        'accent_bg': '#FCD34D',    # Eye-catching yellow
        'font_color': '#78350F',   # Deep amber
        'accent': '#F59E0B',       # BRIGHT amber/orange
        'highlight': '#FBBF24',    # Vibrant gold
        'light': '#FFFBEB',        # Light yellow tint
        'objects': 'planner, coffee, cozy blanket, candles, books, plants, aesthetic desk, ceramic mug, fairy lights, incense, journal, wooden tray, cushions, home decor items',
        'creative_elements': 'lifestyle flat-lay, cozy room aesthetic, morning routine items, self-care products, warm shadows, soft textures, lifestyle vignette, ambient lighting, neutral tones'
    },
    'education': {
        'background': '#E0F7FF',   # Bright cyan-blue
        'background_alt': '#B8ECFF',  # Vibrant aqua
        'accent_bg': '#9BE0FF',    # Eye-catching cyan wash
        'font_color': '#0C4A6E',   # Deep teal
        'accent': '#0EA5E9',       # BRIGHT sky blue
        'highlight': '#38BDF8',    # Vibrant cyan
        'light': '#F0FAFF',        # Light aqua tint
        'objects': 'books, notebook, pencils, glasses, desk lamp, apple, graduation cap, sticky notes, digital tablet, chalk, ruler, school bag, whiteboard',
        'creative_elements': 'study desk setup, lightbulb ideas, brain icons, learning graphics, doodle arrows, chalkboard texture, mind maps, academic diagrams, educational symbols'
    },
    'creative': {
        'background': '#F5D0FE',   # Bright fuchsia-pink
        'background_alt': '#E879F9',  # Vibrant magenta
        'accent_bg': '#D946EF',    # Eye-catching purple-pink
        'font_color': '#701A75',   # Deep magenta
        'accent': '#C026D3',       # BRIGHT fuchsia
        'highlight': '#E879F9',    # Vibrant pink-purple
        'light': '#FDF4FF',        # Light fuchsia tint
        'objects': 'camera, art supplies, sketchbook, color palette, iPad with stylus, paint tubes, creative props, scissors, brushes, markers, canvas board, glue tape',
        'creative_elements': 'paint splashes, creative tools, artistic workspace, colorful illustrations, abstract blobs, brush strokes, layered collage, surreal elements, mixed media textures'
    },
    'travel': {
        'background': '#CFFAFE',   # Bright cyan
        'background_alt': '#A5F3FC',  # Vibrant sky cyan
        'accent_bg': '#67E8F9',    # Eye-catching aqua
        'font_color': '#164E63',   # Deep cyan
        'accent': '#06B6D4',       # BRIGHT cyan
        'highlight': '#22D3EE',    # Vibrant turquoise
        'light': '#ECFEFF',        # Light cyan tint
        'objects': 'passport, boarding pass, camera, suitcase, vintage map, sunglasses, airplane, travel stickers, compass, backpack, travel journal, map pins',
        'creative_elements': 'world map, destination pins, travel icons, adventure aesthetic, clouds, motion trails, paper cutouts, postcard style, travel doodles'
    },
    'finance': {
        'background': '#D4FFED',   # Bright mint green
        'background_alt': '#A7F3D0',  # Vibrant emerald light
        'accent_bg': '#6EE7B7',    # Eye-catching green wash
        'font_color': '#064E3B',   # Deep emerald
        'accent': '#10B981',       # BRIGHT emerald green
        'highlight': '#34D399',    # Vibrant green
        'light': '#ECFDF5',        # Light mint tint
        'objects': 'calculator, coins, money graphics, financial charts, piggy bank, laptop with graphs, credit cards, wallet, receipt slips, budget notebook',
        'creative_elements': 'money icons, growth arrows, financial infographics, investment graphics, glowing bars, stock tickers, upward graphs, profit indicators'
    },
    'fashion': {
        'background': '#FCE7F3',   # Bright pink
        'background_alt': '#FBCFE8',  # Vibrant rose
        'accent_bg': '#F9A8D4',    # Eye-catching hot pink
        'font_color': '#831843',   # Deep rose
        'accent': '#EC4899',       # BRIGHT hot pink
        'highlight': '#F472B6',    # Vibrant pink
        'light': '#FDF2F8',        # Light pink tint
        'objects': 'clothing rack, fashion accessories, sunglasses, handbag, stylish outfits, mirror, heels, perfume bottle, jewelry, fabric swatches',
        'creative_elements': 'fashion sketches, runway aesthetic, style icons, trendy flat-lay, editorial lighting, magazine layout, fashion grids'
    },
    'food': {
        'background': '#FFEDD5',   # Bright peach-orange
        'background_alt': '#FDBA74',  # Vibrant orange
        'accent_bg': '#FB923C',    # Eye-catching tangerine
        'font_color': '#7C2D12',   # Deep burnt orange
        'accent': '#F97316',       # BRIGHT orange
        'highlight': '#FB923C',    # Vibrant tangerine
        'light': '#FFF7ED',        # Light peach tint
        'objects': 'beautiful food flat-lay, coffee, cooking ingredients, elegant plates, wooden table, herbs, napkin, cutlery, spices, sauce bowls',
        'creative_elements': 'food photography, recipe cards, kitchen aesthetic, chef icons, steam effects, rustic textures, overhead composition'
    },
    'default': {
        'background': '#E0E7FF',   # Bright indigo-blue
        'background_alt': '#C7D2FE',  # Vibrant periwinkle
        'accent_bg': '#A5B4FC',    # Eye-catching indigo wash
        'font_color': '#312E81',   # Deep indigo
        'accent': '#6366F1',       # BRIGHT indigo
        'highlight': '#818CF8',    # Vibrant purple-blue
        'light': '#EEF2FF',        # Light indigo tint
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


# ==================== LAYER 2: PER-SLIDE VISUAL MATCHING ====================
# This system analyzes each slide's specific content to select relevant visual objects

SLIDE_PURPOSE_TYPES = {
    'data': {
        'name': 'Data/Statistics',
        'description': 'Presenting numbers, percentages, metrics, growth figures',
        'visual_approach': 'Charts, graphs, metrics with visual impact'
    },
    'process': {
        'name': 'Process/Flow',
        'description': 'Explaining steps, workflows, sequences, how things work',
        'visual_approach': 'Flowcharts, step diagrams, connected arrows'
    },
    'comparison': {
        'name': 'Comparison/Contrast',
        'description': 'Comparing options, before/after, pros/cons',
        'visual_approach': 'Split visuals, comparison tables, side-by-side'
    },
    'concept': {
        'name': 'Concept/Definition',
        'description': 'Explaining ideas, defining terms, abstract concepts',
        'visual_approach': 'Metaphorical illustrations, conceptual icons'
    },
    'timeline': {
        'name': 'Timeline/Sequence',
        'description': 'Historical progression, roadmaps, milestones',
        'visual_approach': 'Timeline graphics, milestone markers, journey path'
    },
    'problem_solution': {
        'name': 'Problem/Solution',
        'description': 'Identifying issues and proposing fixes',
        'visual_approach': 'Before/after visuals, problem icons, solution arrows'
    },
    'list': {
        'name': 'List/Itemization',
        'description': 'Bullet points, numbered lists, tips, features',
        'visual_approach': 'Icon grids, numbered graphics, checkbox visuals'
    },
    'quote': {
        'name': 'Quote/Testimonial',
        'description': 'Inspirational quotes, customer testimonials, expert opinions',
        'visual_approach': 'Elegant typography frames, quote marks, portrait frames'
    },
    'cta': {
        'name': 'Call-to-Action',
        'description': 'Encouraging action, signup, purchase, follow',
        'visual_approach': 'Button graphics, directional arrows, action icons'
    }
}

# Visual objects and icons for each slide purpose
VISUAL_OBJECTS_BY_PURPOSE = {
    'data': {
        'objects': 'bar chart, line graph, pie chart, metrics dashboard, upward arrow, percentage badge, growth indicator, data visualization panel',
        'icons': 'trending up arrow, chart icon, statistics graph, metric counter, progress bar, analytics icon',
        'style': 'clean data visualization, infographic style, bold numbers, highlighted metrics'
    },
    'process': {
        'objects': 'flowchart diagram, step arrows, numbered circles, process pipeline, gear mechanism, workflow nodes',
        'icons': 'connected arrows, step indicators, flow arrows, process wheels, sequential markers',
        'style': 'clean flowchart, numbered steps with connecting lines, process diagram aesthetic'
    },
    'comparison': {
        'objects': 'split screen layout, comparison table, versus badge, balance scale, side-by-side panels',
        'icons': 'vs symbol, comparison arrows, check/x marks, rating stars, pro/con icons',
        'style': 'dual layout, clear separation, before/after effect, contrast zones'
    },
    'concept': {
        'objects': 'lightbulb illustration, brain graphic, abstract shapes, conceptual diagram, thought bubble',
        'icons': 'idea bulb, brain icon, puzzle pieces, concept cloud, abstract symbols',
        'style': 'metaphorical illustration, abstract representation, conceptual visual'
    },
    'timeline': {
        'objects': 'horizontal timeline, milestone markers, date badges, journey path, roadmap illustration',
        'icons': 'calendar icon, clock, milestone flag, date marker, progress dots',
        'style': 'timeline graphic, chronological markers, journey visualization'
    },
    'problem_solution': {
        'objects': 'broken chain icon, warning symbol, checkmark solution, transformation arrow, before/after split',
        'icons': 'warning triangle, problem X, solution checkmark, fix wrench, healing cross',
        'style': 'problem illustration transitioning to solution, transformation visual'
    },
    'list': {
        'objects': 'numbered list graphic, icon grid, feature boxes, bullet point markers, checklist visual',
        'icons': 'numbered badges, checkbox icons, bullet markers, list icons, feature stars',
        'style': 'organized grid layout, numbered or bulleted visual list, icon collection'
    },
    'quote': {
        'objects': 'large quotation marks, elegant frame, portrait silhouette, speech bubble, testimonial card',
        'icons': 'quote marks, speech icon, person silhouette, star rating, testimonial badge',
        'style': 'elegant typography frame, inspirational quote layout, testimonial card design'
    },
    'cta': {
        'objects': 'call-to-action button, pointing arrow, follow icon, subscribe button, action badge',
        'icons': 'arrow pointing right, click cursor, follow plus, subscribe bell, action hand',
        'style': 'prominent action visual, directional emphasis, invitation to act'
    }
}

# Keywords that suggest specific slide purposes
KEYWORD_TO_PURPOSE = {
    # Data/Statistics keywords
    'data': ['percent', 'percentage', '%', 'growth', 'increase', 'decrease', 'revenue', 'sales', 
             'metrics', 'statistics', 'numbers', 'data', 'rate', 'ratio', 'score', 'results',
             'quarterly', 'annually', 'yoy', 'mom', 'kpi', 'roi', 'conversion', 'profits'],
    
    # Process/Flow keywords
    'process': ['step', 'steps', 'process', 'workflow', 'how to', 'guide', 'method', 'procedure',
                'framework', 'system', 'approach', 'sequence', 'phase', 'stage', 'pipeline'],
    
    # Comparison keywords
    'comparison': ['vs', 'versus', 'compare', 'comparison', 'difference', 'between', 'better',
                   'worse', 'pros', 'cons', 'advantages', 'disadvantages', 'option', 'alternative'],
    
    # Concept/Definition keywords
    'concept': ['what is', 'definition', 'meaning', 'concept', 'idea', 'understand', 'learn',
                'discover', 'introduce', 'about', 'overview', 'explained', 'basics'],
    
    # Timeline/Sequence keywords
    'timeline': ['timeline', 'history', 'evolution', 'journey', 'roadmap', 'milestone', 'future',
                 'past', 'present', 'year', 'quarter', 'month', 'when', 'date', 'period'],
    
    # Problem/Solution keywords
    'problem_solution': ['problem', 'challenge', 'issue', 'solution', 'fix', 'solve', 'overcome',
                         'struggle', 'difficulty', 'obstacle', 'barrier', 'pain point', 'mistake'],
    
    # List/Itemization keywords
    'list': ['tip', 'tips', 'ways', 'reasons', 'things', 'list', 'top', 'best', 'must', 'key',
             'essential', 'important', 'features', 'benefits', 'secrets', 'hacks', 'tricks'],
    
    # Quote/Testimonial keywords
    'quote': ['quote', 'said', 'says', 'according', 'expert', 'testimonial', 'review', 'feedback',
              'opinion', 'believe', 'philosophy', 'wisdom', 'inspiration', 'motivational'],
    
    # Call-to-Action keywords
    'cta': ['follow', 'subscribe', 'join', 'sign up', 'start', 'get started', 'try', 'download',
            'click', 'share', 'comment', 'save', 'contact', 'book', 'call', 'action', 'now', 'today']
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


# ==================== LAYER 2: PER-SLIDE ANALYSIS FUNCTIONS ====================

def analyze_slide_purpose(title, description):
    """
    Analyze a slide's title and description to determine its PRIMARY purpose.
    Returns the purpose type that best matches the slide's content.
    
    This is Layer 2 of the visual matching system - it looks at EACH slide's
    specific content rather than the global topic.
    """
    text = f"{title} {description}".lower()
    
    # Score each purpose based on keyword matches
    purpose_scores = {}
    for purpose, keywords in KEYWORD_TO_PURPOSE.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            purpose_scores[purpose] = score
    
    # Special handling for slide position heuristics
    title_lower = title.lower()
    
    # First slide often introduces a concept
    # Last slide often has CTA
    # These are factored in by the caller based on slide_number
    
    # Return the purpose with highest score
    if purpose_scores:
        best_purpose = max(purpose_scores, key=purpose_scores.get)
        print(f"  🔍 Slide purpose scores: {purpose_scores} → {best_purpose}")
        return best_purpose
    
    # Default to 'concept' if no clear purpose detected
    return 'concept'


def extract_slide_keywords(title, description, max_keywords=5):
    """
    Extract the most important content keywords from a slide.
    These keywords help inform what visual objects should appear.
    
    Returns a list of 3-5 key content words.
    """
    import re
    
    text = f"{title} {description}"
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'your',
        'you', 'we', 'they', 'our', 'their', 'how', 'why', 'what', 'when', 'where',
        'which', 'who', 'whom', 'whose', 'not', 'no', 'yes', 'all', 'each', 'every',
        'most', 'more', 'some', 'any', 'make', 'get', 'just', 'also', 'than'
    }
    
    # Extract words (alphanumeric only, 3+ chars)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stop words and keep unique meaningful words
    keywords = []
    seen = set()
    for word in words:
        if word not in stop_words and word not in seen:
            keywords.append(word)
            seen.add(word)
            if len(keywords) >= max_keywords:
                break
    
    return keywords


def get_purpose_specific_visuals(purpose, keywords=None, global_category=None):
    """
    Get the specific visual objects and style for a slide based on its purpose.
    
    Args:
        purpose: The slide's detected purpose (data, process, comparison, etc.)
        keywords: The slide's extracted keywords for additional context
        global_category: The overall topic category (business, tech, etc.) for color consistency
    
    Returns a dict with objects, icons, and style instructions for the image prompt.
    """
    # Get visuals for this purpose
    purpose_visuals = VISUAL_OBJECTS_BY_PURPOSE.get(purpose, VISUAL_OBJECTS_BY_PURPOSE['concept'])
    
    # Get purpose type info
    purpose_info = SLIDE_PURPOSE_TYPES.get(purpose, SLIDE_PURPOSE_TYPES['concept'])
    
    return {
        'purpose_name': purpose_info['name'],
        'visual_approach': purpose_info['visual_approach'],
        'objects': purpose_visuals['objects'],
        'icons': purpose_visuals['icons'],
        'style': purpose_visuals['style'],
        'keywords': keywords or []
    }


def get_slide_visual_context(title, description, slide_number, total_slides, global_topic):
    """
    Complete Layer 2 function that analyzes a slide and returns full visual context.
    
    This is the main entry point for per-slide visual matching.
    It combines purpose detection, keyword extraction, and visual selection.
    
    Args:
        title: The slide's title text
        description: The slide's description text  
        slide_number: Position in the carousel (1-indexed)
        total_slides: Total number of slides in carousel
        global_topic: The overall carousel topic for Layer 1 context
    
    Returns a dict with complete visual instructions for this specific slide.
    """
    print(f"\n🎯 LAYER 2 ANALYSIS - Slide {slide_number}/{total_slides}")
    print(f"  📝 Title: {title[:50]}...")
    
    # Extract keywords from this slide's content
    keywords = extract_slide_keywords(title, description)
    print(f"  🔑 Keywords: {keywords}")
    
    # Detect the slide's primary purpose
    purpose = analyze_slide_purpose(title, description)
    
    # Apply position-based purpose overrides
    if slide_number == 1:
        # First slide is often introductory/concept
        if purpose not in ['data', 'timeline']:
            purpose = 'concept'
    elif slide_number == total_slides:
        # Last slide is often CTA
        purpose = 'cta'
    
    print(f"  🎭 Final Purpose: {purpose}")
    
    # Get global category for color consistency
    global_category = get_topic_category(global_topic)
    
    # Get purpose-specific visuals
    visuals = get_purpose_specific_visuals(purpose, keywords, global_category)
    
    # Add slide-specific context
    visuals['slide_number'] = slide_number
    visuals['total_slides'] = total_slides
    visuals['detected_purpose'] = purpose
    visuals['global_category'] = global_category
    
    return visuals




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
    project_id=None,
    slide_title=None,
    slide_description=None
):
    """
    Generate an enhanced, premium image prompt for carousel slide generation.
    
    Now includes TWO-LAYER MATCHING:
    - Layer 1: Global theme detection from topic (colors, overall style)
    - Layer 2: Per-slide visual matching based on slide's specific content
    
    Each slide gets visuals that directly support its specific content.
    """
    
    # Generate consistent seed for this carousel
    seed = generate_carousel_flow_seed(project_id or 0, topic)
    
    # Select design template
    template_key = select_design_template(seed, style)
    template = DESIGN_TEMPLATES[template_key]
    
    # LAYER 1: Get color palette based on global topic
    color_palette = get_topic_color_palette(topic, brand_colors)
    topic_category = get_topic_category(topic)
    
    # Use topic-specific background colors
    bg_color = color_palette.get('background', '#F7FAFC')
    bg_alt = color_palette.get('background_alt', '#EDF2F7')
    accent_bg = color_palette.get('accent_bg', '#E2E8F0')
    accent_color = color_palette.get('accent', '#4A5568')
    font_color = color_palette.get('font_color', '#2D3748')
    
    # LAYER 2: Per-slide visual context (if slide content is provided)
    slide_visual_context = None
    if slide_title and slide_description:
        slide_visual_context = get_slide_visual_context(
            title=slide_title,
            description=slide_description,
            slide_number=slide_number,
            total_slides=total_slides,
            global_topic=topic
        )
    
    # Get flow description for seamless carousel
    flow_desc = get_slide_flow_description(
        slide_number, 
        total_slides, 
        template['flow_element']
    )
    
    # Build objects instruction based on Layer 2 analysis
    if slide_visual_context:
        # USE LAYER 2: Purpose-specific visuals for THIS slide
        purpose_name = slide_visual_context['purpose_name']
        visual_approach = slide_visual_context['visual_approach']
        purpose_objects = slide_visual_context['objects']
        purpose_icons = slide_visual_context['icons']
        purpose_style = slide_visual_context['style']
        keywords = slide_visual_context['keywords']
        
        objects_instruction = f"""
🎯 LAYER 2: SLIDE-SPECIFIC VISUAL MATCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 SLIDE TITLE: "{slide_title}"
📝 DETECTED PURPOSE: {purpose_name}
🔑 KEY CONTENT: {', '.join(keywords)}

🎨 VISUAL APPROACH FOR THIS SLIDE:
{visual_approach}

📦 RECOMMENDED OBJECTS FOR THIS SLIDE:
{purpose_objects}

🏷️ RECOMMENDED ICONS:
{purpose_icons}

🖼️ VISUAL STYLE:
{purpose_style}

⚡ CRITICAL: The visuals MUST directly relate to "{slide_title}"
Do NOT use generic objects - use objects that SPECIFICALLY support this slide's content!
"""
    else:
        # Fallback to Layer 1 topic-based objects
        objects_str = color_palette.get('objects', 'laptop, notebook, coffee cup, smartphone')
        creative_str = color_palette.get('creative_elements', 'modern minimalist aesthetic, clean design elements')
        
        all_objects = [obj.strip() for obj in objects_str.split(',')]
        all_creative = [elem.strip() for elem in creative_str.split(',')]
        
        object_index = (slide_number - 1) % len(all_objects)
        selected_objects = []
        for i in range(3):
            idx = (object_index + i) % len(all_objects)
            if all_objects[idx] not in selected_objects:
                selected_objects.append(all_objects[idx])
        selected_objects_str = ', '.join(selected_objects[:3])
        
        creative_index = (slide_number - 1) % len(all_creative)
        selected_creative = all_creative[creative_index]
        
        objects_instruction = f"""
🎯 TOPIC-RELATED OBJECTS (Layer 1 - Global Theme):
Create illustrated objects related to {topic_category} theme:
- Suggested: {selected_objects_str}
- Creative accent: {selected_creative}
- Make them relevant to "{topic}" """
    
    # Build the enhanced prompt - CANVA-INSPIRED PREMIUM DESIGN approach
    prompt = f"""Create a SCROLL-STOPPING carousel background inspired by premium Canva templates.

═══════════════════════════════════════════════════════════════
📌 TOPIC: "{topic}"
🎯 SLIDE {slide_number} OF {total_slides} - Part of ONE SEAMLESS DESIGN!
═══════════════════════════════════════════════════════════════

{flow_desc}

🎨 CANVA-STYLE DESIGN APPROACH:
Create a PREMIUM, HIGH-END carousel background with:
- HIGH-CONTRAST colors: bold {accent_color} against soft {bg_color} background
- Soft gradient flowing from {bg_color} → {bg_alt}
- EDGE-LOADING: Objects placed at TOP and BOTTOM edges only
- CENTRAL READABILITY ZONE: 55-60% clear center for text
- GLASSMORPHISM: Semi-transparent, blurred overlay effects
- Premium, professional aesthetic like Canva Pro templates

🔗 SEAMLESS CONTINUITY (PANORAMIC EFFECT):
- Elements should BLEED off the right edge of this slide
- And CONTINUE from the left edge of the next slide
- When swiped, all {total_slides} slides feel like ONE continuous artwork
- Use flowing shapes, gradients, or abstract elements that connect slides
- This creates the premium "seamless carousel" effect

{objects_instruction}

🖼️ COMPOSITION - EDGE-LOADING TECHNIQUE:
┌─────────────────────────────────────────┐
│ ▓▓ [Objects/graphics at TOP] ▓▓        │
│                                         │
│      ╔═══════════════════════╗         │
│      ║  55-60% CLEAR CENTER  ║         │
│      ║  (READABILITY ZONE)   ║         │
│      ╚═══════════════════════╝         │
│                                         │
│ ▓▓ [Objects/graphics at BOTTOM] ▓▓     │
└─────────────────────────────────────────┘

📝 CENTRAL READABILITY ZONE - CRITICAL:
- 55-60% clear center space for the user's text
- This zone should be BRIGHT, CLEAN, and BREATHABLE
- NO complex backgrounds or busy patterns in center
- Soft, pale {bg_color} or subtle gradient only
- User will place BOLD TITLE and text here
- Keep generous margin space around text area

✨ VISUAL ELEMENTS (CANVA-STYLE):
- MICRO-ACCENTS: Small decorative shapes at edges (+, sparkles, geometric shapes)
- GLASSMORPHISM: Frosted glass overlays with blur effect
- SOFT GRADIENTS: Subtle color transitions for depth
- FRAMING: Objects in opposite corners (top-left and bottom-right)
- FLOWING SHAPES: Abstract elements that bleed off edges

🌟 PREMIUM AESTHETICS:
- Minimalist yet visually rich
- Soft muted tones OR bold high-contrast (choose based on topic)
- Professional "breathing room" with intentional negative space
- Modern, clean, Instagram-worthy design
- Looks like a design agency template

🎭 STYLE OPTIONS:
- For {topic}: Use appropriate style (professional/playful/elegant)
- HIGH-CONTRAST for scroll-stopping impact
- SOFT/MUTED for premium, high-end feel
- Always CINEMATIC and professionally art-directed

⛔ DO NOT INCLUDE:
- NO text, NO typography, NO words, NO letters
- NO logos, NO watermarks
- NO objects in the CENTER (only edges!)
- NO busy/complex center backgrounds
- NO disconnected random elements

Create a CANVA-QUALITY, SEAMLESS carousel background that makes users want to swipe through!"""
    
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

