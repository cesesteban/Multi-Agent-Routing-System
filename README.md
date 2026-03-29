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
-   `src/`: Main application (routing, agents, safety).
-   `prompts/`: Prompt definitions in Markdown.
-   `metrics/`: Historical record of latency and token usage.
-   `architecture_reports/`: Architecture and design reports ([EN](architecture_reports/architecture_reports_en.md) | [ES](architecture_reports/architecture_reports_es.md)).
-   `tests/`: Validation unit tests.

### Metrics
The system automatically records:
-   `tokens_prompt`: Input token count.
-   `tokens_completion`: Generated token count.
-   `latency_ms`: Response time in milliseconds.
-   `estimated_cost_usd`: Simulated cost based on GPT-4o pricing.

### Known Limitations
-   Dependency on the quality of the local model for JSON parsing.
-   Security is based on simple text patterns (Safety Layer).

---

## Español

Este proyecto implementa un sistema multi-agente para la gestión de solicitudes mediante un ruteo especializado.

### Requisitos
- **Python 3.10+**.
- **Proveedor de LLM**: El sistema es compatible con **LM Studio**, **OpenAI**, **Groq** y **Gemini**.

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
-   `src/`: Aplicación principal (ruteo, agentes, seguridad).
-   `prompts/`: Definición de prompts en Markdown.
-   `metrics/`: Registro histórico de latencia y uso de tokens.
-   `architecture_reports/`: Informes de arquitectura y diseño ([EN](architecture_reports/architecture_reports_en.md) | [ES](architecture_reports/architecture_reports_es.md)).
-   `tests/`: Pruebas unitarias de validación.

### Métricas
El sistema registra automáticamente:
-   `tokens_prompt`: Conteo de tokens de entrada.
-   `tokens_completion`: Conteo de tokens generados.
-   `latency_ms`: Tiempo de respuesta en milisegundos.
-   `estimated_cost_usd`: Costo simulado basado en precios de GPT-4o.

### Limitaciones Conocidas
-   Dependencia de la calidad del modelo local para el parseo de JSON.
-   La seguridad es basada en patrones de texto simples (Safety Layer).
