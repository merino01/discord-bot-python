"""
Tareas programadas para el módulo de mensajes automáticos usando schedule
"""

import asyncio
import threading
import time
import schedule
from datetime import datetime
from typing import Dict, Optional
import json
from modules.core import logger
from .services import AutomaticMessagesService
from .models import AutomaticMessage
from .text_processor import process_message_text


class AutomaticMessagesScheduler:
    """Programador de mensajes automáticos usando schedule (cron-like)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.service = AutomaticMessagesService()
        self.interval_trackers: Dict[str, datetime] = {}
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Inicia el programador de mensajes"""
        if not self.running:
            self.running = True

            self._setup_scheduled_jobs()
            self._start_scheduler_thread()
    
    def stop(self):
        """Detiene el programador de mensajes"""
        if self.running:
            self.running = False
            schedule.clear()
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            logger.info("Programador de mensajes automáticos detenido")
    
    def _setup_scheduled_jobs(self):
        """Configura todos los trabajos programados basados en la base de datos"""
        # Limpiar trabajos anteriores
        schedule.clear()
        
        # Obtener todos los mensajes programados
        messages, error = self.service.get_all()
        logger.info("Cargando mensajes automáticos - Error: %s, Total mensajes: %s", 
                   error, len(messages) if messages else 0)
        
        if error or not messages:
            logger.warning("No se pudieron cargar mensajes automáticos: %s", error or "Sin mensajes")
            return
        
        for message in messages:
            try:
                logger.info("Procesando mensaje: ID=%s, Tipo=%s, Canal=%s, Hora=%s:%s, Días=%s", 
                           message.id, message.schedule_type, message.channel_id, 
                           message.hour, message.minute, message.weekdays)
                self._schedule_message(message)
            except Exception as e:
                logger.error("Error programando mensaje %s: %s", message.id, str(e))
    
    def _schedule_message(self, message: AutomaticMessage):
        """Programa un mensaje específico usando schedule"""
        if message.schedule_type == "interval":
            self._schedule_interval_message(message)
        elif message.schedule_type == "daily":
            self._schedule_daily_message(message)
        elif message.schedule_type == "weekly":
            self._schedule_weekly_message(message)
        # on_channel_create no necesita programación, se maneja por eventos
    
    def _schedule_interval_message(self, message: AutomaticMessage):
        """Programa un mensaje con intervalo"""
        if not message.interval or not message.interval_unit:
            logger.error("Mensaje %s sin datos de intervalo válidos", message.id)
            return
        
        def job_func():
            if self.bot.loop and not self.bot.loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self._send_message_safe(message), 
                    self.bot.loop
                )
            else:
                logger.error("Loop del bot no disponible para mensaje %s", message.id)
        
        if message.interval_unit == "seconds":
            schedule.every(message.interval).seconds.do(job_func).tag(message.id)
        elif message.interval_unit == "minutes":
            schedule.every(message.interval).minutes.do(job_func).tag(message.id)
        elif message.interval_unit == "hours":
            schedule.every(message.interval).hours.do(job_func).tag(message.id)
        
        logger.debug("Programado mensaje intervalo %s cada %d %s", 
                    message.id, message.interval, message.interval_unit)
    
    def _schedule_daily_message(self, message: AutomaticMessage):
        """Programa un mensaje diario"""
        if message.hour is None or message.minute is None:
            logger.error("Mensaje %s sin hora válida", message.id)
            return
        
        time_str = f"{message.hour:02d}:{message.minute:02d}"
        
        # Función que se ejecutará en el scheduler
        def job_func():
            # Programar la corrutina en el loop del bot
            if self.bot.loop and not self.bot.loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self._send_message_safe(message), 
                    self.bot.loop
                )
            else:
                logger.error("Loop del bot no disponible para mensaje %s", message.id)
        
        schedule.every().day.at(time_str).do(job_func).tag(message.id)
        logger.info("✅ Programado mensaje diario %s para las %s - Canal ID: %s", 
                   message.id, time_str, message.channel_id)
    
    def _schedule_weekly_message(self, message: AutomaticMessage):
        """Programa un mensaje semanal"""
        if message.hour is None or message.minute is None or not message.weekdays:
            logger.error("Mensaje %s sin datos semanales válidos", message.id)
            return
        
        try:
            weekdays = json.loads(message.weekdays)
        except (json.JSONDecodeError, TypeError):
            logger.error("Formato de días inválido para mensaje %s", message.id)
            return
        
        time_str = f"{message.hour:02d}:{message.minute:02d}"
        
        def job_func():
            if self.bot.loop and not self.bot.loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self._send_message_safe(message), 
                    self.bot.loop
                )
            else:
                logger.error("Loop del bot no disponible para mensaje %s", message.id)
        
        # Mapeo de días (0=lunes -> schedule usa nombres)
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for weekday in weekdays:
            if 0 <= weekday <= 6:
                day_name = day_names[weekday]
                getattr(schedule.every(), day_name).at(time_str).do(job_func).tag(message.id)
                logger.info("✅ Programado mensaje semanal %s para %s a las %s", 
                           message.id, day_name, time_str)
    
    def _start_scheduler_thread(self):
        def run_scheduler():
            while self.running:
                # Ejecutar trabajos pendientes
                jobs_run = schedule.run_pending()
                if jobs_run:
                    logger.info("⏰ Ejecutados %d trabajos a las %s", 
                               len([j for j in schedule.jobs if j.should_run]), 
                               datetime.now().strftime("%H:%M:%S"))
                time.sleep(1)  # Verificar cada segundo
            logger.info("🛑 Hilo del scheduler detenido")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    async def _send_message_safe(self, message: AutomaticMessage):
        try:
            await self._send_message(message)
        except Exception as e:
            logger.error("Error enviando mensaje %s: %s", message.id, str(e))
    
    def reload_schedules(self):
        """Recarga todos los trabajos programados desde la base de datos"""
        if self.running:
            logger.info("Recargando trabajos programados...")
            self._setup_scheduled_jobs()
    
    def remove_message_schedule(self, message_id: str):
        """Elimina la programación de un mensaje específico"""
        schedule.clear(message_id)
        logger.debug("Eliminada programación para mensaje %s", message_id)
    
    def add_message_schedule(self, message: AutomaticMessage):
        """Agrega la programación para un nuevo mensaje"""
        try:
            logger.info("Agregando programación para mensaje: ID=%s, Tipo=%s", 
                       message.id, message.schedule_type)
            self._schedule_message(message)
            logger.info("✅ Agregada programación para mensaje %s", message.id)
        except Exception as e:
            logger.error("Error agregando programación para mensaje %s: %s", message.id, str(e))
    
    async def _send_message(self, message: AutomaticMessage):
        """Envía un mensaje automático"""
        try:
            # Determinar el canal
            channel = None
            if message.channel_id:
                channel = self.bot.get_channel(message.channel_id)
            elif message.category_id:
                # Para mensajes de categoría, no se envían por scheduler
                logger.warning("Mensaje de categoría %s siendo procesado por scheduler", message.id)
                return
            
            if not channel:
                logger.warning(
                    "Canal %s no encontrado para mensaje %s", 
                    message.channel_id, message.id
                )
                return
            
            # Procesar el texto del mensaje (variables, menciones, etc.)
            processed_text = process_message_text(message.text, channel, self.bot)
            
            # Usar el nuevo formatter para enviar mensajes con embeds e imágenes
            from .message_formatter import send_formatted_message
            sent_message = await send_formatted_message(channel, processed_text)
            
            if sent_message:
                # Actualizar el tracker para evitar duplicados
                self.interval_trackers[message.id] = datetime.now()
                
                logger.info(
                    "Mensaje automático enviado: %s en canal %s", 
                    message.display_name, channel.name
                )
            else:
                logger.error("No se pudo enviar el mensaje %s", message.id)
            
        except Exception as e:
            logger.error(
                "Error enviando mensaje automático %s: %s", 
                message.id, str(e)
            )
    
    async def send_category_message(self, category_id: int, new_channel):
        """Envía mensajes automáticos cuando se crea un canal en una categoría"""
        try:
            messages, error = self.service.get_by_category_id(category_id)
            
            if error or not messages:
                return
            
            for message in messages:
                if message.schedule_type == "on_channel_create":
                    processed_text = process_message_text(message.text, new_channel, self.bot)
                    
                    # Usar el nuevo formatter para enviar mensajes con embeds e imágenes
                    from .message_formatter import send_formatted_message
                    sent_message = await send_formatted_message(new_channel, processed_text)
                    
                    if sent_message:
                        logger.info(
                            "Mensaje automático de categoría enviado: %s en canal %s", 
                            message.display_name, new_channel.name
                        )
                    else:
                        logger.error("No se pudo enviar mensaje de categoría %s", message.id)
                    
        except Exception as e:
            logger.error(
                "Error enviando mensajes de categoría %s: %s", 
                category_id, str(e)
            )


# Instancia global del programador
_scheduler = None


def setup_automatic_messages(bot):
    """Configura e inicia el sistema de mensajes automáticos"""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = AutomaticMessagesScheduler(bot)
        _scheduler.start()


def get_scheduler():
    """Obtiene la instancia del programador"""
    return _scheduler


def stop_automatic_messages():
    """Detiene el sistema de mensajes automáticos"""
    global _scheduler
    
    if _scheduler:
        _scheduler.stop()
        _scheduler = None


def reload_all_schedules():
    """Recarga todos los trabajos programados"""
    global _scheduler
    if _scheduler:
        _scheduler.reload_schedules()
