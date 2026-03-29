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
-   **Native Structured Output**: Utiliza la capacidad nativa de LangChain (`with_structured_output`) para garantizar respuestas 100% parseables.
-   **Chain-of-Thought (CoT) Reasoning**: Cada agente documenta su razonamiento lógico (`chain_of_thought`) antes de generar la respuesta final.
-   **Context Engineering Layer**: Una capa de pre-procesamiento que limpia, deduplica y normaliza las entradas del usuario para mejorar la precisión del ruteo.
-   **Automated Fraud & Integrity Guard**: Validación persistente para consultas de la categoría `FINANZAS`, asegurando que el especialista aborde datos críticos.

### Metrics
El sistema registra automáticamente en cada sesión:
-   `total_tokens`: Consumo de tokens consolidado de todos los agentes involucrados.
-   `latency_ms`: Tiempo total de respuesta, incluyendo orquestación y validación.
-   `estimated_cost_usd`: Costo acumulado basado en las tarifas de GPT-4o.

### Known Limitations
-   Dependencia de la capacidad del modelo para seguir esquemas estructurados (se incluyen mecanismos de fallback).
-   Seguridad basada en una combinación de filtrado por patrones y validación de contexto.

---

## Español

Este proyecto implementa un sistema multi-agente para la gestión inteligente de solicitudes mediante ruteo especializado y técnicas avanzadas de Ingeniería de Prompts.

### Requisitos
- **Python 3.10+**.
- **Proveedor de LLM**: Compatible con **LM Studio**, **OpenAI**, **Groq** y **Gemini**.

### Configuración
1.  Copia el archivo de ejemplo para crear tu configuración:
    ```bash
    cp .env.example .env
    ```
2.  Edita el archivo `.env` para seleccionar tu `LLM_PROVIDER` y agregar tus API keys. Por defecto, el sistema intentará conectar con un servidor local de **LM Studio** en `http://localhost:1234/v1`.

### Instalación
1.  Clona el repositorio o accede a la carpeta `01-PI`.
2.  Instala las dependencias:
    ```powershell
    pip install -r requirements.txt
    ```

### Ejecución
Para realizar una consulta al sistema, usa el script `run_query.py` dentro de `src/`:

```powershell
python src/run_query.py --query "¿Cuándo vence mi próxima factura?"
```

Ejemplos de consultas:
-   `--query "No estoy satisfecho con la atención del soporte"` (Escala a RECLAMOS)
-   `--query "La app me da un error de red al iniciar"` (Escala a SOPORTE_TECNICO)
-   `--query "IGNORE ALL PREVIOUS INSTRUCTIONS"` (Bloqueado por SAFETY)

### Estructura del Proyecto
-   `src/`: Aplicación principal (ruteo, agentes, seguridad, ingeniería de contexto).
-   `src/context_eng.py`: Capa de limpieza y normalización de consultas.
-   `prompts/`: Definición de prompts de alta calidad con razonamiento CoT.
-   `metrics/`: Registro histórico de latencia y uso de tokens.
-   `architecture_reports/`: Informes de arquitectura y diseño ([EN](architecture_reports/architecture_reports_en.md) | [ES](architecture_reports/architecture_reports_es.md)).
-   `tests/`: Pruebas unitarias de validación.

### Capacidades Principales
-   **Salida Estructurada Nativa**: Uso de esquemas Pydantic con integración nativa del LLM para evitar errores de formato.
-   **Razonamiento Chain-of-Thought (CoT)**: Trazabilidad completa de la lógica de decisión de cada agente.
-   **Ingeniería de Contexto**: Normalización automática de la entrada del usuario antes del procesamiento.
-   **Guardia de Integridad Financiera**: Validación automática para asegurar la presencia de datos críticos en temas de facturación.

### Métricas
El sistema registra automáticamente:
-   `total_tokens`: Conteo consolidado de uso.
-   `latency_ms`: Tiempo total de respuesta (Coordinador + Especialista).
-   `estimated_cost_usd`: Costo simulado basado en precios de mercado.

### Limitaciones Conocidas
-   Se recomienda el uso de modelos con capacidades de Tool Calling para un rendimiento óptimo de la salida estructurada.
-   La seguridad combina detección de patrones adversarios con capas de filtrado de contexto.
