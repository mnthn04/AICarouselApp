"""
saystory Carousel Generator - AI-Powered Slide Creation
Uses OpenAI APIs
"""

import json
import openai
import requests
from PIL import Image
import os
import uuid
import re
import traceback
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CarouselProject, Slide, CarouselTemplate, ContentPreview
from .utils import (
    validate_hex_color, save_image_from_url, generate_simple_slides,
    check_openai_connection, get_color_palette, create_slide_image_url,
    generate_saystory_background_svg, get_platform_dimensions
)
from .prompt_generator import (
    generate_enhanced_image_prompt,
    generate_slide_content_prompt,
    get_topic_color_palette,
    get_topic_category,
    generate_pastel_variant
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# ==================== VIEWS ====================

def index(request):
    """Home page - saystory Carousel Generator"""
    return render(request, 'api/index.html')

def templates_page(request):
    """Templates Page - Display pre-generated carousel templates"""
    # Fetch all active templates grouped by category
    templates = CarouselTemplate.objects.filter(is_active=True)
    
    # Group templates by category
    categories = {}
    for template in templates:
        if template.category not in categories:
            categories[template.category] = {
                'name': dict(CarouselTemplate.CATEGORY_CHOICES).get(template.category, template.category),
                'templates': []
            }
        categories[template.category]['templates'].append(template)
    
    return render(request, 'api/templates_page.html', {
        'categories': categories,
        'templates': templates
    })

def recent_page(request):
    """Recent Projects Page"""
    recent_projects = CarouselProject.objects.all().prefetch_related('slides').order_by('-created_at')
    return render(request, 'api/recent_page.html', {
        'recent_projects': recent_projects
    })


@csrf_exempt
def use_template(request, template_id):
    """Create a new carousel project from a template"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        template = CarouselTemplate.objects.get(id=template_id, is_active=True)
        
        # Parse slide images from template
        slide_images = json.loads(template.slide_images) if template.slide_images else []
        
        # Create new project from template
        project = CarouselProject.objects.create(
            topic=template.description or template.name,
            platform=template.platform,
            style=template.style,
            slide_count=template.slide_count
        )
        
        # Create slides with template images
        for i, image_base64 in enumerate(slide_images, 1):
            # Save the image to media folder
            import base64
            from django.conf import settings
            
            image_filename = f"template_{template_id}_slide_{i}_{uuid.uuid4().hex[:8]}.png"
            image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
            
            # Decode and save the base64 image
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_base64))
            
            Slide.objects.create(
                project=project,
                slide_number=i,
                title=f"Slide {i}",
                description="",
                image_prompt="Template image",
                background_color=template.primary_color,
                font_color=template.font_color,
                generated_image=image_filename
            )
        
        # Increment template use count
        template.use_count += 1
        template.save()
        
        return JsonResponse({
            'success': True,
            'project_id': project.id,
            'message': 'Carousel created from template',
            'redirect_url': f'/editor/{project.id}/'
        })
        
    except CarouselTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def editor(request, project_id=None):
    """saystory-style Visual Editor"""
    try:
        if project_id:
            project = CarouselProject.objects.get(id=project_id)
            slides = Slide.objects.filter(project=project).order_by('slide_number')
            
            if not slides.exists():
                return render(request, 'api/editor.html', {
                    'project_id': project_id,
                    'error': 'No slides found. Please generate a carousel first.'
                })
            
            # Prepare slide data with image URLs
            slides_data = []
            for slide in slides:
                slide_dict = {
                    'id': slide.id,
                    'slide_number': slide.slide_number,
                    'title': slide.title,
                    'description': slide.description,
                    'image_prompt': slide.image_prompt,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color,
                    'font_color': slide.font_color,
                    'saystorys_width': slide.saystorys_width,
                    'saystorys_height': slide.saystorys_height,
                    'generated_image': slide.generated_image,
                    'extra_text': slide.extra_text,
                    'extra_texts': slide.extra_texts, # Pass list of texts
                    'text_styles': slide.text_styles, # Pass styles to frontend
                    'title_x': slide.title_x,
                    'title_y': slide.title_y,
                    'description_x': slide.description_x,
                    'description_y': slide.description_y,
                    'extra_text_x': slide.extra_text_x,
                    'extra_text_y': slide.extra_text_y,
                    'user_images': slide.user_images, # Pass list of user images
                    'layout': slide.layout  # Slide layout (image-top, image-left, image-right, full-background)
                }
                
                # Add full image URL if exists
                if slide.generated_image:
                    slide_dict['generated_image_url'] = f"{settings.MEDIA_URL}{slide.generated_image}"
                
                slides_data.append(slide_dict)
            
            return render(request, 'api/editor.html', {
                'project_id': project_id,
                'slides': slides_data
            })
        else:
            return render(request, 'api/editor.html', {
                'error': 'No project ID provided'
            })
    except CarouselProject.DoesNotExist:
        return render(request, 'api/index.html', {
            'error': 'Project not found. Please generate a new carousel.'
        })

def result(request, project_id):
    """Result page"""
    try:
        project = CarouselProject.objects.get(id=project_id)
        slides = Slide.objects.filter(project=project).order_by('slide_number')
        
        # Prepare slides with image URLs
        slides_data = []
        for slide in slides:
            slide_dict = {
                'id': slide.id,
                'slide_number': slide.slide_number,
                'title': slide.title,
                'description': slide.description,
                'background_color': slide.background_color,
                'font_color': slide.font_color,
                'generated_image': slide.generated_image
            }
            
            if slide.generated_image:
                slide_dict['generated_image_url'] = f"{settings.MEDIA_URL}{slide.generated_image}"
            
            slides_data.append(slide_dict)
        
        return render(request, 'api/result.html', {
            'project_id': project_id,
            'slide_count': slides.count(),
            'slides': slides_data
        })
    except CarouselProject.DoesNotExist:
        return render(request, 'api/index.html')

# ==================== UTILITY FUNCTIONS ====================

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
        return '#405DE6'  # Default Instagram blue

def create_default_slides(topic, slide_count, platform, style):
    """Create default slides when OpenAI fails"""
    print(f"🔄 Creating default slides for {topic}")
    
    # Color palettes for different platforms
    color_palettes = {
        'instagram': [
            ('#405DE6', '#FFFFFF'),  # Instagram blue
            ('#8A2BE2', '#FFFFFF'),  # Blue violet  
            ('#FF6B6B', '#FFFFFF'),  # Coral red
            ('#4ECDC4', '#000000'),  # Turquoise
            ('#FFD166', '#000000'),  # Yellow
        ],
        'linkedin': [
            ('#0A66C2', '#FFFFFF'),  # LinkedIn blue
            ('#333333', '#FFFFFF'),  # Dark gray
            ('#666666', '#FFFFFF'),  # Medium gray
            ('#999999', '#000000'),  # Light gray
            ('#CCCCCC', '#000000'),  # Very light gray
        ],
        'twitter': [
            ('#1DA1F2', '#FFFFFF'),  # Twitter blue
            ('#14171A', '#FFFFFF'),  # Dark
            ('#657786', '#FFFFFF'),  # Gray
            ('#AAB8C2', '#000000'),  # Light gray
            ('#E1E8ED', '#000000'),  # Very light gray
        ],
        'presentation': [
            ('#2E86AB', '#FFFFFF'),  # Professional blue
            ('#A23B72', '#FFFFFF'),  # Purple
            ('#F18F01', '#000000'),  # Orange
            ('#C73E1D', '#FFFFFF'),  # Red
            ('#6BAA75', '#000000'),  # Green
        ]
    }
    
    # Get color palette for platform
    colors = color_palettes.get(platform, color_palettes['instagram'])

    # saystory-style slide templates - more professional and engaging
    templates = [
        {
            'title': f"Unlock {topic} Excellence",
            'description': f"Discover the essential concepts that drive success in {topic}.",
            'suffix': "minimal clean background with soft gradients"
        },
        {
            'title': f"Master {topic} Fundamentals",
            'description': f"Build a strong foundation with core {topic} principles.",
            'suffix': "professional geometric shapes and subtle patterns"
        },
        {
            'title': f"Transform Your {topic} Journey",
            'description': f"Implement proven strategies to accelerate your {topic} growth.",
            'suffix': "modern abstract design with flowing elements"
        },
        {
            'title': f"Elevate Your {topic} Skills",
            'description': f"Take your expertise to the next level with advanced techniques.",
            'suffix': "sophisticated color gradients and clean lines"
        },
        {
            'title': f"Dominate {topic} Strategies",
            'description': f"Learn industry-leading approaches that deliver results.",
            'suffix': "premium design with elegant simplicity"
        },
        {
            'title': f"Navigate {topic} Like a Pro",
            'description': f"Master the skills needed to excel in {topic}.",
            'suffix': "contemporary layout with subtle textures"
        },
        {
            'title': f"Revolutionize Your {topic} Approach",
            'description': f"Discover innovative methods that transform outcomes.",
            'suffix': "cutting-edge design with minimalist elements"
        },
        {
            'title': f"Conquer {topic} Challenges",
            'description': f"Overcome obstacles and achieve {topic} mastery.",
            'suffix': "bold and confident design aesthetic"
        }
    ]

    # Generate slides
    slides = []
    for i in range(min(slide_count, len(templates))):
        color_idx = i % len(colors)
        bg_color, font_color = colors[color_idx]

        template = templates[i]

        slides.append({
            'title': template['title'],
            'description': template['description'],
            'image_prompt': f"Minimal saystory {platform} background: {template['suffix']}, perfect for professional {topic} content, text-friendly design",
            'background_color': bg_color,
            'font_color': font_color
        })

    return slides

def create_fallback_slide(topic, slide_number, platform, style):
    """Create a single fallback slide with saystory-style content"""
    # Platform-specific color palettes
    color_palettes = {
        'instagram': [
            ('#405DE6', '#FFFFFF'),  # Instagram blue
            ('#8A2BE2', '#FFFFFF'),  # Blue violet
            ('#FF6B6B', '#FFFFFF'),  # Coral red
            ('#4ECDC4', '#000000'),  # Turquoise
            ('#FFD166', '#000000'),  # Yellow
        ],
        'linkedin': [
            ('#0A66C2', '#FFFFFF'),  # LinkedIn blue
            ('#333333', '#FFFFFF'),  # Dark gray
            ('#666666', '#FFFFFF'),  # Medium gray
            ('#999999', '#000000'),  # Light gray
            ('#CCCCCC', '#000000'),  # Very light gray
        ],
        'twitter': [
            ('#1DA1F2', '#FFFFFF'),  # Twitter blue
            ('#14171A', '#FFFFFF'),  # Dark
            ('#657786', '#FFFFFF'),  # Gray
            ('#AAB8C2', '#000000'),  # Light gray
            ('#E1E8ED', '#000000'),  # Very light gray
        ]
    }

    colors = color_palettes.get(platform, color_palettes['instagram'])
    bg_color, font_color = colors[(slide_number - 1) % len(colors)]

    # saystory-style titles - punchy and professional
    saystory_titles = [
        f"Unlock {topic} Success",
        f"Master {topic} Fundamentals",
        f"Transform Your {topic} Journey",
        f"Elevate Your {topic} Skills",
        f"Discover {topic} Excellence",
        f"Navigate {topic} Like a Pro",
        f"Accelerate {topic} Growth",
        f"Dominate {topic} Strategies",
        f"Revolutionize Your {topic} Approach",
        f"Conquer {topic} Challenges"
    ]

    # saystory-style descriptions - concise and impactful
    saystory_descriptions = [
        f"Discover the essential concepts that drive success in {topic}.",
        f"Master the core principles behind effective {topic} strategies.",
        f"Transform your approach with proven {topic} techniques.",
        f"Elevate your skills with professional {topic} insights.",
        f"Unlock excellence through strategic {topic} implementation.",
        f"Navigate complex {topic} challenges with confidence.",
        f"Accelerate your progress with expert {topic} guidance.",
        f"Dominate your field with advanced {topic} strategies.",
        f"Revolutionize your results with innovative {topic} methods.",
        f"Conquer obstacles and achieve {topic} mastery."
    ]

    title_idx = min(slide_number - 1, len(saystory_titles) - 1)
    desc_idx = min(slide_number - 1, len(saystory_descriptions) - 1)

    return {
        'title': saystory_titles[title_idx],
        'description': saystory_descriptions[desc_idx],
        'image_prompt': f"Minimal saystory {platform} background with soft {style} gradients, subtle abstract shapes, and clean professional design perfect for {topic} content",
        'background_color': bg_color,
        'font_color': font_color
    }

# ==================== CORE OPENAI FUNCTIONS ====================

@csrf_exempt
def generate_saystory_carousel(request):
    """
    Generate complete saystory-style carousel
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '').strip()
            platform = data.get('platform', 'instagram')
            style = data.get('style', 'modern')
            slide_count = int(data.get('slide_count', 5))
            profile_image_base64 = data.get('profile_image')
            brand_logo_base64 = data.get('brand_logo')
            profile_handle = data.get('profile_handle', '').strip()
            
            if not topic:
                return JsonResponse({'error': 'Topic is required'}, status=400)
            
            # Detect topic category for debugging
            detected_category = get_topic_category(topic)
            
            print(f"\n🎨 GENERATING saystory CAROUSEL")
            print(f"📌 Topic: {topic}")
            print(f"🏷️ Detected Category: {detected_category}")
            print(f"📱 Platform: {platform}")
            print(f"✨ Style: {style}")
            print(f"📊 Slides: {slide_count}")
            
            # Create project
            project = CarouselProject.objects.create(
                topic=topic,
                platform=platform,
                style=style,
                slide_count=slide_count,
                profile_handle=profile_handle
            )
            
            # Save branding images if provided
            if profile_image_base64:
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    
                    header, data = profile_image_base64.split(',')
                    file_content = ContentFile(base64.b64decode(data))
                    project.profile_image.save(f'profile_{project.id}.png', file_content)
                    print(f"✅ Profile image saved")
                except Exception as e:
                    print(f"⚠️ Error saving profile image: {e}")
            
            if brand_logo_base64:
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    
                    header, data = brand_logo_base64.split(',')
                    file_content = ContentFile(base64.b64decode(data))
                    project.brand_logo.save(f'logo_{project.id}.png', file_content)
                    print(f"✅ Brand logo saved")
                except Exception as e:
                    print(f"⚠️ Error saving brand logo: {e}")
            
            # Step 1: Generate slide content
            print(f"\n🤖 STEP 1: Generating slide content...")
            slides_content = generate_saystory_slides_content(topic, slide_count, platform, style)
            
            # Step 2: Create slides WITHOUT generating images (to avoid timeout)
            # Images will be generated one-by-one in the editor
            print(f"\n🎨 STEP 2: Creating slides (images will be generated in editor)...")
            slides_data = []
            
            for i, content in enumerate(slides_content):
                # Get platform dimensions
                saystorys_width, saystorys_height = get_platform_dimensions(platform)
                
                # Create the slide with content only (no image yet)
                slide = Slide.objects.create(
                    project=project,
                    slide_number=i + 1,
                    title=content['title'],
                    description=content['description'],
                    image_prompt=content['image_prompt'],
                    font_color=content['font_color'],
                    saystorys_width=saystorys_width,
                    saystorys_height=saystorys_height,
                    layout=content.get('layout', 'table')  # Use AI layout or default to Table
                )
                
                # Prepare response data (no image yet)
                slide_data = {
                    'id': slide.id,
                    'slide_number': slide.slide_number,
                    'title': slide.title,
                    'description': slide.description,
                    'image_prompt': slide.image_prompt,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color,
                    'generated_image': None
                }
                
                slides_data.append(slide_data)
                print(f"✅ Slide {i+1}: {slide.title[:40]}...")
            
            print(f"\n🎉 CAROUSEL CREATION COMPLETE!")
            print(f"✅ Created {len(slides_data)} slides")
            print(f"💡 Images will be generated in the editor")
            
            return JsonResponse({
                'success': True,
                'project_id': project.id,
                'slides': slides_data,
                'images_pending': True,  # Flag to indicate images need generation
                'message': f'Carousel created! Redirecting to editor to generate images...'
            })
            
        except Exception as e:
            print(f"❌ Error generating carousel: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'error': f'Failed to generate carousel: {str(e)}',
                'details': 'Please check your OpenAI API key and try again.'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ==================== GAMMA-STYLE CONTENT PREVIEW FUNCTIONS ====================

@csrf_exempt
def generate_content_previews(request):
    """
    Generate 3 different content preview variants for user selection.
    Returns content only (no images) with different tones: Professional, Creative, Bold
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '').strip()
            platform = data.get('platform', 'instagram')
            style = data.get('style', 'modern')
            slide_count = int(data.get('slide_count', 5))
            
            if not topic:
                return JsonResponse({'error': 'Topic is required'}, status=400)
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            print(f"\n🎨 GENERATING 3 CONTENT PREVIEWS")
            print(f"📌 Topic: {topic}")
            print(f"📱 Platform: {platform}")
            print(f"✨ Style: {style}")
            print(f"📊 Slides: {slide_count}")
            print(f"🔑 Session: {session_id}")
            
            # Define the 3 variant tones
            variants = [
                {"number": 1, "name": "Professional", "tone": "professional, authoritative, and business-focused"},
                {"number": 2, "name": "Creative", "tone": "creative, engaging, and storytelling-focused"},
                {"number": 3, "name": "Bold", "tone": "bold, punchy, and attention-grabbing with short impactful statements"},
            ]
            
            previews = []
            
            for variant in variants:
                print(f"\n📝 Generating variant {variant['number']}: {variant['name']}...")
                
                # Generate content with specific tone
                slides_content = generate_variant_content(
                    topic, slide_count, platform, style, variant['tone']
                )
                
                # Save to database
                preview = ContentPreview.objects.create(
                    session_id=session_id,
                    variant_number=variant['number'],
                    variant_name=variant['name'],
                    topic=topic,
                    platform=platform,
                    style=style,
                    slide_count=slide_count,
                    slides_json=json.dumps(slides_content)
                )
                
                previews.append({
                    'id': preview.id,
                    'variant_number': variant['number'],
                    'variant_name': variant['name'],
                    'slides': slides_content
                })
                
                print(f"✅ Variant {variant['number']} generated with {len(slides_content)} slides")
            
            print(f"\n🎉 ALL 3 PREVIEWS GENERATED!")
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'previews': previews,
                'message': 'Choose your preferred content style!'
            })
            
        except Exception as e:
            print(f"❌ Error generating previews: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'error': f'Failed to generate previews: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_variant_content(topic, slide_count, platform, style, tone):
    """Generate slide content with a specific tone/style variant"""
    try:
        prompt = f"""You are a world-class presentation designer and visual storyteller.
OBJECTIVE:
Transform a basic, generic slide plan into a visually stunning, premium, high-impact carousel about "{topic}" for {platform} (Style: {tone}).

The slides MUST NOT look:
- Stock
- Flat
- Generic
- Like default AI output

YOUR TASKS:
1. Write catchy, engaging headlines (Max 8 words).
2. Write support text that is short, powerful, and visually scannable (25-40 words).
3. Suggest a layout that feels modern and spacious.
4. Generate a high-quality image prompt for a premium illustration/background.

LAYOUT OPTIONS:
- "hero_split": Text left, image right (great for intros)
- "visual_focus": Image dominant, minimal text
- "card_grid": For listicles or multiple points
- "step_flow": Process or transformation
- "stat_focus": Big number + insight

Return a JSON array with exactly {slide_count} slides. Each slide must have:
- "title": Impactful headline
- "description": Scannable supporting text
- "image_prompt": Detailed visual description for premium SaaS/abstract illustration
- "background_color": Hex color (premium palette)
- "font_color": Hex color (high contrast)
- "layout": ONE of ["hero_split", "visual_focus", "card_grid", "step_flow", "stat_focus"]

Return ONLY valid JSON array."""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a senior visual designer and content strategist.
Transform the topic into premium, competitive carousel slides for a high-growth SaaS or Creator brand.

RULES:
1. CONTENT: Remove unnecessary words. Use short, punchy language.
   - Headline: Max 8 words, high impact.
   - Supporting: 25-40 words (2-3 punchy sentences). Add value but keep it clean.
2. HIERARCHY: Establish clear reading order.
3. TONE: {tone}
4. INTENT: Focus on clarity and value.

Return ONLY a valid JSON array. No explanations."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean response
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        slides = json.loads(content)
        
        # Ensure we have the right number of slides
        if isinstance(slides, list):
            return slides[:slide_count]
        
        return create_default_slides(topic, slide_count, platform, style)
        
    except Exception as e:
        print(f"⚠️ Error generating variant: {e}")
        return create_default_slides(topic, slide_count, platform, style)


@csrf_exempt
def select_preview_and_create_project(request):
    """
    Create a project from the selected preview variant.
    Assigns varied layouts to slides for visual diversity.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            variant_number = int(data.get('variant_number', 1))
            profile_image_base64 = data.get('profile_image')
            brand_logo_base64 = data.get('brand_logo')
            profile_handle = data.get('profile_handle', '').strip()
            
            if not session_id:
                return JsonResponse({'error': 'Session ID is required'}, status=400)
            
            # Get the selected preview
            try:
                preview = ContentPreview.objects.get(
                    session_id=session_id,
                    variant_number=variant_number
                )
            except ContentPreview.DoesNotExist:
                return JsonResponse({'error': 'Preview not found'}, status=404)
            
            print(f"\n🎯 CREATING PROJECT FROM PREVIEW")
            print(f"📌 Session: {session_id}")
            print(f"✨ Selected: Variant {variant_number} ({preview.variant_name})")
            
            # Mark as selected
            preview.is_selected = True
            preview.save()
            
            # Create project
            project = CarouselProject.objects.create(
                topic=preview.topic,
                platform=preview.platform,
                style=preview.style,
                slide_count=preview.slide_count,
                profile_handle=profile_handle
            )
            
            # Save branding images if provided
            if profile_image_base64:
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    header, img_data = profile_image_base64.split(',')
                    file_content = ContentFile(base64.b64decode(img_data))
                    project.profile_image.save(f'profile_{project.id}.png', file_content)
                except Exception as e:
                    print(f"⚠️ Error saving profile image: {e}")
            
            if brand_logo_base64:
                try:
                    import base64
                    from django.core.files.base import ContentFile
                    header, img_data = brand_logo_base64.split(',')
                    file_content = ContentFile(base64.b64decode(img_data))
                    project.brand_logo.save(f'logo_{project.id}.png', file_content)
                except Exception as e:
                    print(f"⚠️ Error saving brand logo: {e}")
            
            # Parse slides content
            slides_content = json.loads(preview.slides_json)
            
            # Layout assignment logic
            # Map new premium layouts to legacy frontend layouts
            def map_layout(layout_name, slide_num, total_slides):
                # Normalize
                layout_name = str(layout_name).lower().strip().replace(' ', '_')
                
                # Check for legacy matches first
                if layout_name in ['image-left', 'image-right', 'image-top', 'full-background', 'table']:
                    return layout_name
                    
                # Map new layouts to best frontend equivalent
                mapping = {
                    'hero_split': 'image-right',    # Text Left, Image Right
                    'visual_focus': 'full-background', # Image Dominant
                    'card_grid': 'image-left',     # Text Right (cards often on right/left)
                    'step_flow': 'image-right',    # Process flow
                    'stat_focus': 'image-top'      # Big number top/bottom
                }
                
                return mapping.get(layout_name, 'image-right') # Default fallback
            
            # Get platform dimensions
            saystorys_width, saystorys_height = get_platform_dimensions(preview.platform)

            # Create slides
            slides_data = []
            total_slides = len(slides_content)
            
            for i, content in enumerate(slides_content):
                # Get raw layout suggestion
                raw_layout = content.get('layout', 'hero_split')
                
                # Map to frontend supported layout
                layout_frontend = map_layout(raw_layout, i + 1, total_slides)
                
                slide = Slide.objects.create(
                    project=project,
                    slide_number=i + 1,
                    title=content.get('title', f'Slide {i+1}'),
                    description=content.get('description', ''),
                    image_prompt=content.get('image_prompt', ''),
                    background_color=content.get('background_color', '#405DE6'),
                    font_color=content.get('font_color', '#FFFFFF'),
                    saystorys_width=saystorys_width,
                    saystorys_height=saystorys_height,
                    layout=layout_frontend
                )
                
                slides_data.append({
                    'id': slide.id,
                    'slide_number': slide.slide_number,
                    'title': slide.title,
                    'description': slide.description,
                    'layout': slide.layout,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color
                })
                
                print(f"✅ Slide {i+1}: {slide.title[:30]}... (Layout: {slide.layout})")
            
            # Clean up old previews from this session
            ContentPreview.objects.filter(session_id=session_id).exclude(id=preview.id).delete()
            
            print(f"\n🎉 PROJECT CREATED!")
            print(f"📊 Project ID: {project.id}")
            print(f"📝 {len(slides_data)} slides with varied layouts")
            
            return JsonResponse({
                'success': True,
                'project_id': project.id,
                'slides': slides_data,
                'message': 'Project created! Redirecting to editor...'
            })
            
        except Exception as e:
            print(f"❌ Error creating project: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'error': f'Failed to create project: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_saystory_slides_content(topic, slide_count, platform, style):
    """
    Generate saystory-style slide content using OpenAI API
    Now with enhanced prompts for connected, premium carousel designs.
    """
    print(f"📝 Generating {slide_count} ENHANCED saystory slides...")
    
    try:
        # Use the enhanced content prompt from prompt_generator
        # Use the enhanced content prompt from prompt_generator
        # prompt = generate_slide_content_prompt(topic, slide_count, platform, style)
        
        # OVERRIDE with Premium Designer Prompt Logic directly
        # OVERRIDE with "World-Class" Premium Designer Prompt
        prompt = f"""You are a world-class presentation designer and visual storyteller.

OBJECTIVE:
Transform a basic, generic slide plan into a visually stunning, premium, high-impact carousel about "{topic}" for {platform} (Style: {style}).

The slides MUST NOT look:
- Stock
- Flat
- Generic
- Like default AI output

YOUR TASKS:
1. Rewrite content to be short, powerful, and visually scannable.
2. Create captions/descriptions max 40 words.
3. Suggest a layout that feels modern.
4. Generate a high-quality image prompt for premium illustration.

LAYOUT OPTIONS:
- "hero_split": Text left, image right
- "visual_focus": Image dominant, minimal text
- "card_grid": For listicles
- "step_flow": Process
- "stat_focus": Big number

Return a JSON array with exactly {slide_count} slides. Each slide must have:
- "title": Impactful headline (Max 8 words)
- "description": Scannable supporting text (25-40 words)
- "image_prompt": Detailed visual description for premium SaaS/abstract illustration
- "background_color": Hex code (premium palette)
- "font_color": Hex code (high contrast)
- "layout": ONE of ["hero_split", "visual_focus", "card_grid", "step_flow", "stat_focus"]

Return ONLY valid JSON array."""
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a senior visual designer and content strategist.
You create carousel content that goes VIRAL on Instagram and LinkedIn.

RULES:
1. BREVITY: Headlines < 8 words. Body text 25-40 words.
2. IMPACT: Use punchy, value-driven language.
3. VISUALS: Cohesive, flowing design elements.
4. LAYOUT INTELLIGENCE: Select the best layout for each slide.

Return ONLY a valid JSON array. No explanations."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content.strip()
        print(f"✅ Response received ({len(content)} chars)")
        
        # Clean the response
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        try:
            parsed = json.loads(content)
            
            slides_data = []
            if isinstance(parsed, list):
                slides_data = parsed
            elif isinstance(parsed, dict):
                # Look for slides in common keys
                for key in ['slides', 'content', 'data', 'carousel']:
                    if key in parsed and isinstance(parsed[key], list):
                        slides_data = parsed[key]
                        break
                
                # If dict has required keys, treat as one slide
                if not slides_data:
                    required_keys = ['title', 'description', 'image_prompt']
                    if all(key in parsed for key in required_keys):
                        slides_data = [parsed]
            
            # Validate and format slides
            validated_slides = []
            for i, slide in enumerate(slides_data[:slide_count]):
                try:
                    validated_slide = {
                        'title': str(slide.get('title', f"{topic} - Part {i+1}")).strip(),
                        'description': str(slide.get('description', f"Learn about {topic}.")).strip(),
                        'image_prompt': str(slide.get('image_prompt', 
                            f"saystory {platform} template with {style} style")).strip(),
                        'background_color': validate_hex_color(slide.get('background_color', '#405DE6')),
                        'font_color': validate_hex_color(slide.get('font_color', '#FFFFFF')),
                        'font_color': validate_hex_color(slide.get('font_color', '#FFFFFF')),
                        # Use new mapping logic for direct generation too
                        'layout': map_layout(slide.get('layout', 'hero_split'), i+1, slide_count)
                    }
                    validated_slides.append(validated_slide)
                except Exception as slide_error:
                    print(f"⚠️ Error processing slide {i+1}: {slide_error}")
                    validated_slides.append(create_fallback_slide(topic, i+1, platform, style))
            
            # Helper function for mapping (duplicated from select_preview but necessary here)
            def map_layout(layout_name, slide_num, total_slides):
                layout_name = str(layout_name).lower().strip().replace(' ', '_')
                if layout_name in ['image-left', 'image-right', 'image-top', 'full-background', 'table']:
                    return layout_name
                mapping = {
                    'hero_split': 'image-right',
                    'visual_focus': 'full-background',
                    'card_grid': 'image-left',
                    'step_flow': 'image-right',
                    'stat_focus': 'image-top'
                }
                return mapping.get(layout_name, 'image-right')
            
            # Ensure we have requested number of slides
            while len(validated_slides) < slide_count:
                i = len(validated_slides)
                validated_slides.append(create_fallback_slide(topic, i+1, platform, style))
            
            print(f"✅ Generated {len(validated_slides)} slides")
            return validated_slides
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Raw content: {content[:200]}...")
            return create_default_slides(topic, slide_count, platform, style)
            
    except Exception as e:
        print(f"❌ OpenAI API error: {str(e)}")
        return create_default_slides(topic, slide_count, platform, style)


def generate_saystory_image(prompt, platform, style, slide_id, bg_color=None, profile_image_path=None, brand_logo_path=None, slide_number=1, total_slides=1, project_id=None, topic=None, brand_colors=None, slide_title=None, slide_description=None):
    """
    Generate saystory-style background image using GPT Image API
    Now with enhanced prompts for connected, premium carousel designs.
    
    IMPORTANT: The original slide image_prompt is the PRIMARY instruction.
    The enhanced prompt provides styling context, but the image_prompt content takes priority.
    """
    print(f"🎨 Generating ENHANCED saystory image: {prompt[:50]}...")
    print(f"📝 Original image_prompt will be PRIMARY focus")
    
    # Use the enhanced prompt generator for premium, connected designs
    if topic:
        # Get styling context from enhanced prompt generator
        styling_context = generate_enhanced_image_prompt(
            topic=topic,
            slide_number=slide_number,
            total_slides=total_slides,
            platform=platform,
            style=style,
            brand_colors=brand_colors,
            project_id=project_id,
            slide_title=slide_title,
            slide_description=slide_description
        )
        
        # CRITICAL FIX: Put original image_prompt as PRIMARY at the TOP
        # The original prompt (e.g., "diverse people holding hands") should be the MAIN subject
        saystory_prompt = f"""🎯 PRIMARY IMAGE INSTRUCTION - THIS IS WHAT TO DRAW:
═══════════════════════════════════════════════════════════════
{prompt}
═══════════════════════════════════════════════════════════════

⚠️ CRITICAL: The above description is the MAIN SUBJECT of this image.
Draw EXACTLY what is described above. Do NOT replace it with generic objects or icons.

📐 STYLING & LAYOUT CONTEXT (apply to the main subject above):
- Platform: {platform.upper()} carousel slide ({slide_number} of {total_slides})
- Keep center 40-50% clear for text overlay
- Use premium, professional styling
- Soft pastel colors with modern gradients

{styling_context[-1500:] if len(styling_context) > 1500 else styling_context}"""
    else:
        # Fallback to enhanced but non-connected prompt
        saystory_prompt = f"""Create a STUNNING, ULTRA-PREMIUM carousel slide background that makes viewers say "WOW".

THEME: {prompt}
PLATFORM: {platform.upper()} carousel slide
STYLE: {style}

COLOR PALETTE:
- Use bright but SOFT pastel colors like light coral pink (#FFB5BA), peach cream (#FFE5B4), light lavender (#D4B5FF)
- Create beautiful gradient transitions between colors
- Add subtle accent highlights with vibrant colors

VISUAL ELEMENTS:
- Flowing gradient waves or curved design elements
- Subtle glass-morphism effects with frosted overlays
- Delicate geometric accents at edges
- Soft shadows and depth for premium feel
- Modern, sleek aesthetic

CRITICAL REQUIREMENTS:
1. PREMIUM QUALITY - High-end design agency look
2. TEXT-FRIENDLY - Keep center 40-50% clear for text overlay
3. BRIGHT BUT SOFT - Pastel colors prominently but elegantly
4. MODERN - Glass morphism, soft shadows, subtle depth
5. UNIQUE - Not generic stock photo look

AVOID:
- Plain solid backgrounds
- Cluttered busy designs
- Generic stock aesthetics
- Hard edges without softness"""
    
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=saystory_prompt[:4000],
            size="1024x1024",
            quality="auto",
            n=1
        )
        
        # The image API may return either a URL or base64 data depending on model/version.
        image_entry = response.data[0]
        image_url = None
        image_b64 = None
        try:
            # Try dict-like access first
            if isinstance(image_entry, dict):
                image_url = image_entry.get('url')
                image_b64 = image_entry.get('b64_json') or image_entry.get('b64')
            else:
                # Object with attributes
                image_url = getattr(image_entry, 'url', None)
                image_b64 = getattr(image_entry, 'b64_json', None) or getattr(image_entry, 'b64', None)
        except Exception:
            image_url = None
            image_b64 = None

        # Generate filename and path
        filename = f"saystory_slide_{slide_id}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if image_url:
            print(f"✅ GPT image generated (URL)")
            # Download image
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
        elif image_b64:
            print(f"✅ GPT image generated (base64)")
            import base64
            try:
                image_bytes = base64.b64decode(image_b64)
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
            except Exception as e:
                print(f"❌ Error decoding base64 image: {e}")
                return None
        else:
            print(f"❌ Error: image response did not contain URL or base64 data: {response}")
            return None

        # If a background color was requested, composite/tint the image
        try:
            if bg_color:
                # Normalize color
                bg_color = str(bg_color).strip()
                if not bg_color.startswith('#'):
                    bg_color = '#' + bg_color
                # Open saved image
                img = Image.open(filepath).convert('RGBA')

                # Convert hex to RGB tuple
                try:
                    r = int(bg_color[1:3], 16)
                    g = int(bg_color[3:5], 16)
                    b = int(bg_color[5:7], 16)
                except Exception:
                    r, g, b = (255, 255, 255)

                bg = Image.new('RGBA', img.size, (r, g, b, 255))

                # Detect transparency
                has_transparency = False
                try:
                    a_extrema = img.getchannel('A').getextrema()
                    if a_extrema and a_extrema[0] < 255:
                        has_transparency = True
                except Exception:
                    has_transparency = False

                if has_transparency:
                    # If transparent areas exist, place image over solid background
                    result = Image.alpha_composite(bg, img)
                else:
                    # Otherwise, gently blend the background color to tint the image
                    result = Image.blend(img, bg, alpha=0.15)

                # Save composited image (overwrite)
                result.convert('RGBA').save(filepath, format='PNG')

        except Exception as proc_err:
            print(f"⚠️ Warning processing background color: {proc_err}")

        # BRANDING COMPOSITING DISABLED - branding is now handled as frontend overlay only
        # Profile images and logos will NOT be baked into the generated image files
        # They appear as separate overlay elements on the canvas (renderBrandingOverlay)
        #
        # try:
        #     if profile_image_path or brand_logo_path:
        #         from PIL import ImageDraw, ImageFont
        #         img = Image.open(filepath).convert('RGBA')
        #         
        #         # Add profile image (LEFT BOTTOM corner, small)
        #         if profile_image_path and os.path.exists(profile_image_path):
        #             profile = Image.open(profile_image_path).convert('RGBA')
        #             profile_size = 60  # Small size for bottom-left
        #             profile.thumbnail((profile_size, profile_size), Image.Resampling.LANCZOS)
        #             
        #             # Position: bottom-left with padding
        #             pos_x = 15  # Left padding
        #             pos_y = img.height - profile_size - 15  # Bottom padding
        #             img.paste(profile, (pos_x, pos_y), profile)
        #             print(f"✅ Profile image embedded (bottom-left)")
        #         
        #         # Add brand logo (RIGHT BOTTOM corner)
        #         if brand_logo_path and os.path.exists(brand_logo_path):
        #             logo = Image.open(brand_logo_path).convert('RGBA')
        #             logo_size = 70  # Slightly larger for brand logo
        #             logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        #             
        #             # Position: bottom-right with padding
        #             pos_x = img.width - logo_size - 15  # Right padding
        #             pos_y = img.height - logo_size - 15  # Bottom padding
        #             img.paste(logo, (pos_x, pos_y), logo)
        #             print(f"✅ Brand logo embedded (bottom-right)")
        #         
        #         # Save final image
        #         img.convert('RGB').save(filepath, format='PNG')
        # 
        # except Exception as brand_err:
        #     print(f"⚠️ Warning adding branding: {brand_err}")

        print(f"💾 Image saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error generating image: {str(e)}")
        return None


# ==================== EDITOR FUNCTIONS ====================

@csrf_exempt
def generate_slide_image(request):
    """
    Generate and apply saystory image to specific slide
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slide_id = data.get('slide_id')
            prompt = data.get('prompt', '').strip()
            
            if not slide_id:
                return JsonResponse({'error': 'Slide ID is required'}, status=400)
            
            if not prompt:
                return JsonResponse({'error': 'Image prompt is required'}, status=400)
            
            slide = Slide.objects.get(id=slide_id)
            project = slide.project
            
            print(f"\n🖼️ GENERATING saystory IMAGE FOR SLIDE")
            print(f"📝 Slide: {slide.title}")
            print(f"🎨 Prompt: {prompt}")
            
            # Get total slides for connected design context
            total_slides = Slide.objects.filter(project=project).count()
            
            # Generate saystory image WITHOUT branding (branding is added as overlay in frontend)
            image_filename = generate_saystory_image(
                prompt,
                project.platform,
                project.style,
                slide_id,
                bg_color=slide.background_color,
                profile_image_path=None,  # Branding now handled as overlay in frontend
                brand_logo_path=None,      # Branding now handled as overlay in frontend
                slide_number=slide.slide_number,
                total_slides=total_slides,
                project_id=project.id,
                topic=project.topic
            )
            
            if image_filename:
                # Update slide
                slide.generated_image = image_filename
                slide.image_prompt = prompt
                slide.save()
                
                return JsonResponse({
                    'success': True,
                    'image_url': f"{settings.MEDIA_URL}{image_filename}",
                    'filename': image_filename,
                    'slide_id': slide.id,
                    'message': 'saystory image generated and applied successfully!'
                })
            else:
                return JsonResponse({
                    'error': 'Failed to generate image'
                }, status=500)
                
        except Slide.DoesNotExist:
            return JsonResponse({'error': 'Slide not found'}, status=404)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def regenerate_slide_content(request):
    """
    Regenerate slide content with OpenAI
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slide_id = data.get('slide_id')
            
            if not slide_id:
                return JsonResponse({'error': 'Slide ID is required'}, status=400)
            
            slide = Slide.objects.get(id=slide_id)
            project = slide.project
            
            print(f"\n🔄 REGENERATING SLIDE CONTENT")
            print(f"📝 Slide: {slide.title}")
            
            # Generate new content for this slide
            prompt = f"""Create new content for one carousel slide about "{project.topic}" for {project.platform}.

Current slide: {slide.title} - {slide.description}

Return a JSON object with:
- title: New engaging title
- description: New informative description
- image_prompt: New prompt for saystory background
- background_color: Hex color
- font_color: Hex color

Make it fresh and suitable for {project.platform} saystory template."""
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Return ONLY a valid JSON object."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content).strip()
            
            new_data = json.loads(content)
            
            # Update slide
            slide.title = new_data.get('title', slide.title)
            slide.description = new_data.get('description', slide.description)
            slide.image_prompt = new_data.get('image_prompt', slide.image_prompt)
            slide.background_color = validate_hex_color(new_data.get('background_color', slide.background_color))
            slide.font_color = validate_hex_color(new_data.get('font_color', slide.font_color))
            slide.save()
            
            print(f"✅ Slide regenerated: {slide.title}")
            
            return JsonResponse({
                'success': True,
                'slide': {
                    'id': slide.id,
                    'title': slide.title,
                    'description': slide.description,
                    'image_prompt': slide.image_prompt,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color,
                    'generated_image': slide.generated_image,
                    'generated_image_url': f"{settings.MEDIA_URL}{slide.generated_image}" if slide.generated_image else None
                },
                'message': 'Slide content regenerated successfully'
            })
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_slide(request):
    """
    Update slide content and design
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slide_id = data.get('slide_id')
            slide_data = data.get('slide_data', {})
            
            if not slide_id:
                return JsonResponse({'error': 'Slide ID is required'}, status=400)
            
            slide = Slide.objects.get(id=slide_id)
            
            # Update fields
            if 'title' in slide_data:
                slide.title = slide_data['title']
            if 'description' in slide_data:
                slide.description = slide_data['description']
            if 'image_prompt' in slide_data:
                slide.image_prompt = slide_data['image_prompt']
            if 'background_color' in slide_data:
                slide.background_color = validate_hex_color(slide_data['background_color'])
            if 'font_color' in slide_data:
                slide.font_color = validate_hex_color(slide_data['font_color'])
            if 'saystorys_width' in slide_data:
                slide.saystorys_width = int(slide_data['saystorys_width'])
            if 'saystorys_height' in slide_data:
                slide.saystorys_height = int(slide_data['saystorys_height'])
                
            # Text Positioning
            if 'title_x' in slide_data and slide_data['title_x'] is not None: 
                slide.title_x = int(float(slide_data['title_x']))
            if 'title_y' in slide_data and slide_data['title_y'] is not None: 
                slide.title_y = int(float(slide_data['title_y']))
            if 'description_x' in slide_data and slide_data['description_x'] is not None: 
                slide.description_x = int(float(slide_data['description_x']))
            if 'description_y' in slide_data and slide_data['description_y'] is not None: 
                slide.description_y = int(float(slide_data['description_y']))
            if 'extra_text_x' in slide_data and slide_data['extra_text_x'] is not None: 
                slide.extra_text_x = int(float(slide_data['extra_text_x']))
            if 'extra_text_y' in slide_data and slide_data['extra_text_y'] is not None: 
                slide.extra_text_y = int(float(slide_data['extra_text_y']))
            
            # Additional Fields
            if 'extra_text' in slide_data:
                slide.extra_text = slide_data['extra_text']
            
            if 'text_styles' in slide_data:
                # Ensure it's stored as string
                styles = slide_data['text_styles']
                if isinstance(styles, dict):
                    slide.text_styles = json.dumps(styles)
                else:
                    slide.text_styles = styles
            
            if 'extra_texts' in slide_data:
                # Ensure it's stored as string
                eterms = slide_data['extra_texts']
                if isinstance(eterms, list):
                    slide.extra_texts = json.dumps(eterms)
                else:
                    slide.extra_texts = eterms

            if 'user_images' in slide_data:
                # Ensure it's stored as string
                uimages = slide_data['user_images']
                if isinstance(uimages, list):
                    slide.user_images = json.dumps(uimages)
                else:
                    slide.user_images = uimages



            slide.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Slide updated successfully',
                'slide': {
                    'id': slide.id,
                    'title': slide.title,
                    'description': slide.description,
                    'image_prompt': slide.image_prompt,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color,
                    'saystorys_width': slide.saystorys_width,
                    'saystorys_height': slide.saystorys_height,
                    'title_x': slide.title_x,
                    'title_y': slide.title_y,
                    'description_x': slide.description_x,
                    'description_y': slide.description_y,
                    'extra_text': slide.extra_text,
                    'extra_text_x': slide.extra_text_x,
                    'extra_text_y': slide.extra_text_y
                }
            })
            
        except Slide.DoesNotExist:
            return JsonResponse({'error': 'Slide not found'}, status=404)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def generate_all_images(request):
    """
    Generate images for all slides in a project
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            
            if not project_id:
                return JsonResponse({'error': 'Project ID is required'}, status=400)
            
            project = CarouselProject.objects.get(id=project_id)
            slides = Slide.objects.filter(project=project).order_by('slide_number')
            
            print(f"\n🖼️ GENERATING IMAGES FOR ALL SLIDES")
            print(f"📊 Project: {project.topic}")
            print(f"📈 Total slides: {slides.count()}")
            
            generated_count = 0
            failed_count = 0
            
            for slide in slides:
                try:
                    # Skip if already has image
                    if slide.generated_image:
                        print(f"⏩ Slide {slide.slide_number}: Already has image")
                        continue
                    
                    print(f"🎨 Generating image for Slide {slide.slide_number}...")
                    
                    # Use enhanced prompts with slide connectivity AND per-slide analysis
                    image_filename = generate_saystory_image(
                        slide.image_prompt,
                        project.platform,
                        project.style,
                        slide.id,
                        bg_color=slide.background_color,
                        profile_image_path=project.profile_image.path if project.profile_image else None,
                        brand_logo_path=project.brand_logo.path if project.brand_logo else None,
                        slide_number=slide.slide_number,
                        total_slides=slides.count(),
                        project_id=project.id,
                        topic=project.topic,
                        slide_title=slide.title,  # NEW: Pass slide title for Layer 2 analysis
                        slide_description=slide.description  # NEW: Pass slide description for Layer 2 analysis
                    )
                    
                    if image_filename:
                        slide.generated_image = image_filename
                        slide.save()
                        generated_count += 1
                        print(f"✅ Image generated for Slide {slide.slide_number}")
                    else:
                        failed_count += 1
                        print(f"❌ Failed to generate image for Slide {slide.slide_number}")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Error for Slide {slide.slide_number}: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'generated': generated_count,
                'failed': failed_count,
                'total': slides.count(),
                'message': f'Generated {generated_count} images, {failed_count} failed'
            })
            
        except CarouselProject.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_project_slides(request, project_id):
    """Get all slides for a project"""
    try:
        project = CarouselProject.objects.get(id=project_id)
        slides = Slide.objects.filter(project=project).order_by('slide_number')
        
        slides_data = []
        for slide in slides:
            slide_dict = {
                'id': slide.id,
                'slide_number': slide.slide_number,
                'title': slide.title,
                'description': slide.description,
                'image_prompt': slide.image_prompt,
                'background_color': slide.background_color,
                'font_color': slide.font_color,
                'saystorys_width': slide.saystorys_width,
                'saystorys_height': slide.saystorys_height,
                'generated_image': slide.generated_image,
                'text_styles': slide.text_styles,
                'extra_texts': slide.extra_texts,
                'user_images': slide.user_images,
                'title_x': slide.title_x,
                'title_y': slide.title_y,
                'description_x': slide.description_x,
                'description_y': slide.description_y,
                'layout': slide.layout  # Include layout for frontend rendering
            }
            
            if slide.generated_image:
                slide_dict['generated_image_url'] = f"{settings.MEDIA_URL}{slide.generated_image}"
            
            slides_data.append(slide_dict)
        
        # Include project data with branding info
        project_data = {
            'id': project.id,
            'profile_handle': project.profile_handle or '',
            'profile_image_url': project.profile_image.url if project.profile_image else None,
            'brand_logo_url': project.brand_logo.url if project.brand_logo else None,
            'topic': project.topic,
            'platform': project.platform,
            'style': project.style
        }
        
        return JsonResponse({
            'success': True,
            'project_id': project.id,
            'project': project_data,
            'slides': slides_data
        })
        
    except CarouselProject.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

