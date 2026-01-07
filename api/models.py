# api/models.py
from django.db import models
from django.utils import timezone  # Add this import

class CarouselProject(models.Model):
    """saystory Carousel Project"""
    topic = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    style = models.CharField(max_length=100)
    slide_count = models.IntegerField()
    profile_image = models.ImageField(upload_to='branding/profiles/', blank=True, null=True)
    profile_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Social media handle for @ symbol")
    brand_logo = models.ImageField(upload_to='branding/logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic} ({self.platform})"

class Slide(models.Model):
    """saystory Slide"""
    # Layout options for slide: determines image/text arrangement
    LAYOUT_CHOICES = [
        ('image-top', 'Image Top, Text Below'),
        ('image-left', 'Image Left, Text Right'),
        ('image-right', 'Image Right, Text Left'),
        ('full-background', 'Full Background Image'),
    ]
    
    project = models.ForeignKey(CarouselProject, on_delete=models.CASCADE, related_name='slides')
    slide_number = models.IntegerField()
    title = models.TextField()
    description = models.TextField()
    extra_text = models.TextField(blank=True, null=True, help_text="Additional custom text for the slide")
    image_prompt = models.TextField()
    background_color = models.CharField(max_length=20, default='#FFFFFF')
    font_color = models.CharField(max_length=20, default='#000000')
    saystorys_width = models.IntegerField(default=1080)
    saystorys_height = models.IntegerField(default=1080)
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='full-background')
    
    # Text Positioning
    title_x = models.IntegerField(blank=True, null=True)
    title_y = models.IntegerField(blank=True, null=True)
    description_x = models.IntegerField(blank=True, null=True)
    description_y = models.IntegerField(blank=True, null=True)
    extra_text_x = models.IntegerField(blank=True, null=True)
    extra_text_y = models.IntegerField(blank=True, null=True)
    
    # Store granular text styles (JSON string)
    text_styles = models.TextField(blank=True, default='{}')
    
    # Store multiple extra text elements (JSON list)
    # Format: [{"id": "uuid", "text": "...", "x": 0, "y": 0, "styles": {...}}]
    extra_texts = models.TextField(blank=True, default='[]')
    
    # Store user uploaded images (JSON list)
    # Format: [{"id": "uuid", "src": "base64...", "x": 0, "y": 0, "width": 100, "height": 100, "rotation": 0}]
    user_images = models.TextField(blank=True, default='[]')
    
    generated_image = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Use default instead of auto_now_add
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['slide_number']
    
    def __str__(self):
        return f"Slide {self.slide_number}: {self.title[:30]}"


class CarouselTemplate(models.Model):
    """Pre-generated carousel template for the template gallery"""
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('business', 'Business'),
        ('technology', 'Technology'),
        ('health', 'Health & Fitness'),
        ('lifestyle', 'Lifestyle'),
        ('education', 'Education'),
        ('creative', 'Creative'),
        ('travel', 'Travel'),
        ('finance', 'Finance'),
        ('fashion', 'Fashion'),
        ('food', 'Food'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    platform = models.CharField(max_length=50, default='instagram')
    style = models.CharField(max_length=100, default='modern')
    description = models.TextField(blank=True)
    
    # Template preview (first slide as thumbnail)
    preview_image = models.TextField(blank=True)  # Base64 encoded image
    
    # All slide images stored as JSON array of base64 strings
    slide_images = models.TextField(default='[]')
    slide_count = models.IntegerField(default=5)
    
    # Color scheme
    primary_color = models.CharField(max_length=20, default='#FFFFFF')
    secondary_color = models.CharField(max_length=20, default='#F5F5F5')
    accent_color = models.CharField(max_length=20, default='#3B82F6')
    font_color = models.CharField(max_length=20, default='#1F2937')
    
    # Metadata
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    use_count = models.IntegerField(default=0)  # Track popularity
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class ContentPreview(models.Model):
    """Stores 3 content preview variants for user selection before image generation"""
    session_id = models.CharField(max_length=100, db_index=True)  # Links previews together
    variant_number = models.IntegerField()  # 1, 2, or 3
    variant_name = models.CharField(max_length=50)  # e.g., "Professional", "Creative", "Bold"
    topic = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    style = models.CharField(max_length=100)
    slide_count = models.IntegerField()
    slides_json = models.TextField()  # JSON array of slide content
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['variant_number']
        unique_together = ['session_id', 'variant_number']
    
    def __str__(self):
        return f"Preview {self.variant_number}: {self.variant_name} - {self.topic[:30]}"