import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def clean_markdown(text):
    """
    Remove markdown formatting from text and make it more readable
    """
    if not text:
        return text
    
    # Remove markdown headers (### Key Ideas -> Key Ideas)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove bold formatting (**text** -> text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Remove italic formatting (*text* -> text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert markdown lists to HTML lists
    # Handle bullet points (- item -> • item)
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    
    # Handle numbered lists - keep as is but clean up
    text = re.sub(r'^\d+\.\s+', lambda m: f'<span class="number-point">{m.group(0)}</span>', text, flags=re.MULTILINE)
    
    # Clean up multiple newlines but preserve paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Convert double newlines to paragraph breaks
    text = re.sub(r'\n\n', '</p><p>', text)
    
    # Convert single newlines to line breaks
    text = text.replace('\n', '<br>')
    
    # Wrap in paragraph tags
    if text and not text.startswith('<p>'):
        text = f'<p>{text}</p>'
    
    # Clean up extra spaces
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Fix empty paragraphs
    text = re.sub(r'<p>\s*</p>', '', text)
    
    return mark_safe(text)

@register.filter
def format_summary(text):
    """
    Format summary text for better readability
    """
    if not text:
        return text
    
    # First clean markdown
    text = clean_markdown(text)
    
    # Add some styling classes for bullet points
    text = text.replace('• ', '<span class="bullet-point">• </span>')
    
    # Style section headers (if any remain)
    text = re.sub(r'<p>([A-Z][^<]*?):</p>', r'<h5 class="section-header">\1:</h5>', text)
    
    return mark_safe(text) 