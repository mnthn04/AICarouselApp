# api/models.py
from django.db import models
from django.utils import timezone  # Add this import

class CarouselProject(models.Model):
    """Canva Carousel Project"""
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
    """Canva Slide"""
    project = models.ForeignKey(CarouselProject, on_delete=models.CASCADE, related_name='slides')
    slide_number = models.IntegerField()
    title = models.TextField()
    description = models.TextField()
    extra_text = models.TextField(blank=True, null=True, help_text="Additional custom text for the slide")
    image_prompt = models.TextField()
    background_color = models.CharField(max_length=20, default='#FFFFFF')
    font_color = models.CharField(max_length=20, default='#000000')
    canvas_width = models.IntegerField(default=1080)
    canvas_height = models.IntegerField(default=1080)
    
    # Text Positioning
    title_x = models.IntegerField(blank=True, null=True)
    title_y = models.IntegerField(blank=True, null=True)
    description_x = models.IntegerField(blank=True, null=True)
    description_y = models.IntegerField(blank=True, null=True)
    extra_text_x = models.IntegerField(blank=True, null=True)
    extra_text_y = models.IntegerField(blank=True, null=True)
    
    generated_image = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Use default instead of auto_now_add
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['slide_number']
    
    def __str__(self):
        return f"Slide {self.slide_number}: {self.title[:30]}"