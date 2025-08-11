import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { Product } from "../lib/api";

export default function Stock() {
  const [list, setList] = useState<Product[]>([]);
  const [q, setQ] = useState("");

  const load = () => api.stock().then(setList);
  useEffect(() => { load(); }, []);

  const filtered = !q
    ? list
    : list.filter(
        (p) =>
          p.name.toLowerCase().includes(q.toLowerCase()) ||
          String(p.id).includes(q)
      );

  return (
    <div className="card">
      <h3 className="text-lg mb-2">Склад</h3>
      <div className="flex gap-2">
        <input
          className="input min-w-[260px]"
          placeholder="Поиск по названию..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button className="btn-line" onClick={load}>Обновить</button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th><th>Название</th><th>SKU</th><th className="text-right">Остаток</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td><td>{p.name}</td><td>{p.sku || ""}</td>
              <td className="text-right">{p.qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}