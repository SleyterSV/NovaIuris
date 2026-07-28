import requests
import json
import time

# Esta es la URL de tu API local (asegúrate de que Flask esté corriendo)
API_URL = "http://127.0.0.1:5001/api/simulation/court/simulate"

# 1. El usuario selecciona la tarjeta "Derecho Penal" y escribe su caso en la plataforma:
payload_desde_la_web = {
    "dominio": "Derecho Penal",
    "profundidad": "Alta",
    "caso": "El trabajador Juan Pérez fue despedido sin previo aviso por llegar tarde 3 veces. Exige reposición."
}

print("🌐 [WEB] Usuario hizo clic en 'Iniciar Simulación'...")
print("⏳ [WEB] Mostrando barra de progreso: 'Recuperando normativa...'")

# 2. La web envía los datos a tu servidor de forma invisible
start_time = time.time()
try:
    respuesta = requests.post(API_URL, json=payload_desde_la_web)
    datos_recibidos = respuesta.json()
    
    tiempo_total = round(time.time() - start_time, 2)
    
    # 3. La web recibe el JSON y lo renderiza en tu dashboard profesional
    if datos_recibidos.get("success"):
        data = datos_recibidos["data"]
        print(f"\n✅ [WEB] Simulación completada en {tiempo_total} segundos.")
        print("="*60)
        print(f"📁 ID DEL EXPEDIENTE: {data.get('session_id')}")
        print("="*60)
        
        print("\n⚖️ RENDERIZANDO PESTAÑA: BASE JURÍDICA")
        print(data.get("base_legal")[:150] + "...\n(Continúa en la UI...)")
        
        print("\n👨‍⚖️ RENDERIZANDO INTERACCIÓN: FISCAL")
        print(data.get("fiscal")[:150] + "...\n(Continúa en la UI...)")
        
        print("\n🛡️ RENDERIZANDO INTERACCIÓN: DEFENSA")
        print(data.get("defensa")[:150] + "...\n(Continúa en la UI...)")
        
        print("\n⚖️ RENDERIZANDO RESULTADO: JUEZ")
        print(data.get("juez")[:150] + "...\n(Continúa en la UI...)")
        
    else:
        print("\n❌ [WEB] Error mostrado al usuario:", datos_recibidos.get("error"))

except Exception as e:
    print(f"\n❌ [WEB] El servidor no está corriendo. Error: {e}")