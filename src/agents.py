import json
import time
import os
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
from rag import RAGManager
from config import Config

# Intentar importar proveedores opcionales
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

# 1. Constantes de Costo (Simulación GPT-4o)
COST_INPUT_1M = 5.00
COST_OUTPUT_1M = 15.00

# 2. Modelos de Datos (Pydantic)
class RouterResponse(BaseModel):
    """Modelo para la respuesta del coordinador de ruteo."""
    chain_of_thought: List[str] = Field(description="4 pasos de razonamiento (Señales, Estrategia, Riesgos, Clasificación)")
    intent: str = Field(description="Categoría destino (RRHH, TECNOLOGIA, FINANZAS, RECLAMOS, GENERAL)")
    confidence: float = Field(description="Nivel de certidumbre en la clasificación (0.0-1.0)")
    reason: str = Field(description="Justificación breve del destino elegido")

class SpecialistResponse(BaseModel):
    """Modelo para la respuesta detallada de los especialistas."""
    chain_of_thought: List[str] = Field(description="4 pasos de razonamiento (Análisis, Estrategia, Riesgos, Solución)")
    response_text: str = Field(description="Respuesta directa al usuario")
    next_steps: List[str] = Field(description="Tareas o seguimiento recomendado")
    priority: str = Field(description="Nivel de urgencia detectado (BAJA, MEDIA, ALTA, CRÍTICA)")
    requires_supervisor: bool = Field(description="Define si el caso debe ser escalado a un humano de inmediato")
    avoid: List[str] = Field(description="Lo que se decidió NO decir o evitar en esta respuesta")
    tone_notes: List[str] = Field(description="Notas sobre el tono aplicado (ej. empático, formal)")
    why_it_works: List[str] = Field(description="Justificación técnica de por qué esta respuesta es efectiva para el usuario")

class CriticResponse(BaseModel):
    """Modelo para la auditoría técnica de las respuestas."""
    is_valid: bool = Field(description="Define si la respuesta cumple con los estándares de calidad")
    issues: List[str] = Field(description="Problemas detectados (ambigüedad, tono incorrecto, falta de datos)")
    suggestions: str = Field(description="Sugerencias de mejora para el especialista")
    score: float = Field(description="Calificación de calidad (0.0-1.0)")

class EvaluatorResponse(BaseModel):
    """Modelo para la evaluación automática de RAG en Langfuse."""
    accuracy_score: int = Field(description="Puntaje de precisión del 1 al 10")
    relevance_score: int = Field(description="Puntaje de relevancia del 1 al 10")
    groundedness_score: int = Field(description="Puntaje de fundamentación del 1 al 10")
    final_score: float = Field(description="Puntaje final promedio del 1 al 10")
    justification: str = Field(description="Justificación detallada del puntaje asignado")

# 3. Utilidades del Sistema
def calculate_cost(tokens_in: int, tokens_out: int) -> float:
    return (tokens_in / 1_000_000 * COST_INPUT_1M) + (tokens_out / 1_000_000 * COST_OUTPUT_1M)

def get_metrics(response: Any, start_time: float) -> Dict[str, Any]:
    # Soporte para extracción de metadatos de tokens y latencia
    metadata = getattr(response, "response_metadata", {})
    token_usage = metadata.get("token_usage", {})
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    total_tokens = token_usage.get("total_tokens", 0)
    latency = (time.time() - start_time) * 1000
    
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tokens_prompt": prompt_tokens,
        "tokens_completion": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency, 2),
        "estimated_cost_usd": calculate_cost(prompt_tokens, completion_tokens)
    }

# 4. Factory de LLM
def get_llm():
    provider = Config.LLM_PROVIDER
    model = Config.MODEL_NAME
    api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else "lm-studio"
    
    if provider == "openai":
        return ChatOpenAI(api_key=api_key, model_name=model, temperature=0).with_fallbacks([
            ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0)
        ])
    elif provider == "groq":
        if not ChatGroq:
            raise ImportError("Error: 'langchain-groq' no está instalado.")
        return ChatGroq(api_key=Config.GROQ_API_KEY, model_name=model, temperature=0)
    elif provider == "gemini":
        if not ChatGoogleGenerativeAI:
            raise ImportError("Error: 'langchain-google-genai' no está instalado.")
        return ChatGoogleGenerativeAI(google_api_key=Config.GOOGLE_API_KEY, model=model, temperature=0)
    elif provider == "lm_studio":
        return ChatOpenAI(
            base_url=Config.LM_STUDIO_BASE_URL,
            api_key="lm-studio",
            model_name=model,
            temperature=0
        )
    else:
        raise ValueError(f"Proveedor LLM no soportado: {provider}")

