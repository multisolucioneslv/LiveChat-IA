# Módulo de agentes de IA
# Exporta todas las clases y funciones principales

from .base_agent import BaseAgent
from .openai_agent import OpenAIAgent
from .claude_agent import ClaudeAgent
from .gemini_agent import GeminiAgent
from .ollama_agent import OllamaAgent
from .groq_agent import GroqAgent
from .agent_factory import AgentFactory, AgentManager

__all__ = [
    'BaseAgent',
    'OpenAIAgent',
    'ClaudeAgent',
    'GeminiAgent',
    'OllamaAgent',
    'GroqAgent',
    'AgentFactory',
    'AgentManager'
]