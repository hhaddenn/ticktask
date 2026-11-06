# ADR 0004: API na mesma origem (proxy do Vite em dev, sem CORS)

**Data:** 2026-11-06 · **Estado:** aceite

## Contexto

Em dev, o React corre em `localhost:5173` e o Django em `localhost:8000`. São origens diferentes, por isso o browser bloqueia os pedidos do React à API (same-origin policy) a menos que se configure CORS.

Em produção (ADR 0002), um servidor web serve o build do React e reencaminha `/api/` para o Django, tudo no mesmo domínio: não há pedidos entre origens.

## Decisão

Toda a API fica debaixo de `/api/`. Em dev, o servidor do Vite reencaminha `/api` para o Django (`server.proxy`). Não se usa CORS.

## Alternativas consideradas

- **CORS no Django (`django-cors-headers`):** funciona, e é o que a app de finanças usa. Rejeitado porque só seria preciso em dev (em produção é tudo a mesma origem), é mais uma dependência e configuração para manter, e uma configuração de CORS mal feita é uma falha de segurança comum.

## Consequências

- **Positivas:**
  - Dev e produção funcionam da mesma forma: o React pede sempre caminhos relativos (`/api/...`).
  - Sem configuração de CORS para manter ou restringir.
  - Cookies de sessão e CSRF do Django funcionam sem configuração extra, por ser tudo a mesma origem.
- **Negativas / trade-offs:**
  - Alterações ao `vite.config.js` obrigam a reiniciar o `npm run dev`.
  - O servidor web de produção tem de reencaminhar `/api/` para o Django (fica para o M4).
  - A proteção CSRF continua a ser necessária quando houver login; estar na mesma origem não a dispensa.
- **O que faria reverter esta decisão:** a API passar a ser usada por clientes noutras origens (ex: outra app ou um domínio separado para a API). Aí seria preciso CORS, restrito a essas origens.
