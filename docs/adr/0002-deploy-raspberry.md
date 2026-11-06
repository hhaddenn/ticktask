# ADR 0002: Deploy e alojamento na Raspberry Pi

**Data:** 2026-11-03 · **Estado:** aceite

## Contexto

Quero alojar a aplicação na minha Raspberry Pi, onde já gero outros projetos com o Komodo. Recursos limitados (CPU, RAM, cartão SD). Preciso de aceder à app fora de casa, sem expor a minha rede.

## Decisão

Docker Compose com imagens construídas automaticamente, geridas no Komodo, com Postgres, Django (gunicorn) e um servidor web para o build do React; acesso via Cloudflare tunnel.

## Alternativas consideradas

- **Instalação direta (sem Docker):** dificulta o deploy de novas features, porque obriga a entrar na Raspberry, e não encaixa na gestão de stacks que já faço no Komodo.
- **Abrir portas no router com HTTPS:** expõe o IP de casa e obriga a manter portas abertas e certificados.
- **Só VPN / rede local:** seguro, mas exige um cliente VPN em cada dispositivo de onde quero aceder.
- **Cloudflare tunnel (escolhido):** a ligação é de saída, por isso não há portas abertas no router nem IP de casa exposto, e o HTTPS fica tratado pela Cloudflare.

## Consequências

- **Positivas:**
  - Deploy de novas features sem entrar na Raspberry.
  - Gestão uniforme de stacks entre os vários projetos no Komodo.
  - Sem portas abertas em casa.
- **Negativas / trade-offs:**
  - **Arquitetura ARM:** a Raspberry é `arm64`. As imagens construídas automaticamente (ex: num CI) têm de ser construídas para `arm64`.
  - **Dependência da Cloudflare** para o acesso externo.
  - **Backups da base de dados são responsabilidade minha**, e um cartão SD com Postgres desgasta-se. Por agora, os backups (dump do Postgres) ficam na própria Raspberry. **Risco aceite:** se o cartão SD ou a Raspberry falharem, perdem-se os dados e os backups ao mesmo tempo. Rever quando a app tiver dados que não posso perder: no mínimo um disco USB separado, idealmente uma cópia fora de casa.
- **O que faria reverter esta decisão:** se o projeto crescer ao ponto de fazer sentido alojar noutro local.
