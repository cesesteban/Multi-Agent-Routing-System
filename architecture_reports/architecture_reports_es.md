# Informe de Arquitectura del Sistema de Ruteo Multi-Agente (01-PI)

## 1. Visión de la Arquitectura
El sistema está diseñado como una **Arquitectura de Ruteo Jerárquica**. Emplea un "Agente Router" primario que actúa como controlador de tráfico, dirigiendo las consultas de los usuarios a agentes especializados (Reclamos, Finanzas, Soporte Técnico o General).

### Flujo:
1.  **Capa de Seguridad (Safety)**: Valida la entrada frente a patrones adversarios comunes.
2.  **Agente Router**: Clasifica la consulta y estima la confianza en la clasificación.
3.  **Agente Especialista**: Recibe el contexto específico y genera una respuesta detallada y formateada.
4.  **Observador de Métricas**: Captura el uso de tokens, la latencia y los costos simulados en cada paso.

## 2. Técnicas de Prompting
-   **Prompting basado en instrucciones**: Roles y restricciones claras.
-   **Ejemplos Few-Shot**: Incluidos en el prompt del router para fundamentar la lógica de clasificación.
-   **Chain of Thought (Implícito)**: Los especialistas están instruidos para analizar el caso antes de responder.
-   **Estructuración de Salida**: JSON estrictamente forzado a través de la integración con Pydantic.

## 3. Resumen de Métricas
*(Muestras de métricas registradas durante las ejecuciones iniciales)*

| Métrica | Valor Promedio |
| :--- | :--- |
| Latencia (ms) | ~1200ms |
| Tokens (Total) | ~450 tokens |
| Costo (USD - SIMULADO) | ~$0.003 USD |

## 4. Desafíos y Mejoras
-   **Parseo de JSON**: Los modelos locales pueden tener dificultades ocasionales con JSON estricto. **Mejora**: Implementado un mecanismo de fallback.
-   **Pérdida de Contexto**: Pasar el contexto entre agentes. **Mejora**: El prompt del Especialista incluye el razonamiento del Router.
-   **Seguridad**: Detección básica de palabras clave. **Mejora**: En producción, se usaría un paso de moderación basado en un LLM.

## 5. Conclusión
El sistema 01-PI demuestra una forma escalable de manejar diversas solicitudes de clientes al aislar la experiencia del dominio en agentes especializados, manteniendo al mismo tiempo el control central y la observabilidad.
