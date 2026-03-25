"""Centralized Ollama client - handles both local and remote models."""

import requests
import os
from soul.core.logger import setup_logger
from soul.core.config import identity

logger = setup_logger(__name__)

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = "gpt-oss:120b-cloud"

_embedding_model = None


def get_embedding_model():
    """Get or initialize the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer("BAAI/bge-m3")
        logger.info("BGE-M3 embedding model loaded")
    return _embedding_model


def generate(
    model: str = None, prompt: str = None, system: str = None, **options
) -> dict:
    """Generate response using direct HTTP - handles both local and remote models."""
    model = model or DEFAULT_MODEL

    payload = {
        "model": model,
        "prompt": prompt or "",
        "stream": False,
    }

    # Inject absolute identity
    absolute_system = identity.absolute_system_prompt
    if system:
        payload["system"] = f"{absolute_system}\n\n{system}"
    else:
        payload["system"] = absolute_system

    # Set default options if not provided
    if "options" not in payload:
        payload["options"] = {}

    # Add user options
    if options:
        payload["options"].update({k: v for k, v in options.items() if v is not None})

    # Ensure reasonable default for num_predict
    if "num_predict" not in payload["options"]:
        payload["options"]["num_predict"] = 500

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=options.get("timeout", 120),
        )
        response.raise_for_status()
        result = response.json()

        if "response" in result:
            return {"response": result["response"]}
        elif "message" in result:
            return {"response": result["message"].get("content", "")}
        else:
            logger.warning(f"Unexpected response: {result}")
            return {"response": ""}
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        return {"response": f"Error: {e}"}


def generate_with_context(
    model: str = None,
    prompt: str = None,
    system: str = None,
    context: str = None,
    conversation: list = None,
    **options,
) -> dict:
    """Generate with full context - system prompt, context, and conversation history."""
    model = model or DEFAULT_MODEL

    full_prompt = ""

    if system:
        full_prompt += f"System: {system}\n\n"

    if context:
        full_prompt += f"Context:\n{context}\n\n"

    if conversation:
        for msg in conversation[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt += f"{role.capitalize()}: {content}\n"

    if prompt:
        full_prompt += f"User: {prompt}\n\nAssistant:"

    return generate(model=model, prompt=full_prompt, **options)


def embed(text: str) -> list:
    """Get embeddings using sentence-transformers (BGE-M3)."""
    model = get_embedding_model()
    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return [0.0] * 1024


def embed_batch(texts: list) -> list:
    """Get embeddings for multiple texts."""
    model = get_embedding_model()
    try:
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        return [[0.0] * 1024] * len(texts)


def generate_stream(model: str, prompt: str, **options):
    """Streaming generation for long outputs."""
    model = model or DEFAULT_MODEL
    payload = {"model": model, "prompt": prompt, "stream": True}

    if options:
        payload["options"] = {k: v for k, v in options.items() if v is not None}

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, stream=True
        )
        for line in response.iter_lines():
            if line:
                data = line.decode()
                if data.startswith("{"):
                    yield data
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        yield f'{{"error": "{e}"}}'
