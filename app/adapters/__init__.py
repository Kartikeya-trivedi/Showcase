# app/adapters/__init__.py
"""
Adapter layer for external service integrations.

This module provides infrastructure boundaries between the application
and external systems. Adapters handle all low-level communication,
error handling, and protocol details while exposing clean Python interfaces.

Available Adapters:
    - GeminiAdapter: Google Gemini API integration

Exception Hierarchy:
    GeminiError (base)
    ├── GeminiAPIError
    ├── GeminiResponseParseError
    ├── GeminiEmptyResponseError
    └── GeminiRateLimitError
"""


from .gemini_adapter import (
    GeminiAdapter,
    GeminiError,
    GeminiAPIError,
    GeminiResponseParseError,
    GeminiEmptyResponseError,
    GeminiRateLimitError,
)

__all__ = [
    "GeminiAdapter",
    "GeminiError",
    "GeminiAPIError",
    "GeminiResponseParseError",
    "GeminiEmptyResponseError",
    "GeminiRateLimitError",
]