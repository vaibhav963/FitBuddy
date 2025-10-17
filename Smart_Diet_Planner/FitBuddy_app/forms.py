from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, MealLog
from recipes.models import Recipe
from datetime import date


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class MealLogForm(forms.ModelForm):
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'recipe-select'
        }),
        empty_label="Select a recipe..."
    )
    
    meal_type = forms.ChoiceField(
        choices=MealLog.MEAL_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_logged = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    servings = forms.FloatField(
        initial=1.0,
        min_value=0.1,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0.1',
            'max': '10'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this meal...'
        })
    )

    class Meta:
        model = MealLog
        fields = ['recipe', 'meal_type', 'date_logged', 'servings', 'notes']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit recipes to those with basic nutrition info
        if user:
            self.fields['recipe'].queryset = Recipe.objects.filter(
                calories__isnull=False
            ).order_by('recipe_name')


class QuickMealLogForm(forms.Form):
    """Simplified form for quick meal logging"""
    recipe_id = forms.IntegerField(widget=forms.HiddenInput())
    meal_type = forms.ChoiceField(
        choices=MealLog.MEAL_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm'
        })
    )
    servings = forms.FloatField(
        initial=1.0,
        min_value=0.1,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'step': '0.1',
            'value': '1.0'
        })
    )
