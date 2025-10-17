from django.core.management.base import BaseCommand
from django.test import Client
from recipes.models import Recipe

class Command(BaseCommand):
    help = 'Test the features page functionality'

    def handle(self, *args, **options):
        self.stdout.write("Testing features page...")
        
        # Check recipe count
        recipe_count = Recipe.objects.count()
        self.stdout.write(f"Found {recipe_count} recipes in database")
        
        # Test the view
        client = Client()
        response = client.get('/feature/')
        
        self.stdout.write(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            self.stdout.write("✅ Features page loads successfully!")
            self.stdout.write(f"Template used: {response.templates[0].name if response.templates else 'None'}")
            
            # Check if recipes are in context
            if response.context and 'recipes' in response.context:
                recipes_in_context = len(response.context['recipes'])
                self.stdout.write(f"Recipes in context: {recipes_in_context}")
            else:
                self.stdout.write("❌ No recipes found in context")
                self.stdout.write(f"Context available: {response.context is not None}")
                if response.context:
                    self.stdout.write(f"Context keys: {list(response.context.keys())}")
        else:
            self.stdout.write(f"❌ Features page failed with status {response.status_code}")
            if hasattr(response, 'content'):
                self.stdout.write(f"Error content: {response.content.decode()[:500]}")