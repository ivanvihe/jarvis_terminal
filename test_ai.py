from ai import ask_ai
from memory import Memory

mem = Memory()

prompt = "¿Qué hora es?"
response = ask_ai(prompt, mem)
print("Respuesta AI:", response)
