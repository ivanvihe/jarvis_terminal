# ai.py - Módulo básico de IA

import time
from config_loader import AI_PROVIDER, groq_key, openai_key, gemini_key, claude_key

def ask_ai(query, memory=None):
    """
    Función principal para hacer consultas a la IA
    """
    try:
        # Si tienes configurado Groq
        if AI_PROVIDER == "groq" and groq_key:
            return ask_groq(query, memory)
        # Si tienes configurado OpenAI
        elif AI_PROVIDER == "openai" and openai_key:
            return ask_openai(query, memory)
        # Si tienes configurado Gemini
        elif AI_PROVIDER == "gemini" and gemini_key:
            return ask_gemini(query, memory)
        # Fallback: respuesta local básica
        else:
            return ask_local(query, memory)
            
    except Exception as e:
        return f"Error procesando consulta: {e}"

def ask_groq(query, memory=None):
    """Consulta usando Groq API"""
    try:
        from groq import Groq
        
        client = Groq(api_key=groq_key)
        
        # Construir contexto
        context = ""
        if memory and hasattr(memory, 'get_context'):
            context = memory.get_context()
        
        messages = [
            {"role": "system", "content": "Eres Jarvis, un asistente virtual útil y amigable. Responde de forma concisa y directa."}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Contexto previo: {context}"})
            
        messages.append({"role": "user", "content": query})
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        return "Error: Librería 'groq' no instalada. Usa: pip install groq"
    except Exception as e:
        return f"Error en Groq API: {e}"

def ask_openai(query, memory=None):
    """Consulta usando OpenAI API"""
    try:
        import openai
        
        openai.api_key = openai_key
        
        # Construir contexto
        context = ""
        if memory and hasattr(memory, 'get_context'):
            context = memory.get_context()
        
        messages = [
            {"role": "system", "content": "Eres Jarvis, un asistente virtual útil y amigable. Responde de forma concisa y directa."}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Contexto previo: {context}"})
            
        messages.append({"role": "user", "content": query})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        return "Error: Librería 'openai' no instalada. Usa: pip install openai"
    except Exception as e:
        return f"Error en OpenAI API: {e}"

def ask_gemini(query, memory=None):
    """Consulta usando Gemini API"""
    return "Gemini no implementado aún. Configurando..."

def ask_local(query, memory=None):
    """Respuesta local básica cuando no hay APIs configuradas"""
    
    query_lower = query.lower()
    
    # Respuestas básicas
    if any(word in query_lower for word in ["hora", "time"]):
        import datetime
        now = datetime.datetime.now()
        return f"Son las {now.strftime('%H:%M:%S')} del {now.strftime('%d/%m/%Y')}"
    
    elif any(word in query_lower for word in ["fecha", "date"]):
        import datetime
        now = datetime.datetime.now()
        return f"Hoy es {now.strftime('%d de %B de %Y')}"
    
    elif any(word in query_lower for word in ["hola", "hello", "hi"]):
        return "¡Hola! Soy Jarvis, tu asistente virtual. ¿En qué puedo ayudarte?"
    
    elif any(word in query_lower for word in ["gracias", "thanks"]):
        return "¡De nada! Estoy aquí para ayudarte."
    
    elif any(word in query_lower for word in ["como estas", "how are you"]):
        return "Estoy funcionando perfectamente, gracias por preguntar. ¿Y tú qué tal?"
    
    elif any(word in query_lower for word in ["clima", "weather", "tiempo"]):
        return "Lo siento, no tengo acceso a información meteorológica en este momento. Puedes consultar tu app de clima favorita."
    
    else:
        return f"He recibido tu consulta: '{query}'. Como no tengo configurada una API de IA, esta es una respuesta básica. Para funcionalidad completa, configura tu API key en config.json."