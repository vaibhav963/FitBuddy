"""
Script to regenerate FAISS index for the chatbot
Run this if FAISS files are missing or corrupted
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning:.*")

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from recipes.utils import get_recipes_data
from dotenv import load_dotenv
import shutil

load_dotenv()

def regenerate_faiss_index():
    """Regenerate the FAISS index from scratch"""
    
    print("🔄 Regenerating FAISS index...")
    
    # Check if API key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("💡 Please add your Google API key to the .env file")
        return False
    
    try:
        # Remove existing corrupted files
        vectorstore_path = "faiss_index.index"
        pkl_path = "faiss_index.pkl"
        
        if os.path.exists(vectorstore_path):
            print(f"🗑️ Removing existing directory: {vectorstore_path}")
            shutil.rmtree(vectorstore_path)
            
        if os.path.exists(pkl_path):
            print(f"🗑️ Removing existing file: {pkl_path}")
            os.remove(pkl_path)
        
        # Get recipe data
        print("📚 Loading recipe data...")
        data = get_recipes_data()
        print(f"✅ Loaded {len(data)} recipes")
        
        # Create documents
        print("📝 Creating documents...")
        documents = []
        for recipe in data:
            text = f"Recipe: {recipe['recipe_name']}\n"
            text += f"Cuisine: {recipe['cuisine']}\n"
            text += f"Type: {recipe['type']}\n"
            text += f"Ingredients: {recipe['ingredients']}\n"
            text += f"Instructions: {recipe['instructions']}\n"
            text += f"Nutritional Information:\n"
            text += f"- Calories: {recipe['calories']}\n"
            text += f"- Fat: {recipe['fat']}g\n"
            text += f"- Saturated Fat: {recipe['saturated_fat']}g\n"
            text += f"- Cholesterol: {recipe['cholesterol']}mg\n"
            text += f"- Sodium: {recipe['sodium']}mg\n"
            text += f"- Carbohydrate: {recipe['carbohydrate']}g\n"
            text += f"- Fiber: {recipe['fiber']}g\n"
            text += f"- Sugar: {recipe['sugar']}g\n"
            text += f"- Protein: {recipe['protein']}g\n"
            documents.append(text)
        
        print(f"✅ Created {len(documents)} documents")
        
        # Create embeddings
        print("🧠 Creating embeddings (this may take a few minutes)...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=api_key
        )
        
        # Create and save FAISS vectorstore
        print("💾 Creating FAISS vectorstore...")
        vectorstore = FAISS.from_texts(documents, embeddings)
        
        print("💾 Saving FAISS index...")
        vectorstore.save_local(vectorstore_path)
        
        # Verify the files were created
        if os.path.exists(vectorstore_path) and os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
            print("✅ FAISS index created successfully!")
            print(f"📁 Files created:")
            print(f"   - {vectorstore_path}/")
            
            # List files in the directory
            for file in os.listdir(vectorstore_path):
                file_path = os.path.join(vectorstore_path, file)
                size = os.path.getsize(file_path)
                print(f"   - {file} ({size} bytes)")
            
            return True
        else:
            print("❌ Error: FAISS index files were not created properly")
            return False
            
    except Exception as e:
        print(f"❌ Error creating FAISS index: {e}")
        return False

def test_faiss_index():
    """Test if the FAISS index works correctly"""
    
    print("\n🧪 Testing FAISS index...")
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=api_key
        )
        
        vectorstore_path = "faiss_index.index"
        vectorstore = FAISS.load_local(
            vectorstore_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Test search
        results = vectorstore.similarity_search("chicken recipe", k=2)
        
        print(f"✅ FAISS index test successful!")
        print(f"📋 Found {len(results)} test results")
        if results:
            print(f"📄 Sample result: {results[0].page_content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAISS index test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 FAISS Index Recovery Tool")
    print("=" * 50)
    
    success = regenerate_faiss_index()
    
    if success:
        test_success = test_faiss_index()
        if test_success:
            print("\n🎉 FAISS index successfully regenerated and tested!")
            print("💬 Your chatbot should now work properly!")
        else:
            print("\n⚠️ FAISS index was created but test failed")
            print("🔧 The chatbot might still have issues")
    else:
        print("\n❌ Failed to regenerate FAISS index")
        print("🔧 Please check your API key and try again")