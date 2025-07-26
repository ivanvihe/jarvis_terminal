import requests
from datetime import datetime
from config_loader import AI_PROVIDER, groq_key, openai_key, gemini_key, claude_key, DEBUG_AI

def ask_ai(prompt, memory):
    prompt_lower = prompt.lower()
    
    if DEBUG_AI:
        print(f"[DEBUG AI] Prompt recibido: {prompt}")
    
    # Respuesta rápida si se pregunta la hora
    if "hora" in prompt_lower:
        now = datetime.now().strftime("%H:%M")
        if DEBUG_AI:
            print(f"[DEBUG AI] Respuesta local: La hora actual es {now}.")
        return f"La hora actual es {now}."

    # Guardar en memoria si se solicita
    if any(x in prompt_lower for x in ["recorda que", "acuerdate que", "quiero que recuerdes"]):
        memory.append(prompt)
        memory.save()
        if DEBUG_AI:
            print("[DEBUG AI] Información guardada en memoria.")
        return "He guardado esa información."

    memory_context = "\n".join(memory.data)
    if DEBUG_AI and memory_context:
        print(f"[DEBUG AI] Contexto de memoria enviado al modelo:\n{memory_context}")

    try:
        if AI_PROVIDER == "groq":
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": f"Memoria: {memory_context}"},
                        {"role": "user", "content": prompt}]
            data = {"messages": messages, "model": "llama3-8b-8192", "max_tokens": 200, "temperature": 0.7}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
            if DEBUG_AI:
                print(f"[DEBUG AI] Groq respuesta HTTP: {r.status_code}")
            if r.ok:
                result = r.json()['choices'][0]['message']['content']
                if DEBUG_AI:
                    print(f"[DEBUG AI] Respuesta Groq: {result}")
                return result
            return "Groq no respondió correctamente."

        elif AI_PROVIDER == "openai":
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": f"Memoria: {memory_context}"},
                        {"role": "user", "content": prompt}]
            data = {"messages": messages, "model": "gpt-3.5-turbo", "max_tokens": 200, "temperature": 0.7}
            r = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
            if DEBUG_AI:
                print(f"[DEBUG AI] OpenAI respuesta HTTP: {r.status_code}")
            if r.ok:
                result = r.json()['choices'][0]['message']['content']
                if DEBUG_AI:
                    print(f"[DEBUG AI] Respuesta OpenAI: {result}")
                return result
            return "OpenAI no respondió correctamente."

        elif AI_PROVIDER == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
            data = {"contents": [{"parts": [{"text": memory_context + "\n" + prompt}]}]}
            r = requests.post(url, json=data)
            if DEBUG_AI:
                print(f"[DEBUG AI] Gemini respuesta HTTP: {r.status_code}")
            if r.ok:
                result = r.json()['candidates'][0]['content']['parts'][0]['text']
                if DEBUG_AI:
                    print(f"[DEBUG AI] Respuesta Gemini: {result}")
                return result
            return "Gemini no respondió correctamente."

        elif AI_PROVIDER == "claude":
            headers = {"x-api-key": claude_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
            data = {"model": "claude-3-haiku-20240307",
                    "messages": [{"role": "user", "content": memory_context + "\n" + prompt}],
                    "max_tokens": 200}
            r = requests.post("https://api.anthropic.com/v1/messages", json=data, headers=headers)
            if DEBUG_AI:
                print(f"[DEBUG AI] Claude respuesta HTTP: {r.status_code}")
            if r.ok:
                result = r.json()['content'][0]['text']
                if DEBUG_AI:
                    print(f"[DEBUG AI] Respuesta Claude: {result}")
                return result
            return "Claude no respondió correctamente."

        return "Proveedor AI no soportado."

    except Exception as e:
        print(f"❌ Error AI: {e}")
        if DEBUG_AI:
            import traceback
            print("[DEBUG AI] Excepción completa:")
            traceback.print_exc()
        return "Error procesando tu consulta."
