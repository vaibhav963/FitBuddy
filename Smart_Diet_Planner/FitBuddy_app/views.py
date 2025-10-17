from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings
from django.db.models import Q
from .models import UserProfile, MealLog, DailyNutritionSummary
from recipes.models import Recipe
from datetime import date
import json
from recipes.rag import process_query
from recipes.simple_meal_planner import generate_simple_meal_plan, get_simple_recipe_by_name
from django.utils.http import url_has_allowed_host_and_scheme
import re
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'FitBuddy_app/home.html')

def login(request):

    if request.method == 'POST':
        

        form_type = request.POST.get('form_type')
        auth_method = request.POST.get('auth_method', 'manual')
        
        if auth_method != 'manual':
            messages.error(request, "Invalid authentication method.")
            return render(request, 'FitBuddy_app/login.html')
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate email and password
        if not all([email, password]):
            messages.error(request, "Email and password are required!")
            return render(request, 'FitBuddy_app/login.html')
        
        if form_type == 'signup':

            # Handle Sign-Up
            name = request.POST.get('name')
            if not name:
                messages.error(request, "Name is required for registration!")
                return render(request, 'FitBuddy_app/login.html')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
                return render(request, 'FitBuddy_app/login.html')
            
            try:
                # Create new user
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=password, 
                    first_name=name
                )
                
                # Login the new user
                user = authenticate(request, username=email, password=password)
                if user:
                    auth_login(request, user)
                    messages.success(request, "Account created successfully! Welcome!")
                    # Redirect new users to intended page if safe, else home
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)
                    return redirect('home')
                
            except Exception as e:
                messages.error(request, "Error creating account. Please try again.")
                return render(request, 'FitBuddy_app/login.html')
        
        elif form_type == 'signin':
            # Handle Sign-In

            user = authenticate(request, username=email, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, "Welcome back!")
                # After successful sign-in, go to intended page if supplied
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password!")
                return render(request, 'FitBuddy_app/login.html')
        
        else:
            messages.error(request, "Invalid form type.")
    
    # GET request
    form = AuthenticationForm()
    return render(request, 'FitBuddy_app/login.html', {'form': form})


def save_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.age = data.get('age')
        profile.height = data.get('height')
        profile.height_unit = data.get('height_unit')
        profile.gender = data.get('gender')
        profile.current_weight = data.get('current_weight')
        profile.target_weight = data.get('target_weight')
        profile.weight_unit = data.get('weight_unit')
        profile.food_allergies = ','.join(data.get('allergies', []))
        profile.cooking_skill = data.get('cooking_skill')
        profile.budget = data.get('budget')
        profile.physical_activity = data.get('physical_activity')
        profile.include_exercise = data.get('include_exercise')
        profile.meal_prep_time = data.get('meal_prep_time')
        profile.meals_per_day = data.get('meals_per_day')
        profile.cooking_frequency = data.get('cooking_frequency')
        profile.commitment_duration = data.get('commitment_duration')
        profile.additional_info = data.get('additional_info')
        profile.save()

        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False}, status=400)
    
def about(request):
    return render(request, 'FitBuddy_app/about.html')

