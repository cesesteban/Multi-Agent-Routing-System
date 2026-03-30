import sys
import os
import json
import argparse
import time
from agents import MultiAgentSystem, SpecialistResponse
from safety import SafetyGuard
from context_eng import ContextEngineer
from config import Config

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Router Query Execution")
    parser.add_argument("--query", type=str, required=True, help="Pregunta del usuario")
    args = parser.parse_args()
    
    query = args.query
    system = MultiAgentSystem()
    safety = SafetyGuard()
    context_eng = ContextEngineer()
    
    print(f"--- Solicitud recibida: '{query}' ---")
    
    # 1. Pre-procesamientos (Limpieza y Seguridad)
    ctx = context_eng.build_context_packet(query)
    clean_query = ctx["clean_query"]
    
    is_unsafe, reason = safety.is_adversarial(clean_query)
    if is_unsafe:
        print(f"!!! SEGURIDAD: {reason}")
        output = safety.fallback_response(reason)
        
        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tokens_prompt": 0, "tokens_completion": 0, "total_tokens": 0,
            "latency_ms": 0, "estimated_cost_usd": 0.0
        }
        
        final_output = {
            "query": query,
            "routing": {"intent": "SAFETY_BLOCKED", "confidence": 1.0, "reason": reason},
            "response": output,
            "metrics": metrics
        }
        
        save_output(final_output)
        save_history(final_output)
        return

    # 2. Orquestación Multi-Agente
    print("  Analizando intención (Coordinador)...")
    routing_result = system.route_query(clean_query)
    intent_data = routing_result["data"]
    
    print(f"  Destino: {intent_data.intent} (Confianza: {intent_data.confidence:.2f})")

    # 3. Ciclo Especialista - Auditor (Feedback Loop)
    attempts = 0
    max_attempts = 3
    feedback = ""
    audit_history = []
    context_used = ""
    
    while attempts < max_attempts:
        attempts += 1
        print(f"  [{attempts}/{max_attempts}] Generando/Refinando respuesta...")
        
        specialist_result = system.handle_specialist(clean_query, intent_data, feedback=feedback)
        final_data = specialist_result["data"]
        context_used = specialist_result.get("context_used", "")
        
        print(f"  [{attempts}/{max_attempts}] Ejecutando Auditoría de Calidad...")
        audit_result = system.audit_and_refine(clean_query, final_data)
        critic_data = audit_result["data"]
        audit_history.append(critic_data.model_dump())
        
        if critic_data.is_valid:
            print(f"  [OK] Auditoría APROBADA (Score: {critic_data.score})")
            break
        else:
            print(f"  [AVISO] Auditoría RECHAZADA: {', '.join(critic_data.issues)}")
            feedback = f"Issues detectados: {', '.join(critic_data.issues)}. Sugerencia: {critic_data.suggestions}"
            if attempts < max_attempts:
                print(f"  [ACCIÓN] Re-intentando con retroalimentación...")

    # 4. Agente Evaluador RAG (Bonus)
    print("  [Bonus] Ejecutando Agente Evaluador RAG...")
    eval_result = system.evaluate_response(clean_query, final_data.response_text)
    evaluation = eval_result["data"]
    print(f"  [Score] Calidad RAG: {evaluation.final_score}/10")

    # 5. Generación de Payload Enriquecido
    total_metrics = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_tokens": routing_result["metrics"]["total_tokens"] + (specialist_result["metrics"]["total_tokens"] * attempts) + (audit_result["metrics"]["total_tokens"] * attempts),
        "latency_ms": round(routing_result["metrics"]["latency_ms"] + (specialist_result["metrics"]["latency_ms"] * attempts) + (audit_result["metrics"]["latency_ms"] * attempts) + eval_result["metrics"]["latency_ms"], 2),
        "estimated_cost_usd": round(routing_result["metrics"]["estimated_cost_usd"] + (specialist_result["metrics"]["estimated_cost_usd"] * attempts) + (audit_result["metrics"]["estimated_cost_usd"] * attempts), 5)
    }

    final_output = {
        "__system": {
            "model": Config.MODEL_NAME,
            "context_hash": ctx["context_hash"],
            "attempts": attempts,
            "rag_context": context_used[:200] + "..." if context_used else None
        },
        "query": query,
        "routing": intent_data.model_dump(),
        "audit_trace": audit_history,
        "evaluation": evaluation.model_dump(),
        "response": final_data.model_dump(),
        "metrics": total_metrics
    }
    
    print("\n" + "="*50)
    print("--- RESULTADO FINAL (CORE + RAG + EVAL) ---")
    print("="*50)
    # ... [Rest is formatting]
    print(f"\nRazonamiento (CoT):")
    for step in final_data.chain_of_thought:
        print(f"  - {step}")
    
    print(f"\nRespuesta:\n{final_data.response_text}")
    print(f"\nPrioridad: {final_data.priority}")
    print(f"Próximos Pasos: {', '.join(final_data.next_steps)}")
    
    print("\n" + "-"*50)
    print("MÉTRICAS DE SISTEMA")
    print(f"Latencia Total: {total_metrics['latency_ms']} ms")
    print(f"Costo Estimado: ${total_metrics['estimated_cost_usd']}")
    print("-"*50)
    
    save_output(final_output)
    save_history(final_output)
    save_metrics_log(total_metrics)

def save_output(data):
    with open("metrics/latest_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_metrics_log(metrics):
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