# 5. Sistema Multi-Agente
class MultiAgentSystem:
    def __init__(self):
        Config.validate()
        self.raw_llm = get_llm()
        self.rag = RAGManager()
        
        # Inicialización de Langfuse
        self.langfuse_handler = None
        self.langfuse_client = None
        if Config.LANGFUSE_PUBLIC_KEY and Config.LANGFUSE_SECRET_KEY:
            self.langfuse_handler = CallbackHandler()
            self.langfuse_client = Langfuse(
                public_key=Config.LANGFUSE_PUBLIC_KEY,
                secret_key=Config.LANGFUSE_SECRET_KEY,
                host=Config.LANGFUSE_HOST
            )
		
        
        # Inicialización con Salida Estructurada Nativa
        self.router_llm = self.raw_llm.with_structured_output(RouterResponse)
        self.specialist_llm = self.raw_llm.with_structured_output(SpecialistResponse)
        self.critic_llm = self.raw_llm.with_structured_output(CriticResponse)
        self.evaluator_llm = self.raw_llm.with_structured_output(EvaluatorResponse)

    def route_query(self, query: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Clasifica la intención del usuario utilizando el prompt del coordinador."""
        with open("prompts/router_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.router_llm
        
        start_time = time.time()
        
        # Configuración de callbacks
        config = {"callbacks": [self.langfuse_handler]} if self.langfuse_handler else {}
        
        content = chain.invoke({"query": query}, config=config)
        
        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tokens_prompt": len(query) // 4,
            "tokens_completion": 50,
            "total_tokens": (len(query) // 4) + 50,
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "estimated_cost_usd": 0.001 
        }
        
        return {"data": content, "metrics": metrics}

    def handle_specialist(self, query: str, routing: RouterResponse, feedback: str = "") -> Dict[str, Any]:
        """Deriva la consulta al especialista adecuado según la intención detectada."""
        roles = {
            "RRHH": {"role": "Especialista en Recursos Humanos y Cultura", "tone": "Profesional y Atento"},
            "TECNOLOGIA": {"role": "Ingeniero de Soporte Técnico Senior", "tone": "Técnico y Directo"},
            "RECLAMOS": {"role": "Especialista en Reclamos y Gestión de Crisis", "tone": "Empático y Resolutivo"},
            "FINANZAS": {"role": "Especialista Financiero y Contable", "tone": "Formal y Preciso"},
            "GENERAL": {"role": "Asistente de Información General", "tone": "Informativo"}
        }
        
        config_role = roles.get(routing.intent, roles["GENERAL"])
        
        # Recuperación RAG (Habilitado para todas las categorías)
        context = ""
        valid_rag_intents = ["RRHH", "TECNOLOGIA", "FINANZAS", "RECLAMOS", "GENERAL"]
        if routing.intent in valid_rag_intents:
            print(f"  [RAG] Recuperando contexto para {routing.intent}...")
            context = self.rag.retrieve_context(query, routing.intent)
        
        with open("prompts/specialist_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.specialist_llm
        
        start_time = time.time()
        llm_config = {"callbacks": [self.langfuse_handler]} if self.langfuse_handler else {}
        
        content = chain.invoke({
            "role_description": config_role["role"],
            "tone": config_role["tone"],
            "query": query,
            "intent": routing.intent,
            "reason": routing.reason,
            "context": context if context else "No se encontró información específica en la base de datos.",
            "feedback": feedback
        }, config=llm_config)
        
        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tokens_prompt": len(query) // 4,
            "tokens_completion": 100,
            "total_tokens": (len(query) // 4) + 100,
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "estimated_cost_usd": 0.002
        }
        
        return {"data": content, "metrics": metrics, "context_used": context}

    def audit_and_refine(self, query: str, specialist_data: SpecialistResponse) -> Dict[str, Any]:
        """Realiza una auditoría técnica y refina la respuesta si es necesario (Feedback Loop)."""
        with open("prompts/critic_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.critic_llm
        
        start_time = time.time()
        llm_config = {"callbacks": [self.langfuse_handler]} if self.langfuse_handler else {}
        
        audit_result = chain.invoke({
            "query": query,
            "response_text": specialist_data.response_text,
            "reasoning": "\n".join(specialist_data.chain_of_thought)
        }, config=llm_config)
        
        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tokens_prompt": 200,
            "tokens_completion": 50,
            "total_tokens": 250,
            "latency_ms": round((time.time() - start_time) * 1000, 2),
            "estimated_cost_usd": 0.0005
        }
        
        return {"data": audit_result, "metrics": metrics}

    def evaluate_response(self, query: str, response_text: str) -> Dict[str, Any]:
        """Agente Evaluador que asigna puntaje y lo envía a Langfuse."""
        with open("prompts/evaluator_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.evaluator_llm
        
        start_time = time.time()
        llm_config = {"callbacks": [self.langfuse_handler]} if self.langfuse_handler else {}
        
        eval_result = chain.invoke({
            "query": query,
            "response_text": response_text
        }, config=llm_config)
        
        # Registrar puntaje en Langfuse si está disponible
        if self.langfuse_client:
            try:
                self.langfuse_client.score(
                    name="rag_quality",
                    value=eval_result.final_score,
                    comment=eval_result.justification
                )
            except Exception as e:
                print(f"  [Error Langfuse Score] {e}")

        metrics = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
        
        return {"data": eval_result, "metrics": metrics}