@csrf_exempt
def test_openai(request):
    """Simple test of OpenAI API"""
    if request.method == 'POST':
        try:
            print("\n🧪 TESTING OPENAI CONNECTION")
            
            # Check API key
            if not settings.OPENAI_API_KEY:
                return JsonResponse({
                    'success': False,
                    'error': 'OPENAI_API_KEY not set in settings.py'
                }, status=400)
            
            print(f"📋 API Key: {settings.OPENAI_API_KEY[:10]}...")
            
            # Test GPT-3.5
            print(f"\n🤖 Testing GPT-4.1-mini...")
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": "Say 'saystory Carousel Generator is working!'"}
                ],
                max_tokens=50
            )
            
            gpt_response = response.choices[0].message.content
            print(f"✅ GPT-3.5 Test Successful!")
            print(f"📄 Response: {gpt_response}")
            
            return JsonResponse({
                'success': True,
                'gpt_response': gpt_response,
                'message': 'OpenAI API is working!'
            })
            
        except Exception as e:
            print(f"❌ Test Failed: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def debug_generate(request):
    """
    Debug endpoint to test slide generation
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', 'Test Topic')
            slide_count = int(data.get('slide_count', 3))
            
            print(f"\n🔧 DEBUG GENERATION")
            print(f"📌 Topic: {topic}")
            
            # Test with simple prompt
            prompt = f"Create {slide_count} slides about {topic}. Return JSON array."
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Return JSON array."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            print(f"✅ Debug response received")
            
            return JsonResponse({
                'success': True,
                'raw_response': content,
                'model_used': 'gpt-4.1-mini'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def generate_and_apply_image(request):
    """
    Generate an image from a user description and apply it to the slide.
    Request JSON: { slide_id, description }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slide_id = data.get('slide_id')
            description = data.get('description', '').strip()

            if not slide_id:
                return JsonResponse({'error': 'Slide ID is required'}, status=400)
            if not description:
                return JsonResponse({'error': 'Description is required'}, status=400)

            slide = Slide.objects.get(id=slide_id)
            project = slide.project

            print(f"\n🖼️ GENERATE AND APPLY IMAGE")
            print(f"📝 Slide: {slide.title}")
            print(f"🧾 Description: {description}")

            # Build a saystory-friendly prompt from user description
            prompt = f"saystory-style minimal background for: {description}. Make it clean, leave a clear center area for text, flat/vector style, subtle colors."
            
            # Get total slides for context
            total_slides = Slide.objects.filter(project=project).count()

            image_filename = generate_saystory_image(
                prompt,
                project.platform,
                project.style,
                slide.id,
                bg_color=slide.background_color,
                profile_image_path=project.profile_image.path if project.profile_image else None,
                brand_logo_path=project.brand_logo.path if project.brand_logo else None,
                slide_number=slide.slide_number,
                total_slides=total_slides,
                project_id=project.id,
                topic=project.topic
            )

            if image_filename:
                slide.generated_image = image_filename
                slide.image_prompt = description
                slide.save()

                return JsonResponse({
                    'success': True,
                    'image_url': f"{settings.MEDIA_URL}{image_filename}",
                    'filename': image_filename,
                    'slide_id': slide.id,
                    'message': 'Image generated from description and applied to slide.'
                })
            else:
                return JsonResponse({'error': 'Failed to generate image'}, status=500)

        except Slide.DoesNotExist:
            return JsonResponse({'error': 'Slide not found'}, status=404)
        except Exception as e:
            print(f"❌ Error in generate_and_apply_image: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_slide(request):
    """
    Add a new slide to a project with default values
    Request JSON: { project_id }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')

            if not project_id:
                return JsonResponse({'error': 'Project ID is required'}, status=400)

            project = CarouselProject.objects.get(id=project_id)

            # Get the next slide number
            last_slide = Slide.objects.filter(project=project).order_by('-slide_number').first()
            next_slide_number = (last_slide.slide_number + 1) if last_slide else 1

            # Get platform dimensions
            saystorys_width, saystorys_height = get_platform_dimensions(project.platform)

            # Create new slide with default values
            slide = Slide.objects.create(
                project=project,
                slide_number=next_slide_number,
                title=f"New Slide {next_slide_number}",
                description="Add your content here",
                extra_text="",
                image_prompt="",
                background_color="#FFFFFF",
                font_color="#000000",
                saystorys_width=saystorys_width,
                saystorys_height=saystorys_height
            )

            print(f"✅ New slide added: {slide.title} (ID: {slide.id})")

            return JsonResponse({
                'success': True,
                'slide': {
                    'id': slide.id,
                    'slide_number': slide.slide_number,
                    'title': slide.title,
                    'description': slide.description,
                    'extra_text': slide.extra_text,
                    'image_prompt': slide.image_prompt,
                    'background_color': slide.background_color,
                    'font_color': slide.font_color,
                    'saystorys_width': slide.saystorys_width,
                    'saystorys_height': slide.saystorys_height,
                    'generated_image': slide.generated_image
                },
                'message': 'New slide added successfully'
            })

        except CarouselProject.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        except Exception as e:
            print(f"❌ Error adding slide: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_slide(request):
    """
    Delete a slide from a project and update slide numbers
    Request JSON: { slide_id }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slide_id = data.get('slide_id')

            if not slide_id:
                return JsonResponse({'error': 'Slide ID is required'}, status=400)

            slide = Slide.objects.get(id=slide_id)
            project = slide.project
            slide_number = slide.slide_number

            # Delete the slide
            slide.delete()

            # Update slide numbers for remaining slides
            slides_to_update = Slide.objects.filter(
                project=project,
                slide_number__gt=slide_number
            ).order_by('slide_number')

            for s in slides_to_update:
                s.slide_number -= 1
                s.save()

            print(f"✅ Slide {slide_number} deleted from project {project.id}")

            return JsonResponse({
                'success': True,
                'message': 'Slide deleted successfully',
                'deleted_slide_number': slide_number
            })

        except Slide.DoesNotExist:
            return JsonResponse({'error': 'Slide not found'}, status=404)
        except Exception as e:
            print(f"❌ Error deleting slide: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
@require_http_methods(["POST"])
def adapt_slide_content(request):
    """Adapt slide content to a specific layout style using AI"""
    try:
        data = json.loads(request.body)
        slide_id = data.get('slide_id')
        layout_style = data.get('layout_style')
        
        if not slide_id or not layout_style:
            return JsonResponse({'success': False, 'error': 'Missing slide_id or layout_style'}, status=400)
            
        slide = Slide.objects.get(id=slide_id)
        project = slide.project
        
        # User defined prompt for adaptation
        prompt = f"""You are a world-class presentation designer and UX copywriter.

CONTEXT:
- The user is on an EDITOR page.
- A slide layout has already been SELECTED by the user.
- Your job is to ADAPT the slide title and description to perfectly fit the selected layout.
- Each layout has a unique visual personality and content structure.
- The output will be rendered directly in the editor.

IMPORTANT:
- DO NOT change the selected layout.
- DO NOT generate a new layout.
- ONLY adapt content (title + description) to match the layout style.
- Content must feel intentional and designer-crafted.

INPUT:
Topic:
"{project.topic}"

Selected Layout:
"{layout_style}"

AVAILABLE LAYOUTS & CONTENT BEHAVIOR:

1. Split Screen
- Bold headline
- Short, confident description
- Strong contrast between left and right
- Ideal for value propositions

2. Creative Chaos
- Experimental headline
- Punchy, fragmented text
- High energy, playful tone
- Works best with short phrases

3. Corporate Pro
- Professional, polished headline
- Clear, business-focused description
- Formal but modern tone

4. Minimal Clean
- Very short headline
- Minimal description
- Calm, elegant, whitespace-friendly

5. Gradient Flow
- Inspirational headline
- Smooth, flowing description
- Modern SaaS marketing tone

6. Neon Glow
- Bold, futuristic headline
- High-impact, confident description
- Tech / cyber / innovation tone

7. Geometric Pro
- Structured headline
- Sharp, concise description
- Precision and clarity

8. Magazine Style
- Editorial-style headline
- Story-driven but short description
- Premium, lifestyle or thought-leadership tone

9. Card Layout
- Headline broken into key ideas
- Modular, scannable description
- Each line should feel like a card

10. Sidebar Focus
- Strong headline
- Supporting description aligned to sidebar narrative
- Gamma-style storytelling

TASKS:
1. Adapt the TITLE to match the selected layout style.
2. Adapt the DESCRIPTION to match the selected layout structure.
3. Determine the best STRUCTURAL LAYOUT (e.g., 'hero_split', 'visual_focus') that fits this style.
4. Ensure text length fits the layout visually.
5. Maintain clarity, impact, and visual harmony.

CONTENT RULES:
- No long paragraphs
- Max 8–12 words per line
- Layout determines tone and structure
- Use power words, clarity, and rhythm
- Less text, more meaning
- CURRENT CONTENT TO ADAPT:
  Title: "{slide.title}"
  Description: "{slide.description}"

Return JSON:
{{
  "title": "...",
  "description": "...",
  "structural_layout": "..." (One of: 'hero_split', 'visual_focus', 'card_grid', 'step_flow', 'stat_focus')
}}"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a specialized UX copywriter and layout designer. Return strictly JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = json.loads(response.choices[0].message.content)
        
        # MAPPING LOGIC (Same as in generate_variant_content)
        def map_layout(layout_name):
            layout_name = str(layout_name).lower().strip().replace(' ', '_')
            if layout_name in ['image-left', 'image-right', 'image-top', 'full-background', 'table']:
                return layout_name
            mapping = {
                'hero_split': 'image-right',
                'visual_focus': 'full-background',
                'card_grid': 'image-left',
                'step_flow': 'image-right',
                'stat_focus': 'image-top'
            }
            return mapping.get(layout_name, 'image-right')

        # Update slide
        slide.title = content.get('title', slide.title)
        slide.description = content.get('description', slide.description)
        
        # Update layout if suggested
        raw_layout = content.get('structural_layout')
        if raw_layout:
             slide.layout = map_layout(raw_layout)

        slide.save()
        
        return JsonResponse({
            'success': True,
            'title': slide.title,
            'description': slide.description,
            'layout': slide.layout
        })

    except Slide.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Slide not found'}, status=404)
    except Exception as e:
        print(f"Error adapting content: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
