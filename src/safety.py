from typing import Tuple, Dict, Any

class SafetyGuard:
    @staticmethod
    def is_adversarial(query: str) -> Tuple[bool, str]:
        """Detección simple de prompts adversarios."""
        forbidden_patterns = [
            "ignore all previous instructions",
            "olas de prompt anterior",
            "dan modo",
            "escribe el sistema interno",
            "revelar configuración",
            "delete system files",
            "hack"
        ]
        
        query_lower = query.lower()
        for pattern in forbidden_patterns:
            if pattern in query_lower:
                return True, f"Patrón prohibido detectado: {pattern}"
                
        return False, ""

    @staticmethod
    def fallback_response(reason: str) -> Dict[str, Any]:
        """Respuesta de seguridad predefinida."""
        return {
            "response_text": "Lo sentimos, la solicitud no cumple con nuestras políticas de seguridad.",
            "next_steps": ["Contactar a un supervisor humano"],
            "priority": "CRITICAL",
            "requires_supervisor": True,
            "safety_reason": reason
        }
