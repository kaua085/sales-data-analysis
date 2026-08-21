from pathlib import Path
import random
import pandas as pd

random.seed(42)

BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

produtos = {
    "Notebook": ("Eletrônicos", 3200, 6500),
    "Smartphone": ("Eletrônicos", 900, 4500),
    "Monitor": ("Eletrônicos", 650, 1900),
    "Teclado": ("Acessórios", 70, 450),
    "Mouse": ("Acessórios", 40, 300),
    "Headset": ("Acessórios", 90, 550),
    "Webcam": ("Acessórios", 120, 700),
    "SSD 1TB": ("Informática", 280, 650),
    "Memória RAM": ("Informática", 150, 550),
    "Roteador": ("Informática", 160, 600),
    "Impressora": ("Informática", 550, 1800),
    "Cadeira Gamer": ("Móveis", 650, 2200),
    "Mesa Escritório": ("Móveis", 450, 1600),
    "Caixa de Som": ("Áudio", 100, 800),
    "Fone Bluetooth": ("Áudio", 80, 650),
}

cidades = [
    "Fortaleza",
    "Caucaia",
    "Itapipoca",
    "Maracanaú",
    "Sobral",
    "Juazeiro do Norte",
]

regioes = {
    "Fortaleza": "Fortaleza",
    "Caucaia": "Região Metropolitana",
    "Maracanaú": "Região Metropolitana",
    "Itapipoca": "Interior",
    "Sobral": "Interior",
    "Juazeiro do Norte": "Interior",
}

canais = ["Loja Física", "Site", "Marketplace"]

pagamentos = [
    "PIX",
    "Cartão de Crédito",
    "Cartão de Débito",
    "Boleto",
]

datas = pd.date_range(
    "2025-01-01",
    "2026-07-31",
    freq="D"
)

registros = []

for numero in range(1, 10001):

    produto = random.choice(list(produtos.keys()))
    categoria, preco_min, preco_max = produtos[produto]

    cidade = random.choices(
        cidades,
        weights=[40, 15, 10, 12, 12, 11],
        k=1,
    )[0]

    quantidade = random.choices(
        [1, 2, 3, 4],
        weights=[65, 23, 9, 3],
        k=1,
    )[0]

    desconto = random.choices(
        [0, 0.05, 0.10, 0.15],
        weights=[55, 20, 18, 7],
        k=1,
    )[0]

    registros.append({
        "order_id": f"PED{numero:05d}",
        "date": random.choice(datas),
        "product": produto,
        "category": categoria,
        "city": cidade,
        "region": regioes[cidade],
        "channel": random.choice(canais),
        "payment_method": random.choice(pagamentos),
        "quantity": quantidade,
        "unit_price": round(
            random.uniform(preco_min, preco_max), 2
        ),
        "discount": desconto,
    })

df = pd.DataFrame(registros)

df = df.sort_values("date").reset_index(drop=True)

arquivo = DATA / "sales.csv"

df.to_csv(
    arquivo,
    index=False
)

print("=" * 50)
print("BASE DE VENDAS GERADA COM SUCESSO")
print("=" * 50)
print(f"Registros: {len(df):,}")
print(f"Pedidos: {df['order_id'].nunique():,}")
print(f"Produtos: {df['product'].nunique()}")
print(f"Cidades: {df['city'].nunique()}")
print(f"Período: {df['date'].min()} até {df['date'].max()}")
print(f"Arquivo: {arquivo}")