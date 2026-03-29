import json
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
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
    intent: str
    confidence: float
    reason: str

class SpecialistResponse(BaseModel):
    response_text: str
    next_steps: List[str]
    priority: str
    requires_supervisor: bool

# 3. Utilidades de Métricas
def calculate_cost(tokens_in: int, tokens_out: int) -> float:
    return (tokens_in / 1_000_000 * COST_INPUT_1M) + (tokens_out / 1_000_000 * COST_OUTPUT_1M)

def get_metrics(response: Any, start_time: float) -> Dict[str, Any]:
    metadata = response.response_metadata
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
    
    if provider == "openai":
        return ChatOpenAI(api_key=Config.OPENAI_API_KEY, model_name=model, temperature=0)
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

# 5. Orquestación de Agentes
class MultiAgentSystem:
    def __init__(self):
        Config.validate()
        self.llm = get_llm()
        self.router_parser = PydanticOutputParser(pydantic_object=RouterResponse)
        self.specialist_parser = PydanticOutputParser(pydantic_object=SpecialistResponse)

    def route_query(self, query: str) -> Dict[str, Any]:
        with open("prompts/router_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.llm
        
        start_time = time.time()
        response = chain.invoke({
            "query": query,
            "format_instructions": self.router_parser.get_format_instructions()
        })
        
        metrics = get_metrics(response, start_time)
        try:
            content = self.router_parser.parse(response.content)
            return {"data": content, "metrics": metrics}
        except:
            # Fallback simple si el JSON falla
            return {"data": RouterResponse(intent="GENERAL", confidence=0.5, reason="JSON fallback"), "metrics": metrics}

    def handle_specialist(self, query: str, routing: RouterResponse) -> Dict[str, Any]:
        roles = {
            "RECLAMOS": {"role": "Especialista en Reclamos y Gestión de Crisis", "tone": "Empático y Resolutivo"},
            "FINANZAS": {"role": "Especialista Financiero y Contable", "tone": "Formal y Preciso"},
            "SOPORTE_TECNICO": {"role": "Ingeniero de Soporte Nivel 2", "tone": "Técnico y Directo"},
            "GENERAL": {"role": "Asistente de Información General", "tone": "Informativo"}
        }
        
        config = roles.get(routing.intent, roles["GENERAL"])
        
        with open("prompts/specialist_prompt.md", "r", encoding="utf-8") as f:
            template_text = f.read()
            
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | self.llm
        
        start_time = time.time()
        response = chain.invoke({
            "role_description": config["role"],
            "tone": config["tone"],
            "query": query,
            "intent": routing.intent,
            "reason": routing.reason,
            "format_instructions": self.specialist_parser.get_format_instructions()
        })
        
        metrics = get_metrics(response, start_time)
        try:
            content = self.specialist_parser.parse(response.content)
            return {"data": content, "metrics": metrics}
        except:
            # Fallback simple
            return {"data": SpecialistResponse(response_text="Error procesando respuesta.", next_steps=[], priority="HIGH", requires_supervisor=True), "metrics": metrics}
