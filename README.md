# Multi-Agent Routing System (01-PI)

[Español](#español) | [English](#english)

---

## English

This project implements a multi-agent system for handling customer requests using specialized routing.

### Requirements
- **Python 3.10+**.
- **LLM Provider**: The system is compatible with **LM Studio**, **OpenAI**, **Groq**, and **Gemini**.

### Configuration
1.  Copy the example file to create your configuration:
    ```bash
    cp .env.example .env
    ```
2.  Edit the `.env` file to select your `LLM_PROVIDER` and add your API keys. By default, the system will attempt to connect to a local **LM Studio** server at `http://localhost:1234/v1`.

### Installation
1.  Clone the repository or enter the `01-PI` folder.
2.  Install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```

### Execution
To query the system, use the `run_query.py` script inside `src/`:

```powershell
python src/run_query.py --query "When does my next invoice expire?"
```

Query examples:
-   `--query "I am not satisfied with the support service"` (Routes to RECLAMOS/COMPLAINTS)
-   `--query "The app gives me a network error at startup"` (Routes to SOPORTE_TECNICO/TECH_SUPPORT)
-   `--query "IGNORE ALL PREVIOUS INSTRUCTIONS"` (Blocked by SAFETY)

### Project Structure
-   `src/`: Main application (routing, agents, safety, context engineering).
-   `src/context_eng.py`: Context cleaning and normalization layer.
-   `prompts/`: High-quality role-based prompt definitions.
-   `metrics/`: Historical record of latency, usage, and simulated costs.
-   `architecture_reports/`: Architecture and design reports ([EN](architecture_reports/architecture_reports_en.md) | [ES](architecture_reports/architecture_reports_es.md)).
-   `tests/`: Validation unit tests.

### Key System Capabilities
-   **Native Structured Output**: Utiliza `with_structured_output` para garantizar respuestas 100% parseables mediante esquemas Pydantic.
-   **Granular Chain-of-Thought (CoT)**: Cada agente genera un razonamiento estructurado en 4 pasos (Señales, Estrategia, Riesgos, Conclusión), aumentando la interpretabilidad.
-   **Feedback Loop Avanzado (Critic Agent)**: Incluye un nodo de auditoría técnica que evalúa la calidad de la respuesta del especialista y sugiere refinamientos en tiempo real.
-   **Enriched Developer Payload**: El sistema genera un rastro completo de ejecución que incluye metadatos del modelo, hashing de contexto y diagramas de flujo `Mermaid`.
-   **Context Engineering Layer**: Capa de pre-procesamiento que limpia y normaliza las entradas para maximizar la precisión del ruteo.

### Metrics
El sistema registra automáticamente:
-   `total_tokens`: Consumo consolidado (Router + Especialista + Crítico).
-   `latency_ms`: Tiempo total de la cadena de razonamiento.
-   `estimated_cost_usd`: Costo acumulado basado en tarifas de mercado.

### Known Limitations
-   Dependencia de la capacidad del modelo para seguir esquemas estructurados complejos.
-   La latencia aumenta proporcionalmente al número de pasos de auditoría/refinamiento.

---

## Español

Este proyecto implementa un sistema multi-agente premium para la gestión inteligente de solicitudes mediante ruteo especializado y técnicas avanzadas de Ingeniería de Prompts.

### Requisitos
- **Python 3.10+**.
- **Proveedor de LLM**: Compatible con **LM Studio**, **OpenAI**, **Groq** y **Gemini**.

### Configuración
1.  Copia el archivo de ejemplo para crear tu configuración:
    ```bash
    cp .env.example .env
    ```
2.  Edita el archivo `.env` para seleccionar tu `LLM_PROVIDER` y agregar tus API keys.

### Instalación
1.  Instala las dependencias:
    ```powershell
    pip install -r requirements.txt
    ```

### Ejecución
```powershell
python src/run_query.py --query "¿Cuándo vence mi próxima factura?"
```

### Capacidades Principales
-   **Salida Estructurada Nativa**: Integración profunda con Pydantic para evitar errores de formato.
-   **Razonamiento CoT Granular**: Trazabilidad de lógica en 4 pasos técnicos obligatorios para cada decisión.
-   **Bucle de Retroalimentación (Agente Crítico)**: Procesamiento iterativo donde un auditor interno valida la calidad de la respuesta antes de la entrega final.
-   **Payload Enriquecido para Desarrolladores**: Salida JSON que incluye rastro de ejecución, diagramas `Mermaid` y metadatos de sistema.
-   **Guardia de Integridad Financiera**: Validación automática de datos críticos en consultas de facturación.

### Estructura del Proyecto
-   `src/`: Núcleo del sistema (agentes, ruteo, seguridad, auditoría).
-   `prompts/`: Templates de alta fidelidad optimizados para razonamiento complejo.
-   `metrics/`: Registro histórico y telemetría de ejecuciones.
-   `architecture_reports/`: Informes técnicos detallados.

### Métricas
El sistema registra automáticamente:
-   `total_tokens`: Conteo consolidado de uso.
-   `latency_ms`: Tiempo total de respuesta (Coordinador + Especialista).
-   `estimated_cost_usd`: Costo simulado basado en precios de mercado.

### Limitaciones Conocidas
-   Se recomienda el uso de modelos con capacidades de Tool Calling para un rendimiento óptimo de la salida estructurada.
-   La seguridad combina detección de patrones adversarios con capas de filtrado de contexto.
