# Radar Aereo Brasil

Mapa de radar aéreo em tempo real cobrindo todo o Brasil, usando [Leaflet.js](https://leafletjs.com/) + [OpenSky Network API](https://opensky-network.org/).

## Funcionalidades

- 🗺️ Mapa dark mode (CartoDB Dark Matter)
- ✈️ Ícones por categoria: Comercial, Geral e Helicóptero
- 🛰️ Dados em tempo real via OpenSky Network (atualização a cada 10s)
- 📍 Trajetória da aeronave ao clicar
- 🔄 Ciclo automático entre aeronaves a cada 10s
- 📋 Lista de aeronaves visíveis no viewport atual
- 🇧🇷 Cobertura de todo o Brasil

## Como rodar localmente

```bash
python server.py
# Acesse: http://localhost:9090
```

## Deploy

Este projeto está configurado para deploy no [Render.com](https://render.com) com zero dependências externas.
