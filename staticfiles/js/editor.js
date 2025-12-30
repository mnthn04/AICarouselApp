class CarouselEditor {
    constructor() {
        this.stage = null;
        this.layer = null;
        this.currentSlide = 0;
        this.slides = [];
        this.undoStack = [];
        this.redoStack = [];
        this.scale = 1;
        this.isLoading = true;
        
        this.init();
    }
    
    async init() {
        // Get project ID from URL
        const pathParts = window.location.pathname.split('/');
        this.projectId = pathParts[2];
        
        // Show loading
        this.showLoading();
        
        // Initialize Konva
        await this.initKonva();
        
        // Load slides
        await this.loadSlides();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Hide loading
        this.hideLoading();
    }
    
    showLoading() {
        document.getElementById('editorLoading').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('editorLoading').style.display = 'none';
    }
    
    async initKonva() {
        const container = document.getElementById('konvaContainer');
        const width = container.clientWidth;
        const height = container.clientHeight - 100;
        
        this.stage = new Konva.Stage({
            container: 'konvaContainer',
            width: width,
            height: height
        });
        
        this.layer = new Konva.Layer();
        this.stage.add(this.layer);
        
        // Add transformer for editing
        this.transformer = new Konva.Transformer({
            rotateEnabled: true,
            borderStroke: '#6366f1',
            borderStrokeWidth: 2,
            anchorStroke: '#6366f1',
            anchorFill: 'white',
            anchorSize: 10
        });
        this.layer.add(this.transformer);
        
        // Handle stage scaling
        this.stage.on('wheel', (e) => {
            e.evt.preventDefault();
            const scaleBy = 1.1;
            const oldScale = this.stage.scaleX();
            const pointer = this.stage.getPointerPosition();
            
            const mousePointTo = {
                x: (pointer.x - this.stage.x()) / oldScale,
                y: (pointer.y - this.stage.y()) / oldScale
            };
            
            const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy;
            
            this.stage.scale({ x: newScale, y: newScale });
            
            const newPos = {
                x: pointer.x - mousePointTo.x * newScale,
                y: pointer.y - mousePointTo.y * newScale
            };
            
            this.stage.position(newPos);
            this.scale = newScale;
            this.layer.batchDraw();
        });
    }
    
    async loadSlides() {
        try {
            // Get project ID from URL
            const pathParts = window.location.pathname.split('/');
            const projectId = pathParts[2];
            
            const response = await fetch(`/api/project/${projectId}/slides/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API Response:', data);
            
            if (data.success && data.slides && Array.isArray(data.slides)) {
                this.slides = data.slides;
                this.project = data.project; // Store project data
                console.log('Loaded slides:', this.slides.length);
            } else {
                throw new Error(data.error || 'Invalid response format');
            }
            
            this.renderSlidesList();
            this.renderSlide(0);
            
        } catch (error) {
            console.error('Error loading slides:', error);
            toastr.error('Failed to load slides');
        }
    }
    
    renderSlidesList() {
        const slidesList = document.getElementById('slidesList');
        slidesList.innerHTML = '';
        
        this.slides.forEach((slide, index) => {
            const slideItem = document.createElement('div');
            slideItem.className = `slide-item ${index === this.currentSlide ? 'active' : ''}`;
            slideItem.innerHTML = `
                <div class="slide-item-header">
                    <div class="slide-item-title">${slide.title || 'Slide ' + (index + 1)}</div>
                    <div class="slide-item-actions">
                        <button class="delete-slide-btn" data-slide-id="${slide.id}" title="Delete slide">
                            <i class="fas fa-trash"></i>
                        </button>
                        <span class="slide-number">${index + 1}</span>
                    </div>
                </div>
                <div class="slide-item-preview">
                    ${slide.title ? slide.title.substring(0, 30) : 'Preview'}
                </div>
            `;
            
            slideItem.addEventListener('click', () => {
                this.currentSlide = index;
                this.renderSlide(index);
                this.updateSlidesList();
            });
            
            // Add delete button event listener
            const deleteBtn = slideItem.querySelector('.delete-slide-btn');
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                
                if (this.slides.length <= 1) {
                    toastr.error('Cannot delete the last slide');
                    return;
                }
                
                if (!confirm('Are you sure you want to delete this slide?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/delete-slide/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({
                            slide_id: slide.id
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.slides.splice(index, 1);
                        if (this.currentSlide >= this.slides.length) {
                            this.currentSlide = Math.max(0, this.slides.length - 1);
                        }
                        this.renderSlidesList();
                        if (this.slides.length > 0) {
                            this.renderSlide(this.currentSlide);
                        }
                        toastr.success('Slide deleted');
                    } else {
                        toastr.error(data.error || 'Failed to delete slide');
                    }
                } catch (error) {
                    console.error('Error deleting slide:', error);
                    toastr.error('Failed to delete slide');
                }
            });
            
            slidesList.appendChild(slideItem);
        });
    }
    
    updateSlidesList() {
        document.querySelectorAll('.slide-item').forEach((item, index) => {
            item.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    renderSlide(slideIndex) {
        this.layer.destroyChildren();
        
        const slide = this.slides[slideIndex];
        const width = this.stage.width();
        const height = this.stage.height();
        
        // Background
        const background = new Konva.Rect({
            x: 0,
            y: 0,
            width: width,
            height: height,
            fill: slide.background_color,
            stroke: '#e5e7eb',
            strokeWidth: 1
        });
        
        // Title
        const title = new Konva.Text({
            x: width / 2,
            y: height / 3,
            text: slide.title,
            fontSize: 48,
            fontFamily: 'Poppins',
            fill: slide.font_color,
            align: 'center',
            width: width * 0.8,
            padding: 20
        });
        
        title.offsetX(title.width() / 2);
        
        // Description
        const description = new Konva.Text({
            x: width / 2,
            y: height / 2,
            text: slide.description,
            fontSize: 24,
            fontFamily: 'Inter',
            fill: slide.font_color,
            align: 'center',
            width: width * 0.7,
            padding: 20
        });
        
        description.offsetX(description.width() / 2);
        
        // Add all to layer
        this.layer.add(background, title, description);
        
        // Make text editable
        this.makeEditable(title);
        this.makeEditable(description);
        
        // Update UI
        document.getElementById('currentSlide').textContent = 
            `Slide ${slideIndex + 1} of ${this.slides.length}`;
        
        document.getElementById('slideTitle').value = slide.title;
        document.getElementById('slideDescription').value = slide.description;
        document.getElementById('slideImagePrompt').value = slide.image_prompt;
        document.getElementById('bgColor').value = slide.background_color;
        document.getElementById('fontColor').value = slide.font_color;
        
        this.layer.batchDraw();
    }
    
    makeEditable(textNode) {
        textNode.on('dblclick', () => {
            const textPosition = textNode.absolutePosition();
            const stageBox = this.stage.container().getBoundingClientRect();
            
            const areaPosition = {
                x: stageBox.left + textPosition.x,
                y: stageBox.top + textPosition.y
            };
            
            const textarea = document.createElement('textarea');
            document.body.appendChild(textarea);
            
            textarea.value = textNode.text();
            textarea.style.position = 'absolute';
            textarea.style.top = areaPosition.y + 'px';
            textarea.style.left = areaPosition.x + 'px';
            textarea.style.width = textNode.width() + 'px';
            textarea.style.height = textNode.height() + 'px';
            textarea.style.fontSize = textNode.fontSize() + 'px';
            textarea.style.border = 'none';
            textarea.style.padding = '0px';
            textarea.style.margin = '0px';
            textarea.style.overflow = 'hidden';
            textarea.style.background = 'none';
            textarea.style.outline = 'none';
            textarea.style.resize = 'none';
            textarea.style.lineHeight = textNode.lineHeight();
            textarea.style.fontFamily = textNode.fontFamily();
            textarea.style.transformOrigin = 'left top';
            textarea.style.textAlign = textNode.align();
            textarea.style.color = textNode.fill();
            textarea.focus();
            
            const transform = textNode.getAbsoluteTransform().copy();
            transform.invert();
            const textareaOffset = transform.point(textNode.offset());
            
            textarea.style.top = (areaPosition.y - textareaOffset.y) + 'px';
            textarea.style.left = (areaPosition.x - textareaOffset.x) + 'px';
            
            const removeTextarea = () => {
                textarea.removeEventListener('blur', removeTextarea);
                textarea.remove();
                window.removeEventListener('click', handleOutsideClick);
                
                textNode.text(textarea.value);
                this.layer.batchDraw();
            };
            
            textarea.addEventListener('blur', removeTextarea);
            
            const handleOutsideClick = (e) => {
                if (e.target !== textarea) {
                    removeTextarea();
                }
            };
            
            setTimeout(() => {
                window.addEventListener('click', handleOutsideClick);
            });
        });
    }
    
    setupEventListeners() {
        // Navigation
        document.getElementById('prevSlide').addEventListener('click', () => {
            if (this.currentSlide > 0) {
                this.currentSlide--;
                this.renderSlide(this.currentSlide);
                this.updateSlidesList();
            }
        });
        
        document.getElementById('nextSlide').addEventListener('click', () => {
            if (this.currentSlide < this.slides.length - 1) {
                this.currentSlide++;
                this.renderSlide(this.currentSlide);
                this.updateSlidesList();
            }
        });
        
        // Design controls
        document.getElementById('bgColor').addEventListener('change', (e) => {
            const slide = this.slides[this.currentSlide];
            slide.background_color = e.target.value;
            this.renderSlide(this.currentSlide);
        });
        
        document.getElementById('fontColor').addEventListener('change', (e) => {
            const slide = this.slides[this.currentSlide];
            slide.font_color = e.target.value;
            this.renderSlide(this.currentSlide);
        });
        
        // Content update
        document.getElementById('updateContent').addEventListener('click', () => {
            const slide = this.slides[this.currentSlide];
            slide.title = document.getElementById('slideTitle').value;
            slide.description = document.getElementById('slideDescription').value;
            slide.image_prompt = document.getElementById('slideImagePrompt').value;
            this.renderSlide(this.currentSlide);
            this.renderSlidesList();
            toastr.success('Slide updated');
        });
        
        // Add slide
        document.getElementById('addSlide').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/add-slide/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        project_id: this.projectId
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.slides.push(data.slide);
                    this.currentSlide = this.slides.length - 1;
                    this.renderSlide(this.currentSlide);
                    this.renderSlidesList();
                    toastr.success('New slide added');
                } else {
                    toastr.error(data.error || 'Failed to add slide');
                }
            } catch (error) {
                console.error('Error adding slide:', error);
                toastr.error('Failed to add slide');
            }
        });
        
        // Generate image
        document.getElementById('generateImageBtn').addEventListener('click', async () => {
            const prompt = document.getElementById('imagePrompt').value;
            if (!prompt.trim()) {
                toastr.error('Please enter an image description');
                return;
            }
            
            toastr.info('Generating image...');
            
            try {
                const response = await fetch('/api/generate-image/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Add image to slide
                    const imagePreview = document.getElementById('imagePreview');
                    imagePreview.innerHTML = `<img src="${data.image_url}" alt="Generated">`;
                    
                    // Add image to canvas
                    const img = new Image();
                    img.onload = () => {
                        const konvaImage = new Konva.Image({
                            x: 0,
                            y: 0,
                            image: img,
                            width: this.stage.width(),
                            height: this.stage.height()
                        });
                        
                        // Move to back
                        konvaImage.moveToBottom();
                        this.layer.add(konvaImage);
                        this.layer.batchDraw();
                        
                        toastr.success('Image generated and added to slide');
                    };
                    img.src = data.image_url;
                } else {
                    toastr.error(data.error);
                }
            } catch (error) {
                console.error('Error generating image:', error);
                toastr.error('Failed to generate image');
            }
        });
        
        // Save design
        document.getElementById('saveDesign').addEventListener('click', async () => {
            const slide = this.slides[this.currentSlide];
            
            try {
                const response = await fetch('/api/save-design/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        slide_id: slide.id,
                        design_data: JSON.stringify(slide)
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    toastr.success('Design saved successfully');
                } else {
                    toastr.error(data.error || 'Failed to save design');
                }
            } catch (error) {
                console.error('Error saving design:', error);
                toastr.error('Failed to save design');
            }
        });
        
        // Export
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportSlides();
        });
        
        // Zoom controls
        document.getElementById('zoomIn').addEventListener('click', () => {
            this.zoom(1.2);
        });
        
        document.getElementById('zoomOut').addEventListener('click', () => {
            this.zoom(0.8);
        });
        
        document.getElementById('resetView').addEventListener('click', () => {
            this.stage.scale({ x: 1, y: 1 });
            this.stage.position({ x: 0, y: 0 });
            this.layer.batchDraw();
        });
    }
    
    zoom(factor) {
        const oldScale = this.stage.scaleX();
        const newScale = oldScale * factor;
        
        const center = {
            x: this.stage.width() / 2,
            y: this.stage.height() / 2
        };
        
        const relatedTo = {
            x: (center.x - this.stage.x()) / oldScale,
            y: (center.y - this.stage.y()) / oldScale
        };
        
        this.stage.scale({ x: newScale, y: newScale });
        
        const newPos = {
            x: center.x - relatedTo.x * newScale,
            y: center.y - relatedTo.y * newScale
        };
        
        this.stage.position(newPos);
        this.scale = newScale;
        this.layer.batchDraw();
    }
    
    async exportSlides() {
        toastr.info('Preparing slides for download...');
        
        // Export each slide
        for (let i = 0; i < this.slides.length; i++) {
            await this.exportSlide(i);
        }
        
        toastr.success('All slides exported successfully');
    }
    
    async exportSlide(slideIndex) {
        // Render slide
        this.currentSlide = slideIndex;
        this.renderSlide(slideIndex);
        
        // Wait for render
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Export as image
        const dataURL = this.stage.toDataURL({
            mimeType: 'image/png',
            quality: 1.0,
            pixelRatio: 2
        });
        
        // Download
        const link = document.createElement('a');
        link.download = `slide-${slideIndex + 1}.png`;
        link.href = dataURL;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize editor when page loads
document.addEventListener('DOMContentLoaded', () => {
    new CarouselEditor();
});