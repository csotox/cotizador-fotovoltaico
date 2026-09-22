---
name: memory-logs
description: Registra las decisiones relevantes durante la sesión de trabajo.
---

# Memory Logs

Unicamente si el usuario lo solicita, crear un archivo en:

docs/memoria/YYYY-MM-DD-tema.md

La memoria debe registrar únicamente hechos verificables del trabajo realizado.

## Debe incluir

- Modelo LLM utilizado.
- Contexto.
- Objetivo.
- Cambios realizados.
- Problemas encontrados.
- Decisiones tomadas.
- Dificultades.
- Pendientes, si existen.
- Comandos ejecutados.
- Resultado final.

## No debe incluir

- Suposiciones no verificadas.
- Elogios.
- Narrativa innecesaria.
- Decisiones arquitectónicas nuevas sin ADR.
- Cambios no realizados como si estuvieran hechos.

## Reglas adicionales

- No sobrescribir memorias anteriores.
- Mantener redacción breve y técnica.
- Diferenciar claramente entre trabajo completado y pendiente.
- Si una decisión arquitectónica requiere justificación permanente, crear o actualizar un ADR y referenciarlo desde la memoria.
- No registrar secretos, tokens, contraseñas ni valores sensibles.