def contact(request):
    return render(request, 'FitBuddy_app/contact.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def welcome(request):
    return render(request, 'FitBuddy_app/welcome.html')

def form(request):
    return render(request, 'FitBuddy_app/multiform.html')

def plan(request):
    return render(request, 'FitBuddy_app/plan.html')

def policy(request):
    return render(request, 'FitBuddy_app/policy.html')

def terms(request):
    return render(request, 'FitBuddy_app/terms.html')

def roadmap(request):
    return render(request, 'FitBuddy_app/roadmap.html')

def features(request):
    """View to display recipes filtered by diet type - redirected from old features URL"""
    from django.db.models import Q
    
    diet_type = request.GET.get('diet', 'All')
    search_query = request.GET.get('search', '')
    
    # Get all available diet types
    diet_types = Recipe.get_available_diet_types()
    
    # Filter recipes
    recipes = Recipe.objects.all()
    
    if diet_type != 'All':
        recipes = recipes.filter(diet_types__icontains=diet_type)
    
    if search_query:
        recipes = recipes.filter(
            Q(recipe_name__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(type__icontains=search_query)
        )
    
    # Get recipe counts by diet type
    diet_counts = {}
    for dt in diet_types:
        diet_counts[dt] = Recipe.objects.filter(diet_types__icontains=dt).count()
    
    context = {
        'recipes': recipes.order_by('recipe_name'),
        'diet_types': diet_types,
        'selected_diet': diet_type,
        'search_query': search_query,
        'diet_counts': diet_counts,
        'total_recipes': Recipe.objects.count()
    }
    
    return render(request, 'FitBuddy_app/featured_recipes.html', context)

def recipe_query(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if request.user.is_authenticated:
                user = request.user

            data = json.loads(request.body)
            query = data.get('query')
            history = data.get('history', [])
            
            # Check if query is provided
            if not query or not query.strip():
                return JsonResponse({
                    'response': 'Please enter a question about recipes or nutrition.',
                    'history': history
                })
            
            # Try AI-powered response first
            try:
                response, updated_history = process_query(query, history)
                return JsonResponse({
                    'response': response,
                    'history': updated_history
                })
            except Exception as ai_error:
                print(f"AI error in recipe_query: {ai_error}")
                
                # Fall back to simple responses
                try:
                    from recipes.fallback_responses import get_fallback_response
                    fallback_response = get_fallback_response(query)
                    
                    # Add to history
                    history.append({"role": "human", "content": query})
                    history.append({"role": "assistant", "content": fallback_response})
                    
                    return JsonResponse({
                        'response': fallback_response,
                        'history': history
                    })
                except Exception as fallback_error:
                    print(f"Fallback error: {fallback_error}")
                    
                    # Ultimate fallback
                    basic_response = "I'm having trouble right now, but I'm here to help with recipes and nutrition! You can browse our recipe collection or try our meal planner while I get back online."
                    history.append({"role": "human", "content": query})
                    history.append({"role": "assistant", "content": basic_response})
                    
                    return JsonResponse({
                        'response': basic_response,
                        'history': history
                    })
            
        except Exception as e:
            print(f"General error in recipe_query: {e}")
            
            # Ultimate fallback response
            try:
                data = json.loads(request.body)
                query = data.get('query', 'Hello')
                history = data.get('history', [])
            except:
                query = 'Hello'
                history = []
            
            basic_response = "I'm experiencing some technical difficulties, but I'm here to help! Please try browsing our recipe collection or using our meal planner."
            history.append({"role": "human", "content": query})
            history.append({"role": "assistant", "content": basic_response})
            
            return JsonResponse({
                'response': basic_response,
                'history': history
            })

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def ai_meal_planner(request):
    """AI-Powered Meal Plan Generator View"""
    if request.method == 'POST':
        try:
            # Helpers for parsing and validation
            def parse_weight_to_kg(weight_str: str):
                if not weight_str:
                    return None
                s = weight_str.strip().lower()
                m = re.search(r"(\d+\.?\d*)\s*(kg|kgs|kilogram|kilograms|lb|lbs|pound|pounds)?", s)
                if not m:
                    return None
                value = float(m.group(1))
                unit = m.group(2) or 'kg'
                if unit in ['lb', 'lbs', 'pound', 'pounds']:
                    return value * 0.453592
                return value

            def parse_height_to_cm(height_str: str):
                if not height_str:
                    return None
                s = height_str.strip().lower()
                # cm pattern
                m_cm = re.search(r"(\d+\.?\d*)\s*cm", s)
                if m_cm:
                    return float(m_cm.group(1))
                # feet'in" pattern like 5'8" or 5 ft 8 in
                m_ft_in = re.search(r"(\d+)\s*(ft|')\s*(\d+)?\s*(in|\")?", s)
                if m_ft_in:
                    ft = int(m_ft_in.group(1))
                    inches = int(m_ft_in.group(3) or 0)
                    return ft * 30.48 + inches * 2.54
                # plain number assume cm
                m_plain = re.search(r"^(\d+\.?\d*)$", s)
                if m_plain:
                    return float(m_plain.group(1))
                return None

            def estimate_calories(age: int, weight_kg: float, activity_level: str, goal: str) -> int:
                # Mirror the simple JS heuristic previously used on the client
                bmr = (weight_kg or 70) * 22
                activity_multipliers = {
                    'sedentary': 1.2,
                    'light': 1.375,
                    'moderate': 1.55,
                    'active': 1.725,
                    'very active': 1.9,
                }
                calories = bmr * activity_multipliers.get(activity_level, 1.55)
                if goal in ['lose weight']:
                    calories *= 0.85
                elif goal in ['gain weight', 'build muscle']:
                    calories *= 1.15
                # Clamp to reasonable range
                calories = max(1200, min(4000, round(calories)))
                return int(calories)

            # Collect raw inputs
            raw = {
                'days': request.POST.get('days', '7'),
                'goal': request.POST.get('goal', 'maintain weight').strip().lower(),
                'diet_type': request.POST.get('diet_type', 'Any').strip(),
                'allergies': request.POST.get('allergies', 'none').strip(),
                'age': request.POST.get('age', '30'),
                'weight': request.POST.get('weight', '70kg').strip(),
                'height': request.POST.get('height', "5'8\"").strip(),
                'activity_level': request.POST.get('activity_level', 'moderate').strip().lower(),
                'meals_per_day': request.POST.get('meals_per_day', '4'),
                'preferences': request.POST.get('preferences', 'none').strip(),
            }

            errors = []

            # Validate fields
            # days
            allowed_days = {'1', '3', '7', '14', '21', '28'}
            if raw['days'] not in allowed_days:
                errors.append('Invalid plan duration selected.')
            days = int(raw['days']) if raw['days'] in allowed_days else 7

            # goal
            allowed_goals = {'lose weight', 'maintain weight', 'gain weight', 'build muscle', 'improve health'}
            if raw['goal'] not in allowed_goals:
                errors.append('Invalid goal selected.')

            # activity
            allowed_activity = {'sedentary', 'light', 'moderate', 'active', 'very active'}
            if raw['activity_level'] not in allowed_activity:
                errors.append('Invalid activity level selected.')

            # diet type (allow only the options present)
            allowed_diets = {'Any', 'Balanced', 'Ketogenic', 'Paleo', 'Vegetarian', 'Vegan', 'Mediterranean', 'Low Carb', 'High Protein', 'Gluten Free'}
            if raw['diet_type'] not in allowed_diets:
                errors.append('Invalid diet type selected.')

            # age
            try:
                age = int(raw['age'])
                if age < 15 or age > 100:
                    errors.append('Age must be between 15 and 100.')
            except ValueError:
                errors.append('Age must be a valid number.')
                age = 30

            # weight
            weight_kg = parse_weight_to_kg(raw['weight'])
            if weight_kg is None:
                errors.append("Weight format is invalid. Use formats like '70kg' or '154lbs'.")
            else:
                if weight_kg < 30 or weight_kg > 300:
                    errors.append('Weight must be between 30kg and 300kg.')

            # height
            height_cm = parse_height_to_cm(raw['height'])
            if height_cm is None:
                errors.append("Height format is invalid. Use formats like 5'8\" or 173cm.")
            else:
                if height_cm < 120 or height_cm > 230:
                    errors.append('Height must be between 120cm and 230cm.')

            # meals per day
            allowed_meals = {'3', '4', '5', '6'}
            if raw['meals_per_day'] not in allowed_meals:
                errors.append('Invalid meals per day selected.')
            meals_per_day = int(raw['meals_per_day']) if raw['meals_per_day'] in allowed_meals else 4

            # text limits
            if len(raw['allergies']) > 200:
                errors.append('Allergies field is too long (max 200 characters).')
            if len(raw['preferences']) > 1000:
                errors.append('Preferences field is too long (max 1000 characters).')

            if errors:
                for err in errors:
                    messages.error(request, err)
                # Re-render form with errors; defaults will repopulate
                return render(request, 'FitBuddy_app/ai_meal_planner.html')

            # Compute calories server-side now that calories input was removed
            computed_calories = estimate_calories(age=age, weight_kg=weight_kg, activity_level=raw['activity_level'], goal=raw['goal'])

            # Build preferences for generator
            user_preferences = {
                'days': days,
                'goal': raw['goal'],
                'diet_type': raw['diet_type'],
                'allergies': raw['allergies'] or 'none',
                'calories': int(computed_calories),
                'age': age,
                'weight': raw['weight'],
                'height': raw['height'],
                'activity_level': raw['activity_level'],
                'meals_per_day': meals_per_day,
                'preferences': raw['preferences'] or 'none',
            }

            print(f"DEBUG: User preferences (validated): {user_preferences}")
            
            # Test API key first
            from django.conf import settings
            api_key = getattr(settings, 'GOOGLE_API_KEY', '')
            if not api_key:
                messages.error(request, 'Google API key not configured. Please add GOOGLE_API_KEY to your .env file.')
                return render(request, 'FitBuddy_app/ai_meal_planner.html')
            
            print(f"DEBUG: API key available: {bool(api_key)}")
            
            # Generate meal plan using AI
            print("DEBUG: Calling generate_custom_meal_plan...")
            result = generate_simple_meal_plan(user_preferences)
            print(f"DEBUG: Result: {result}")
            
            if result['success']:
                # Store meal plan in session for display
                request.session['generated_meal_plan'] = result['meal_plan']
                
                # Check if it's a demo plan due to quota exceeded
                if 'note' in result:
                    messages.warning(request, f"Demo meal plan generated! {result['note']}")
                else:
                    messages.success(request, 'Your personalized AI meal plan has been generated!')
                
                return render(request, 'FitBuddy_app/meal_plan_result.html', {
                    'meal_plan': result['meal_plan'],
                    'user_preferences': user_preferences,
                    'is_demo': 'note' in result
                })
            else:
                messages.error(request, f"Error generating meal plan: {result.get('message', 'Unknown error')}")
                return render(request, 'FitBuddy_app/ai_meal_planner.html')
                
        except Exception as e:
            messages.error(request, f'Error processing your request: {str(e)}')
            return render(request, 'FitBuddy_app/ai_meal_planner.html')
    
    # GET request - show the form
    return render(request, 'FitBuddy_app/ai_meal_planner.html')

def meal_plan_recipe_detail(request, recipe_name):
    """Get detailed recipe information for meal plan"""
    recipe_details = get_simple_recipe_by_name(recipe_name)
    
    if recipe_details:
        return JsonResponse({
            'success': True,
            'recipe': recipe_details
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Recipe not found'
        })

def test_ai_setup(request):
    """Test endpoint to verify AI setup"""
    from django.conf import settings
    from recipes.models import Recipe
    
    try:
        # Check API key
        api_key = getattr(settings, 'GOOGLE_API_KEY', '')
        api_key_status = bool(api_key)
        
        # Check recipes
        recipe_count = Recipe.objects.count()
        
        # Test simple AI call with direct Google AI
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # List available models
                available_models = []
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        available_models.append(model.name)
                
                if available_models:
                    # Use the first available model
                    model_name = available_models[0]
                    model = genai.GenerativeModel(model_name)
                    test_response = model.generate_content("Say 'AI setup working!'")
                    ai_test_result = f"SUCCESS: {test_response.text} (using {model_name})"
                else:
                    ai_test_result = "No compatible models found"
                    
            except Exception as e:
                ai_test_result = f"AI test failed: {str(e)}"
        else:
            ai_test_result = "No API key"
        
        return JsonResponse({
            'api_key_configured': api_key_status,
            'api_key_preview': api_key[:10] + '...' if api_key else 'None',
            'recipe_count': recipe_count,
            'ai_test': ai_test_result,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        })


# =============== MEAL LOGGING VIEWS ===============

@login_required
def dashboard(request):
    """Main dashboard with meal logging overview"""
    from datetime import date, timedelta
    from django.db.models import Sum
    from .models import MealLog, DailyNutritionSummary
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Get today's meals
    todays_meals = MealLog.objects.filter(
        user=request.user,
        date_logged=today
    ).select_related('recipe')
    
    # Get today's nutrition summary
    todays_nutrition = {
        'calories': sum(meal.get_total_calories() for meal in todays_meals),
        'protein': sum(meal.get_total_protein() for meal in todays_meals),
        'carbs': sum(meal.get_total_carbs() for meal in todays_meals),
        'fat': sum(meal.get_total_fat() for meal in todays_meals),
    }
    
    # Get recent meals (last 7 days)
    recent_meals = MealLog.objects.filter(
        user=request.user,
        date_logged__gte=week_ago
    ).select_related('recipe').order_by('-date_logged', '-created_at')[:10]
    
    # Group today's meals by type
    meals_by_type = {
        'breakfast': todays_meals.filter(meal_type='breakfast'),
        'lunch': todays_meals.filter(meal_type='lunch'),
        'dinner': todays_meals.filter(meal_type='dinner'),
        'snack': todays_meals.filter(meal_type='snack'),
    }
    
    # Get user's goals (if available)
    user_profile = getattr(request.user, 'userprofile', None)
    daily_goals = {
        'calories': 2000,  # Default values
        'protein': 150,
        'carbs': 250,
        'fat': 65,
    }
    
    if user_profile:
        # Calculate goals based on profile (simplified calculation)
        if user_profile.current_weight and user_profile.physical_activity:
            activity_multiplier = {
                'Sedentary': 1.2,
                'Light': 1.375,
                'Moderate': 1.55,
                'Active': 1.725
            }.get(user_profile.physical_activity, 1.55)
            
            # Basic BMR calculation
            if user_profile.gender == 'Male':
                bmr = 88.362 + (13.397 * user_profile.current_weight)
            else:
                bmr = 447.593 + (9.247 * user_profile.current_weight)
            
            daily_goals['calories'] = int(bmr * activity_multiplier)
            daily_goals['protein'] = int(user_profile.current_weight * 1.2)  # 1.2g per kg
            daily_goals['carbs'] = int(daily_goals['calories'] * 0.5 / 4)  # 50% of calories
            daily_goals['fat'] = int(daily_goals['calories'] * 0.25 / 9)  # 25% of calories
    
    context = {
        'todays_meals': todays_meals,
        'todays_nutrition': todays_nutrition,
        'recent_meals': recent_meals,
        'meals_by_type': meals_by_type,
        'daily_goals': daily_goals,
        'today': today,
        'progress_percentages': {
            'calories': min(100, (todays_nutrition['calories'] / daily_goals['calories']) * 100) if daily_goals['calories'] > 0 else 0,
            'protein': min(100, (todays_nutrition['protein'] / daily_goals['protein']) * 100) if daily_goals['protein'] > 0 else 0,
            'carbs': min(100, (todays_nutrition['carbs'] / daily_goals['carbs']) * 100) if daily_goals['carbs'] > 0 else 0,
            'fat': min(100, (todays_nutrition['fat'] / daily_goals['fat']) * 100) if daily_goals['fat'] > 0 else 0,
        }
    }
    
    return render(request, 'FitBuddy_app/dashboard.html', context)


@login_required
def add_meal_log(request):
    """Add a new meal log entry"""
    from .forms import MealLogForm
    
    if request.method == 'POST':
        form = MealLogForm(request.POST, user=request.user)
        if form.is_valid():
            meal_log = form.save(commit=False)
            meal_log.user = request.user
            
            # Check for duplicate entry
            existing = MealLog.objects.filter(
                user=request.user,
                recipe=meal_log.recipe,
                meal_type=meal_log.meal_type,
                date_logged=meal_log.date_logged
            ).exists()
            
            if existing:
                messages.warning(request, 'You have already logged this recipe for this meal today. Consider editing the existing entry instead.')
                return render(request, 'FitBuddy_app/add_meal_log.html', {'form': form})
            
            meal_log.save()
            messages.success(request, f'Successfully logged {meal_log.recipe.recipe_name} for {meal_log.meal_type}!')
            return redirect('dashboard')
    else:
        form = MealLogForm(user=request.user)
    
    return render(request, 'FitBuddy_app/add_meal_log.html', {'form': form})


@login_required
def quick_add_meal(request):
    """Quick add meal from recipe detail page"""
    from .forms import QuickMealLogForm
    from .models import MealLog
    
    if request.method == 'POST':
        form = QuickMealLogForm(request.POST)
        if form.is_valid():
            recipe_id = form.cleaned_data['recipe_id']
            meal_type = form.cleaned_data['meal_type']
            servings = form.cleaned_data['servings']
            
            try:
                recipe = Recipe.objects.get(id=recipe_id)
                
                # Check for duplicate
                existing = MealLog.objects.filter(
                    user=request.user,
                    recipe=recipe,
                    meal_type=meal_type,
                    date_logged=date.today()
                ).first()
                
                if existing:
                    # Update existing entry
                    existing.servings += servings
                    existing.save()
                    message = f'Updated {recipe.recipe_name} serving size to {existing.servings}'
                else:
                    # Create new entry
                    MealLog.objects.create(
                        user=request.user,
                        recipe=recipe,
                        meal_type=meal_type,
                        servings=servings
                    )
                    message = f'Added {recipe.recipe_name} to your {meal_type} log!'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': message})
                else:
                    messages.success(request, message)
                    return redirect('dashboard')
                    
            except Recipe.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Recipe not found'})
                else:
                    messages.error(request, 'Recipe not found')
                    return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid form data'})
            else:
                messages.error(request, 'Invalid form data')
                return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def edit_meal_log(request, log_id):
    """Edit an existing meal log entry"""
    from .forms import MealLogForm
    from django.shortcuts import get_object_or_404
    
    meal_log = get_object_or_404(MealLog, id=log_id, user=request.user)
    
    if request.method == 'POST':
        form = MealLogForm(request.POST, instance=meal_log, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Successfully updated {meal_log.recipe.recipe_name} log!')
            return redirect('dashboard')
    else:
        form = MealLogForm(instance=meal_log, user=request.user)
    
    return render(request, 'FitBuddy_app/edit_meal_log.html', {
        'form': form,
        'meal_log': meal_log
    })


@login_required
def delete_meal_log(request, log_id):
    """Delete a meal log entry"""
    from django.shortcuts import get_object_or_404
    
    meal_log = get_object_or_404(MealLog, id=log_id, user=request.user)
    
    if request.method == 'POST':
        recipe_name = meal_log.recipe.recipe_name
        meal_type = meal_log.meal_type
        meal_log.delete()
        messages.success(request, f'Removed {recipe_name} from your {meal_type} log!')
        return redirect('dashboard')
    
    return render(request, 'FitBuddy_app/confirm_delete_meal.html', {
        'meal_log': meal_log
    })


@login_required
def meal_history(request):
    """View meal logging history"""
    from datetime import date, timedelta
    from django.db.models import Sum
    
    # Get date range from query params
    days = int(request.GET.get('days', 30))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get meal logs for the period
    meal_logs = MealLog.objects.filter(
        user=request.user,
        date_logged__gte=start_date,
        date_logged__lte=end_date
    ).select_related('recipe').order_by('-date_logged', 'meal_type', '-created_at')
    
    # Group by date
    meals_by_date = {}
    daily_totals = {}
    
    for meal in meal_logs:
        date_key = meal.date_logged
        if date_key not in meals_by_date:
            meals_by_date[date_key] = []
            daily_totals[date_key] = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0
            }
        
        meals_by_date[date_key].append(meal)
        daily_totals[date_key]['calories'] += meal.get_total_calories()
        daily_totals[date_key]['protein'] += meal.get_total_protein()
        daily_totals[date_key]['carbs'] += meal.get_total_carbs()
        daily_totals[date_key]['fat'] += meal.get_total_fat()
    
    # Sort dates descending
    sorted_dates = sorted(meals_by_date.keys(), reverse=True)
    
    context = {
        'meals_by_date': meals_by_date,
        'daily_totals': daily_totals,
        'sorted_dates': sorted_dates,
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'total_entries': meal_logs.count()
    }
    
    return render(request, 'FitBuddy_app/meal_history.html', context)
