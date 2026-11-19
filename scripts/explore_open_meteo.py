"""Explora a Historical Weather API do Open-Meteo (sem chave) para o Energy Analytics.

Uso, na raiz do repositório, no terminal do Codespace (só precisa de requests):

  python scripts/explore_open_meteo.py probe     # uma cidade, poucos dias: variáveis, unidades, grade e fuso
  python scripts/explore_open_meteo.py models    # compara modelos (padrão, era5, era5_land, era5_seamless)
  python scripts/explore_open_meteo.py cities    # cidades candidatas por subsistema: célula da grade e altitude
  python scripts/explore_open_meteo.py tz        # comportamento do fuso e do horário de verão
  python scripts/explore_open_meteo.py recency   # até que dia há dados (defasagem)
  python scripts/explore_open_meteo.py cost      # custo estimado em chamadas (não chama a API)
  python scripts/explore_open_meteo.py check     # todos os anteriores, em sequência

Opções: --model (cities e check; padrão era5_seamless); --city "São Paulo"  --start AAAA-MM-DD  --end AAAA-MM-DD

Uso gratuito: apenas não comercial, com atribuição (CC BY 4.0). Limites do plano gratuito, segundo
a página de preços: 600 chamadas por minuto, 5.000 por hora, 10.000 por dia e 300.000 por mês.
"""

import argparse
import math
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

BASE = "https://archive-api.open-meteo.com/v1/archive"
TZ = "America/Sao_Paulo"
DAILY_ALL = "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum"

# Cidades candidatas por subsistema (nome, latitude, longitude). A escolha final é da Fase 01.
CITIES = {
    "SE": [("São Paulo", -23.5505, -46.6333), ("Rio de Janeiro", -22.9068, -43.1729),
           ("Belo Horizonte", -19.9167, -43.9345), ("Brasília", -15.7939, -47.8828)],
    "S": [("Porto Alegre", -30.0346, -51.2177), ("Curitiba", -25.4284, -49.2733)],
    "NE": [("Salvador", -12.9777, -38.5016), ("Fortaleza", -3.7319, -38.5267),
           ("Recife", -8.0476, -34.8770)],
    "N": [("Manaus", -3.1190, -60.0217), ("Belém", -1.4558, -48.4902)],
}
FLAT = [(sub, n, la, lo) for sub, items in CITIES.items() for n, la, lo in items]


