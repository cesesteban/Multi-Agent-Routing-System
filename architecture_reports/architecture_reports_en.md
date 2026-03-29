# Multi-Agent Routing System Architecture Report (01-PI)

## 1. Vision of Architecture
The system is designed as a **Hierarchical Routing Architecture**. It employs a primary "Router Agent" that acts as a traffic controller, directing user queries to specialized agents (Complaints, Finance, Tech Support, or General).

### Flow:
1.  **Safety Layer**: Validates the input against common adversarial patterns.
2.  **Router Agent**: Classifies the query and estimates confidence.
3.  **Specialist Agent**: Receives the specific context and produces a detailed, formatted response.
4.  **Metrics Observer**: Captures token usage, latency, and simulated costs at each step.

## 2. Prompting Techniques
-   **Instruction-Based Prompting**: Clear roles and constraints.
-   **Few-Shot Examples**: Included in the router prompt to ground the classification logic.
-   **Chain of Thought (Implicit)**: Specialists are instructed to analyze the case before replying.
-   **Output Structuring**: Strictly enforced JSON via Pydantic integration.

## 3. Metrics Summary
*(Sample metrics recorded during initial runs)*

| Metric | Average Value |
| :--- | :--- |
| Latency (ms) | ~1200ms |
| Tokens (Total) | ~450 tokens |
| Cost (USD - SIMULATED) | ~$0.003 USD |

## 4. Challenges & Improvements
-   **JSON Parsing**: Local models can occasionally struggle with strict JSON. **Improvement**: Implemented a fallback mechanism.
-   **Context Loss**: Passing context between agents. **Improvement**: The Specialist prompt includes the Router's reasoning.
-   **Safety**: Basic keyword detection. **Improvement**: In production, an LLM-based moderation step would be used.

## 5. Conclusion
The 01-PI system demonstrates a scalable way to handle diverse customer requests by isolating domain expertise into specialized agents while maintaining central control and observability.
