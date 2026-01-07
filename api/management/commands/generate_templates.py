# api/management/commands/generate_templates.py
"""
Django management command to generate and store carousel templates.
Run: python manage.py generate_templates
"""
import json
import os
import base64
import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from api.models import CarouselTemplate
from api.prompt_generator import (
    TOPIC_COLOR_PALETTES,
    generate_enhanced_image_prompt,
    get_topic_category
)

# OpenAI API for image generation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Command(BaseCommand):
    help = 'Generate and store carousel templates for the template gallery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Generate templates for a specific category only',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of templates per category (default: 1)',
        )
        parser.add_argument(
            '--slides',
            type=int,
            default=5,
            help='Number of slides per template (default: 5)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without actually generating',
        )

    def handle(self, *args, **options):
        category_filter = options.get('category')
        templates_per_category = options['count']
        slides_per_template = options['slides']
        dry_run = options['dry_run']
        
        # Template definitions for each category
        TEMPLATE_DEFINITIONS = {
            'business': [
                {'name': 'Startup Tips', 'topic': 'Essential startup tips for first-time entrepreneurs'},
                {'name': 'Productivity Hacks', 'topic': 'Top productivity hacks for busy professionals'},
                {'name': 'Leadership Skills', 'topic': 'Key leadership skills every manager needs'},
            ],
            'technology': [
                {'name': 'AI Trends', 'topic': 'Latest AI trends shaping the future of technology'},
                {'name': 'Tech Tips', 'topic': 'Essential tech tips for everyday productivity'},
                {'name': 'Coding Basics', 'topic': 'Getting started with programming and coding'},
            ],
            'health': [
                {'name': 'Fitness Journey', 'topic': 'Starting your fitness journey the right way'},
                {'name': 'Healthy Habits', 'topic': 'Daily healthy habits for a better lifestyle'},
                {'name': 'Mental Wellness', 'topic': 'Simple mental wellness practices for stress relief'},
            ],
            'lifestyle': [
                {'name': 'Morning Routine', 'topic': 'Creating the perfect morning routine for success'},
                {'name': 'Self Care', 'topic': 'Essential self-care tips for busy people'},
                {'name': 'Home Organization', 'topic': 'Organizing your home for a clutter-free life'},
            ],
            'education': [
                {'name': 'Study Tips', 'topic': 'Effective study techniques for students'},
                {'name': 'Learning Skills', 'topic': 'How to learn any skill faster and better'},
                {'name': 'Online Learning', 'topic': 'Making the most of online learning platforms'},
            ],
            'creative': [
                {'name': 'Design Basics', 'topic': 'Essential graphic design principles for beginners'},
                {'name': 'Creative Process', 'topic': 'Unlocking your creative potential'},
                {'name': 'Art Inspiration', 'topic': 'Finding inspiration for your creative projects'},
            ],
            'travel': [
                {'name': 'Travel Planning', 'topic': 'Planning your dream vacation step by step'},
                {'name': 'Budget Travel', 'topic': 'How to travel on a budget without compromising'},
                {'name': 'Travel Tips', 'topic': 'Essential travel tips for first-time travelers'},
            ],
            'finance': [
                {'name': 'Investing 101', 'topic': 'Getting started with investing for beginners'},
                {'name': 'Money Management', 'topic': 'Smart money management tips for everyone'},
                {'name': 'Saving Strategies', 'topic': 'Effective saving strategies to build wealth'},
            ],
            'fashion': [
                {'name': 'Style Guide', 'topic': 'Building a timeless wardrobe on any budget'},
                {'name': 'Fashion Trends', 'topic': 'Current fashion trends you need to know'},
                {'name': 'Personal Style', 'topic': 'Discovering and developing your personal style'},
            ],
            'food': [
                {'name': 'Healthy Recipes', 'topic': 'Quick and healthy recipes for busy weekdays'},
                {'name': 'Cooking Tips', 'topic': 'Essential cooking tips for home chefs'},
                {'name': 'Meal Planning', 'topic': 'Mastering weekly meal planning like a pro'},
            ],
        }
        
        # Filter categories if specified
        categories = [category_filter] if category_filter else TEMPLATE_DEFINITIONS.keys()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n🎨 Template Generator\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'Categories: {len(list(categories))}\n'
            f'Templates per category: {templates_per_category}\n'
            f'Slides per template: {slides_per_template}\n'
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No templates will be generated\n'))
        
        total_generated = 0
        
        for category in categories:
            if category not in TEMPLATE_DEFINITIONS:
                self.stdout.write(self.style.ERROR(f'Unknown category: {category}'))
                continue
            
            templates = TEMPLATE_DEFINITIONS[category][:templates_per_category]
            
            self.stdout.write(f'\n📁 Category: {category.upper()}')
            
            for template_def in templates:
                self.stdout.write(f'  📝 {template_def["name"]}')
                
                if dry_run:
                    self.stdout.write(f'     Topic: {template_def["topic"]}')
                    self.stdout.write(f'     Would generate {slides_per_template} slides')
                    continue
                
                try:
                    template = self.generate_template(
                        name=template_def['name'],
                        topic=template_def['topic'],
                        category=category,
                        slide_count=slides_per_template
                    )
                    if template:
                        total_generated += 1
                        self.stdout.write(self.style.SUCCESS(f'     ✅ Generated successfully'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     ❌ Error: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
            f'✅ Total templates generated: {total_generated}\n'
        ))

    def generate_template(self, name, topic, category, slide_count=5):
        """Generate a single template with all slides"""
        
        # Get color palette for this category
        palette = TOPIC_COLOR_PALETTES.get(category, TOPIC_COLOR_PALETTES['default'])
        
        slide_images = []
        
        for slide_num in range(1, slide_count + 1):
            self.stdout.write(f'     Generating slide {slide_num}/{slide_count}...')
            
            # Generate the image prompt
            prompt = generate_enhanced_image_prompt(
                topic=topic,
                platform='instagram',
                style='modern',
                slide_number=slide_num,
                total_slides=slide_count,
                brand_colors=None,
                project_id=None
            )
            
            # Generate image using OpenAI
            image_base64 = self.generate_image(prompt)
            
            if image_base64:
                slide_images.append(image_base64)
            else:
                raise Exception(f'Failed to generate slide {slide_num}')
        
        # Create the template in database
        template = CarouselTemplate.objects.create(
            name=name,
            category=category,
            platform='instagram',
            style='modern',
            description=topic,
            preview_image=slide_images[0] if slide_images else '',
            slide_images=json.dumps(slide_images),
            slide_count=slide_count,
            primary_color=palette.get('background', '#FFFFFF'),
            secondary_color=palette.get('background_alt', '#F5F5F5'),
            accent_color=palette.get('accent', '#3B82F6'),
            font_color=palette.get('font_color', '#1F2937'),
            is_premium=False,
            is_active=True
        )
        
        return template

    def generate_image(self, prompt):
        """Generate image using OpenAI DALL-E API"""
        if not OPENAI_API_KEY:
            raise Exception('OPENAI_API_KEY not set in environment')
        
        try:
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-image-1',
                'prompt': prompt,
                'n': 1,
                'size': '1024x1024',
                'quality': 'medium'
            }
            
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get the base64 image data
                if 'data' in data and len(data['data']) > 0:
                    image_data = data['data'][0]
                    if 'b64_json' in image_data:
                        return image_data['b64_json']
                    elif 'url' in image_data:
                        # Download and convert to base64
                        img_response = requests.get(image_data['url'], timeout=30)
                        if img_response.status_code == 200:
                            return base64.b64encode(img_response.content).decode('utf-8')
            
            self.stdout.write(self.style.ERROR(f'API Error: {response.status_code} - {response.text[:200]}'))
            return None
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Request error: {str(e)}'))
            return None
