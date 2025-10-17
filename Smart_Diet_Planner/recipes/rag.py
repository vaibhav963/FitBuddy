import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning:.*")

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from .utils import get_recipes_data
from dotenv import load_dotenv
load_dotenv()

messages = [
    {"role": "human", "content": "Hello! My name is Mark. My age is 30, weight 70kgs, height 6ft 2in, and I'm looking to lose some weight following the keto diet. My dietary preferences are: I'm trying to eat more protein and fewer carbs. My allergies are: None"},
    {"role": "assistant", "content": "Hi there, Mark! I'd be happy to help you with your diet goals. I can suggest meals that suit your preferences. What would you like to know?"}
]

vectorstore = None 
llm = None 
compressor = None 
compression_retriever = None
memory = None  
retriever = None 


def init_components():
    global vectorstore, llm, compressor, compression_retriever, memory, retriever
    
    try:
        if all([vectorstore, llm, compressor, compression_retriever, memory]):
            return 
        
        print("Initializing components...")

        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        data = get_recipes_data()
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

        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)

        vectorstore_path = "faiss_index.index"

        if os.path.exists(vectorstore_path):
            vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
        else:
            vectorstore = FAISS.from_texts(documents, embeddings)
            vectorstore.save_local(vectorstore_path)

        retriever = vectorstore.as_retriever()

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
        compressor = LLMChainExtractor.from_llm(llm)
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

        memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="recent_history",
            input_key="input",
            k=10   
        )
        
        print("Components initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing components: {e}")
        raise e

def run_chain(query, history):
    try:
        init_components()
        global retriever, memory, messages
        
        system_template = """You are a concise diet coach and meal planner. Answer diet, recipe, and nutrition questions using only verified knowledge and provided context.
Response Format Requirements:

Keep responses under 150 words unless specifically asked for detailed explanations
Use bullet points for ingredients and instructions
Include only essential information

Required Structure:

Recipe Name: [Name]
Time: [Prep + Cook time]
Serves: [Number]
Diet Type: [Keto/Paleo/Vegan/etc.]
Cuisine: [Type]

Ingredients: (max 8 items)

[List concisely]

Instructions: (max 4 steps)

[Brief step]
[Brief step]

Macros per serving:

Calories: [number]
Protein: [g] | Carbs: [g] | Fat: [g]

Key Guidelines:

Prioritize accuracy over completeness
Skip explanatory text unless asked
Focus on practical, actionable information
If unsure about nutritional data, state "approximate values"

Context: {context}"""

        system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "{question}"
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

        chain = chat_prompt | llm | StrOutputParser()

        # Build conversation context
        for i in range(0, len(messages), 2):
            if i+1 < len(messages):
                human_msg = messages[i]["content"]
                ai_msg = messages[i+1]["content"]
                memory.save_context({"input": human_msg}, {"output": ai_msg})
        
        # Get recent conversation history
        recent_history = memory.load_memory_variables({})["recent_history"]
        
        # Retrieve relevant documents
        docs = retriever.invoke(query)
        doc_content = "\n".join([doc.page_content for doc in docs])
        context = f"{recent_history}\n{doc_content}"
        
        # Generate response
        response = chain.invoke({"context": context, "question": query})
        memory.save_context({"input": query}, {"output": response})
        
        # Update history
        history.append({"role": "human", "content": query})
        history.append({"role": "assistant", "content": response})

        return response, history
        
    except Exception as e:
        print(f"Error in run_chain: {e}")
        # Add user query to history even if AI response fails
        history.append({"role": "human", "content": query})
        
        # Provide a fallback response based on error type
        if "quota" in str(e).lower() or "429" in str(e):
            fallback_response = "I'm currently experiencing high usage. Please try again in a moment, or browse our recipe collection in the meantime."
        elif "api" in str(e).lower() or "key" in str(e).lower():
            fallback_response = "I'm having trouble accessing my knowledge base right now. Please try again later."
        else:
            fallback_response = "I encountered an issue processing your request. Could you try rephrasing your question? I'm here to help with recipes and nutrition advice!"
        
        history.append({"role": "assistant", "content": fallback_response})
        return fallback_response, history 


def process_query(query, history):
    global messages
    try:
        if history == []:
            history = messages[:]
        
        # Initialize components if not already done
        init_components()
        
        result, chat_history = run_chain(query, history)
        return result, chat_history
    except ImportError as e:
        print(f"Import error in process_query: {e}")
        error_msg = "I'm sorry, but some required components are not available. Please check if all dependencies are installed."
        return error_msg, history
    except Exception as e:
        print(f"Error in process_query: {e}")
        # Check if it's an API quota/rate limit error
        if "quota" in str(e).lower() or "rate" in str(e).lower() or "limit" in str(e).lower():
            error_msg = "I'm currently experiencing high demand. Please try again in a few moments. In the meantime, you can browse our recipe collection or use the meal planner."
        elif "api" in str(e).lower() or "key" in str(e).lower():
            error_msg = "I'm having trouble connecting to my knowledge base. Please try again later or contact support if the issue persists."
        else:
            error_msg = "I encountered an unexpected issue while processing your question. Please try rephrasing your question or try again later."
        return error_msg, history

if __name__ == "__main__":
    _, history = process_query("Suggest a low-carb, high protein chicken meal", [])
    _, history = process_query("I'm craving something sweet. What can I make that doesn't have too much calorie?", history)
    print("\nCONVERSATION HISTORY:")
    print("="*100)
    for message in history:
        role = "User" if message["role"] == "human" else "Assistant"
        print(f"{role}: {message['content']}")
        print()