def norm(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def pick(city):
    for _, name, lat, lon in FLAT:
        if norm(name) == norm(city):
            return name, lat, lon
    raise SystemExit(f"Cidade '{city}' fora da lista: {', '.join(n for _, n, _, _ in FLAT)}")


def call(params, retries=3):
    """GET com novas tentativas em falha de rede e em 429. Levanta RuntimeError ao desistir."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(BASE, params=params, timeout=(10, 60))
        except requests.exceptions.RequestException as e:
            if attempt == retries:
                raise RuntimeError(f"falha de rede ({type(e).__name__})") from e
            wait = 5 * (attempt + 1) ** 2
            print(f"  falha de rede ({type(e).__name__}); nova tentativa em {wait}s...")
            time.sleep(wait)
            continue
        if r.status_code == 200:
            return r.json(), r
        if r.status_code == 429 and attempt < retries:
            wait = 20 * (attempt + 1)
            print(f"  limite de chamadas (429); aguardando {wait}s...")
            time.sleep(wait)
            continue
        try:
            reason = r.json().get("reason", r.text[:200])
        except Exception:
            reason = r.text[:200]
        raise RuntimeError(f"HTTP {r.status_code}: {reason}")
    raise RuntimeError("sem resposta")


def km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(a))


def mean(values):
    v = [x for x in values if x is not None]
    return sum(v) / len(v) if v else None


def fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def cell(data, lat, lon):
    return (f"{data['latitude']:.3f},{data['longitude']:.3f}",
            km(lat, lon, data["latitude"], data["longitude"]))


# ------------------------------------------------------------------ comandos
def cmd_probe(city, start, end):
    name, lat, lon = pick(city)
    print(f"\n== probe: {name} ({lat}, {lon}), {start} a {end} ==")
    data, resp = call({"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
                       "hourly": "temperature_2m", "daily": DAILY_ALL, "timezone": TZ})
    c, dist = cell(data, lat, lon)
    print(f"célula da grade usada: {c} (a {dist:.1f} km do ponto pedido) | altitude: {data.get('elevation')} m")
    print(f"fuso: {data.get('timezone')} ({data.get('timezone_abbreviation')}) | "
          f"utc_offset_seconds: {data.get('utc_offset_seconds')} | geração: {data.get('generationtime_ms')} ms")
    limits = {k: v for k, v in resp.headers.items() if "limit" in k.lower()}
    print(f"cabeçalhos de limite: {limits or 'nenhum'}")
    print(f"unidades horárias: {data.get('hourly_units')}")
    print(f"unidades diárias:  {data.get('daily_units')}")
    hourly, daily = data["hourly"], data["daily"]
    days = len(daily["time"])
    print(f"pontos horários: {len(hourly['time'])} (esperado {days * 24}) | dias: {days}")
    print("nulos:", {k: sum(v is None for v in vals) for k, vals in {**hourly, **daily}.items() if k != "time"})
    print("\nprimeiros dias (diário):")
    cols = [k for k in daily if k != "time"]
    print("  data        " + "  ".join(f"{c:>20}" for c in cols))
    for i in range(min(3, days)):
        print(f"  {daily['time'][i]}  " + "  ".join(f"{fmt(daily[c][i]):>20}" for c in cols))


def cmd_models(city, start, end):
    name, lat, lon = pick(city)
    print(f"\n== models: {name}, {start} a {end} (temperature_2m_mean e precipitation_sum) ==")
    runs, costs = {}, {}
    for label, model in [("padrão (best_match)", None), ("era5", "era5"),
                         ("era5_land", "era5_land"), ("era5_seamless", "era5_seamless")]:
        params = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
                  "daily": "temperature_2m_mean,precipitation_sum", "timezone": TZ}
        if model:
            params["models"] = model
        try:
            runs[label], resp = call(params)
            costs[label] = resp.headers.get("X-RateLimit-Cost")
        except RuntimeError as e:
            print(f"{label}: erro: {e}")
        time.sleep(0.5)
    ref = runs.get("era5")
    print(f"{'modelo':22}{'célula':>18}{'km':>6}{'alt(m)':>8}{'dias':>6}{'nulos T':>9}{'nulos P':>9}"
          f"{'T média':>9}{'P total':>9}{'|ΔT| vs era5':>14}")
    for label, d in runs.items():
        t, p = d["daily"]["temperature_2m_mean"], d["daily"]["precipitation_sum"]
        c, dist = cell(d, lat, lon)
        diff = None
        if ref and label != "era5":
            pairs = [(a, b) for a, b in zip(t, ref["daily"]["temperature_2m_mean"]) if a is not None and b is not None]
            diff = mean([abs(a - b) for a, b in pairs])
        ptotal = sum(x for x in p if x is not None)
        print(f"{label:22}{c:>18}{dist:>6.1f}{fmt(d.get('elevation'), 0):>8}{len(t):>6}"
              f"{sum(x is None for x in t):>9}{sum(x is None for x in p):>9}"
              f"{fmt(mean(t)):>9}{fmt(ptotal, 1):>9}{fmt(diff, 3):>14}")
    print(f"custo de cada requisição (X-RateLimit-Cost): {costs}")
    print("\nObs.: a documentação recomenda ERA5 ou ERA5-Land para séries longas e consistentes. "
          "Precipitação não existe no ERA5-Land.")


def cmd_cities(model="era5_seamless", start="2023-01-01", end="2023-01-14"):
    print(f"\n== cities: {model}, temperature_2m_mean, {start} a {end} ==")
    print(f"{'sub':4}{'cidade':16}{'ponto pedido':>20}{'célula usada':>18}{'km':>6}{'alt(m)':>8}{'T média':>9}")
    for sub, name, lat, lon in FLAT:
        try:
            d, _ = call({"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
                         "daily": "temperature_2m_mean", "timezone": TZ, "models": model})
        except RuntimeError as e:
            print(f"{sub:4}{name:16} erro: {e}")
            continue
        c, dist = cell(d, lat, lon)
        print(f"{sub:4}{name:16}{f'{lat:.3f},{lon:.3f}':>20}{c:>18}{dist:>6.1f}"
              f"{fmt(d.get('elevation'), 0):>8}{fmt(mean(d['daily']['temperature_2m_mean'])):>9}")
        time.sleep(0.5)


def cmd_tz(city, start="2018-11-03", end="2018-11-05"):
    name, lat, lon = pick(city)
    print(f"\n== tz: {name}, {start} a {end} (início do horário de verão em 2018-11-04) ==")
    base = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
            "hourly": "temperature_2m", "timezone": TZ, "models": "era5_seamless"}
    d, _ = call(base)
    per_day = defaultdict(int)
    for t in d["hourly"]["time"]:
        per_day[t[:10]] += 1
    print(f"utc_offset_seconds fixo: {d['utc_offset_seconds']} | horas por dia (ISO, deslocamento fixo): {dict(per_day)}")
    u, _ = call({**base, "timeformat": "unixtime"})
    local = defaultdict(int)
    for ts in u["hourly"]["time"]:
        local[datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(ZoneInfo(TZ)).date().isoformat()] += 1
    print(f"horas por dia local, convertendo o unixtime com o horário de verão: {dict(local)}")
    print("Obs.: a documentação diz que mudanças de horário de verão no intervalo são ignoradas no modo ISO. "
          "O ONS tem 23 linhas no dia em que o horário de verão começa.")


def cmd_recency():
    today = date.today()
    start, end = (today - timedelta(days=14)).isoformat(), today.isoformat()
    print(f"\n== recency: {start} a {end} (São Paulo, temperature_2m_mean) ==")
    name, lat, lon = pick("São Paulo")
    for label, model in [("era5_seamless", "era5_seamless"), ("era5", "era5"), ("padrão (best_match)", None)]:
        params = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
                  "daily": "temperature_2m_mean", "timezone": TZ}
        if model:
            params["models"] = model
        try:
            d, _ = call(params)
        except RuntimeError as e:
            print(f"{label}: erro: {e}")
            continue
        pairs = [(t, v) for t, v in zip(d["daily"]["time"], d["daily"]["temperature_2m_mean"]) if v is not None]
        last = pairs[-1][0] if pairs else None
        lag = (today - date.fromisoformat(last)).days if last else None
        print(f"{label:22} último dia com dado: {last} | defasagem: {lag} dia(s) | dias sem dado: "
              f"{sum(v is None for v in d['daily']['temperature_2m_mean'])}")
    print("Obs.: a documentação indica atualização diária do ERA5 com 5 dias de atraso; "
          "em 2026-11-19 a defasagem medida foi de 7 dias.")


def cmd_cost(n_cities=None, start=date(2000, 1, 1), variables=2):
    n = n_cities or len(FLAT)
    end = date.today() - timedelta(days=6)
    days = (end - start).days + 1
    # Custo medido (2023, 365 dias, 2 variáveis): X-RateLimit-Cost = 5,214 = 365/14 * 2/10.
    # Ou seja, dias e variáveis escalam juntos; o piso de 1 vale só para a requisição inteira.
    per_loc = max(1, days / 14 * variables / 10)
    total = n * per_loc
    chunk = max(1, 365 / 14 * variables / 10)
    pause = chunk / 500 * 60
    print(f"\n== cost: {n} cidades, {start} a {end} ({days} dias), {variables} variáveis diárias ==")
    print("Regra medida: custo = dias/14 * variáveis/10, com mínimo de 1 chamada por requisição.")
    print(f"por cidade: {per_loc:,.0f} chamadas | total: {total:,.0f} chamadas")
    print(f"limites gratuitos -> minuto 600: {total / 600:.1f} min no mínimo | hora 5.000: {total / 5000:.1f} h no mínimo | "
          f"dia 10.000: {total / 10000 * 100:.0f}% do limite diário | mês 300.000: {total / 300000 * 100:.1f}%")
    print(f"sugestão: requisições de 1 ano por cidade (~{chunk:.0f} chamadas cada) com pausa de pelo menos {pause:.1f} s, "
          f"e dividir a carga histórica em 2 dias se passar de 5.000 por hora")
    print(f"carga diária incremental (últimos 10 dias, {n} cidades): ~{n * max(1, 10 / 14 * variables / 10):.0f} chamadas por execução")
    print("(estimativa pela regra medida; confira o consumo real no cabeçalho X-RateLimit-Remaining)")


def cmd_check(city, start, end, model="era5_seamless"):
    steps = [("probe", cmd_probe, (city, start, end)),
             ("models", cmd_models, (city, "2023-01-01", "2023-12-31")),
             ("cities", cmd_cities, (model,)),
             ("tz", cmd_tz, (city,)),
             ("recency", cmd_recency, ()),
             ("cost", cmd_cost, ())]
    for label, fn, args in steps:
        try:
            fn(*args)
        except RuntimeError as e:
            print(f"\n[{label}] interrompido: {e}. Rode 'python scripts/explore_open_meteo.py {label}' depois.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["probe", "models", "cities", "tz", "recency", "cost", "check"])
    ap.add_argument("--city", default="São Paulo")
    ap.add_argument("--model", default="era5_seamless", help="modelo usado em cities e check")
    ap.add_argument("--start")
    ap.add_argument("--end")
    a = ap.parse_args()
    try:
        if a.command == "probe":
            cmd_probe(a.city, a.start or "2024-01-01", a.end or "2024-01-14")
        elif a.command == "models":
            cmd_models(a.city, a.start or "2023-01-01", a.end or "2023-12-31")
        elif a.command == "cities":
            cmd_cities(a.model)
        elif a.command == "tz":
            cmd_tz(a.city, a.start or "2018-11-03", a.end or "2018-11-05")
        elif a.command == "recency":
            cmd_recency()
        elif a.command == "cost":
            cmd_cost()
        else:
            cmd_check(a.city, a.start or "2024-01-01", a.end or "2024-01-14", a.model)
    except RuntimeError as e:
        sys.exit(f"Erro na API: {e}")


if __name__ == "__main__":
    main()