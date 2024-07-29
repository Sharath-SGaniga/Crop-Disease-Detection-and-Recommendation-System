from django import forms
from .models import Image

from django import forms
from .models import Image

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            image_name = image.name
            image_name = image_name.replace(' ', '-')
            image.name = image_name
        return image
