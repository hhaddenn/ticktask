# ADR 0002: Deploy e alojamento na Raspberry Pi

**Data:** 2026-11-03 · **Estado:** proposta

## Contexto

Quero alojar a aplicação na minha Raspberry Pi. Recursos limitados (CPU, RAM, cartão SD). Falta decidir como instalo os serviços e como acedo à app fora de casa.

## Decisão

<Uma frase. Ex: Docker Compose com Postgres, Django (gunicorn) e um servidor web para o build do React; acesso via <rede local / VPN / HTTPS público>.>

## Alternativas consideradas

- **Instalação direta (sem Docker):** <porque não?>
- **Exposto à internet com HTTPS vs. só VPN/rede local:** <qual e porquê?>
- **<outra>:** <...>

## Consequências

- **Positivas:** <...>
- **Negativas / trade-offs:** <ex: backups da base de dados são responsabilidade minha>
- **O que faria reverter esta decisão:** <...>
