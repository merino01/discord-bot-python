"""Modelos para el módulo Echo"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EchoMessage:
    """Modelo para mensajes enviados con echo"""
    id: str
    message_id: int
    channel_id: int
    guild_id: int
    user_id: int
    content: str
    is_embed: bool
    created_at: datetime
    
    @property
    def preview(self) -> str:
        """Genera una vista previa del mensaje para el selector"""
        if self.is_embed:
            try:
                import json
                embed_data = json.loads(self.content)
                title = embed_data.get('title', '')
                description = embed_data.get('description', '')
                preview_text = title or description or 'Embed sin título'
            except (json.JSONDecodeError, KeyError, TypeError):
                preview_text = 'Embed personalizado'
        else:
            preview_text = self.content
        
        # Truncar a 50 caracteres
        if len(preview_text) > 50:
            preview_text = preview_text[:47] + "..."
        
        return f"#{self.channel_id} | {preview_text}"
    
    @property
    def preview_with_user(self) -> str:
        """Genera una vista previa del mensaje incluyendo información del usuario"""
        base_preview = self.preview
        # Solo mostrar el preview básico sin el ID del usuario
        return base_preview
