"""
Funciones de procesamiento de texto para mensajes automáticos
"""


def process_message_text(text: str) -> str:
    """
    Procesa el texto del mensaje para interpretar caracteres de escape.
    
    Args:
        text: Texto original con posibles caracteres de escape
        
    Returns:
        Texto procesado con caracteres de escape interpretados
    """
    if not text:
        return text

    return (
        text
            .replace('\\n', '\n')
            .replace('\\t', '\t')
            .replace('\\r', '\r')
    )
