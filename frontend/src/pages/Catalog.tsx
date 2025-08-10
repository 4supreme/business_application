import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { Product } from "../lib/api";

export default function Catalog() {
  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [unit, setUnit] = useState("шт");
  const [barcode, setBarcode] = useState("");

  const [list, setList] = useState<Product[]>([]);
  const load = () => api.products().then(setList);

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* левая колонка — создание товара */}
      <div className="card">
        <h3 className="text-lg mb-2">Создать товар</h3>

        <label className="lbl">Название</label>
        <input className="input" value={name} onChange={(e) => setName(e.target.value)} />

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="lbl">SKU</label>
            <input className="input" value={sku} onChange={(e) => setSku(e.target.value)} />
          </div>
          <div>
            <label className="lbl">Ед. изм.</label>
            <input className="input" value={unit} onChange={(e) => setUnit(e.target.value)} />
          </div>
        </div>

        <label className="lbl">Штрихкод</label>
        <input className="input" value={barcode} onChange={(e) => setBarcode(e.target.value)} />

        <div className="mt-3 flex gap-2">
          <button
            className="btn-line"
            onClick={() => {
              setName("");
              setSku("");
              setUnit("шт");
              setBarcode("");
            }}
          >
            Очистить
          </button>

          <button
            className="btn"
            onClick={async () => {
              if (!name.trim()) {
                alert("Введите название");
                return;
              }
              await api.createProduct({
                name,
                sku: sku || null,
                unit: unit || "шт",
                barcode: barcode || null,
              });
              setName("");
              setSku("");
              setUnit("шт");
              setBarcode("");
              load();
            }}
          >
            Создать
          </button>
        </div>
      </div>

      {/* правая колонка — список товаров */}
      <div className="card">
        <h3 className="text-lg mb-2">Список товаров</h3>
        <button className="btn-line mb-2" onClick={load}>Обновить</button>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Ед.</th>
              <th>Штрихкод</th>
            </tr>
          </thead>
          <tbody>
            {list.map((p: Product) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.name}</td>
                <td>{p.unit || ""}</td>
                <td>{p.barcode || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}