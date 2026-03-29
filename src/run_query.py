import sys
import os
import json
import argparse
import time
from agents import MultiAgentSystem
from safety import SafetyGuard

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Router Query Execution")
    parser.add_argument("--query", type=str, required=True, help="Pregunta del usuario")
    args = parser.parse_args()
    
    query = args.query
    system = MultiAgentSystem()
    safety = SafetyGuard()
    
    print(f"--- Solicitud recibida: '{query}' ---")
    
    # 1. Paso de Seguridad
    is_unsafe, reason = safety.is_adversarial(query)
    if is_unsafe:
        print(f"!!! SEGURIDAD: {reason}")
        output = safety.fallback_response(reason)
        
        # Guardar métricas de seguridad (0 tokens, pero registramos el evento)
        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "total_tokens": 0,
            "latency_ms": 0,
            "estimated_cost_usd": 0.0
        }
        
        final_output = {
            "query": query,
            "routing": {"intent": "SAFETY_BLOCKED", "confidence": 1.0, "reason": reason},
            "response": output,
            "metrics": metrics
        }
        
        save_output(final_output)
        save_history(final_output)
        save_metrics_log(metrics)
        
        print(json.dumps(output, indent=4, ensure_ascii=False))
        return

    # 2. Paso de Ruteo
    print("  Enrutando...")
    routing_result = system.route_query(query)
    intent_data = routing_result["data"]
    router_metrics = routing_result["metrics"]
    
    print(f"  Intento: {intent_data.intent} (Confianza: {intent_data.confidence:.2f})")
    print(f"  Razón: {intent_data.reason}")

    # 3. Paso de Especialista
    print(f"  Invocando Especialista -> {intent_data.intent}")
    specialist_result = system.handle_specialist(query, intent_data)
    final_data = specialist_result["data"]
    specialist_metrics = specialist_result["metrics"]
    
    # 4. Consolidación de Métricas
    total_metrics = {
        "timestamp": specialist_metrics["timestamp"],
        "tokens_prompt": router_metrics["tokens_prompt"] + specialist_metrics["tokens_prompt"],
        "tokens_completion": router_metrics["tokens_completion"] + specialist_metrics["tokens_completion"],
        "total_tokens": router_metrics["total_tokens"] + specialist_metrics["total_tokens"],
        "latency_ms": round(router_metrics["latency_ms"] + specialist_metrics["latency_ms"], 2),
        "estimated_cost_usd": round(router_metrics["estimated_cost_usd"] + specialist_metrics["estimated_cost_usd"], 5)
    }

    # 5. Salida Final
    final_output = {
        "query": query,
        "routing": intent_data.dict(),
        "response": final_data.dict(),
        "metrics": total_metrics
    }
    
    print("\n--- RESPUESTA FINAL ---")
    print(json.dumps(final_output["response"], indent=4, ensure_ascii=False))
    
    print("\n--- MÉTRICAS (Simuladas GPT-4o) ---")
    print(f"  Tokens: {total_metrics['total_tokens']}")
    print(f"  Latencia: {total_metrics['latency_ms']} ms")
    print(f"  Costo: ${total_metrics['estimated_cost_usd']} USD")
    
    save_output(final_output)
    save_history(final_output)
    save_metrics_log(total_metrics)

def save_output(data):
    # Guardar la última respuesta
    with open("metrics/latest_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_metrics_log(metrics):
    # Guardar en un log histórico
    log_file = "metrics/metrics.json"
    history = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []
    
    history.append(metrics)
    with open(log_file, "w") as f:
        json.dump(history, f, indent=4)

def save_history(data):
    # Guardar en un historial completo (Pregunta, Respuesta, Métricas)
    log_file = "metrics/history.json"
    history = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except:
                history = []
    
    history.append(data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
