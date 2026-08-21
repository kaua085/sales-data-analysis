from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
df = pd.read_csv(BASE / "data" / "sales.csv", parse_dates=["date"])
df["revenue"] = df["quantity"] * df["unit_price"]

print("=== KPIs ===")
print(f"Faturamento total: R$ {df['revenue'].sum():,.2f}")
print(f"Ticket médio: R$ {df.groupby('order_id')['revenue'].sum().mean():,.2f}")
print(f"Pedidos únicos: {df['order_id'].nunique()}")

by_product = df.groupby("product", as_index=False).agg(
    quantity=("quantity","sum"),
    revenue=("revenue","sum")
).sort_values("revenue", ascending=False)

by_category = df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
by_city = df.groupby("city", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)

out = BASE / "output"
out.mkdir(exist_ok=True)
by_product.to_csv(out / "sales_by_product.csv", index=False)
by_category.to_csv(out / "sales_by_category.csv", index=False)
by_city.to_csv(out / "sales_by_city.csv", index=False)

print("\nTop 5 produtos por receita:")
print(by_product.head(5).to_string(index=False))
