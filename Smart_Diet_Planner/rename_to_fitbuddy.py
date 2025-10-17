"""
Script to rename the entire project from "Diet Planner" to "FitBuddy"
This will update all references, file names, and branding
"""

import os
import shutil
import re

def rename_project_to_fitbuddy():
    """
    Comprehensive renaming from Diet Planner to FitBuddy
    """
    
    print("🔄 Starting project rename from 'Diet Planner' to 'FitBuddy'...")
    
    # Define replacement mappings
    replacements = {
        # Project name replacements
        'Smart Diet Planner': 'FitBuddy',
        'Smart_Diet_Planner': 'FitBuddy',
        'smart-diet-planner': 'fitbuddy',
        'SMART_DIET_PLANNER': 'FITBUDDY',
        
        # App name replacements
        'Diet_planner_app': 'FitBuddy_app',
        'Diet Planner': 'FitBuddy',
        'diet_planner': 'fitbuddy',
        'diet-planner': 'fitbuddy',
        'DIET_PLANNER': 'FITBUDDY',
        
        # Branding replacements in HTML
        'Diet <span style="color: green;">Planner</span>': 'Fit<span style="color: green;">Buddy</span>',
        'Diet <span>Planner</span>': 'Fit<span>Buddy</span>',
        
        # App config replacements
        'DietPlannerAppConfig': 'FitBuddyAppConfig',
        
        # File references
        'Diet_logo.png': 'FitBuddy_logo.png',
    }
    
    # Files to update content
    files_to_update = [
        # Python files
        'manage.py',
        'Smart_Diet_Planner/settings.py',
        'Smart_Diet_Planner/urls.py',
        'Smart_Diet_Planner/wsgi.py',
        'Smart_Diet_Planner/asgi.py',
        'Diet_planner_app/apps.py',
        'Diet_planner_app/views.py',
        'Diet_planner_app/urls.py',
        'recipes/rag.py',
        'recipes/meal_planner.py',
        'recipes/simple_meal_planner.py',
        'regenerate_faiss.py',
        
        # HTML templates
        'Diet_planner_app/templates/Diet_planner_app/base.html',
        'Diet_planner_app/templates/Diet_planner_app/ai_meal_planner.html',
        'Diet_planner_app/templates/Diet_planner_app/meal_plan_result.html',
        'Diet_planner_app/templates/Diet_planner_app/home.html',
        'Diet_planner_app/templates/Diet_planner_app/login.html',
        'Diet_planner_app/templates/Diet_planner_app/about.html',
        'Diet_planner_app/templates/Diet_planner_app/contact.html',
        'Diet_planner_app/templates/Diet_planner_app/welcome.html',
        'Diet_planner_app/templates/Diet_planner_app/multiform.html',
        'Diet_planner_app/templates/Diet_planner_app/plan.html',
        'Diet_planner_app/templates/Diet_planner_app/policy.html',
        'Diet_planner_app/templates/Diet_planner_app/terms.html',
        'Diet_planner_app/templates/Diet_planner_app/roadmap.html',
        'Diet_planner_app/templates/Diet_planner_app/featured_recipes.html',
        'Diet_planner_app/templates/Diet_planner_app/final_sidebar.html',
        'recipes/templates/recipes/recipe_details.html',
        'recipes/templates/recipes/recipes_by_diet.html',
    ]
    
    # Update file contents
    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply all replacements
                for old_text, new_text in replacements.items():
                    content = content.replace(old_text, new_text)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated: {file_path}")
                
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print("\n🎉 Project renaming completed!")
    print("📝 Summary of changes:")
    print("   - Smart Diet Planner → FitBuddy")
    print("   - Diet Planner → FitBuddy")
    print("   - Diet_planner_app → FitBuddy_app (in code references)")
    print("   - Smart_Diet_Planner → FitBuddy (in settings)")
    print("\n⚠️ IMPORTANT NEXT STEPS:")
    print("1. You'll need to manually rename the 'Diet_planner_app' directory to 'FitBuddy_app'")
    print("2. You'll need to rename 'Smart_Diet_Planner' directory to 'FitBuddy'")
    print("3. You'll need to rename the logo file from 'Diet_logo.png' to 'FitBuddy_logo.png'")
    print("4. Run migrations after directory renaming")
    
    return True

if __name__ == "__main__":
    rename_project_to_fitbuddy()