import { useEffect, useState } from "react";
import { api, Product } from "../lib/api";

export default function Stock(){
  const [list,setList] = useState<Product[]>([]); const [q,setQ]=useState("");
  const load=()=>api.stock().then(setList);
  useEffect(()=>{ load(); },[]);
  const filtered = !q ? list : list.filter(p => p.name.toLowerCase().includes(q.toLowerCase()) || String(p.id).includes(q));
  return (
    <div className="card">
      <div className="flex items-center justify-between gap-2 mb-2">
        <h3 className="text-lg">Остатки на складе</h3>
        <div className="flex gap-2">
          <input className="input min-w-[260px]" placeholder="Поиск по названию..." value={q} onChange={e=>setQ(e.target.value)} />
          <button className="btn-line" onClick={load}>Обновить</button>
        </div>
      </div>
      <table className="table">
        <thead><tr><th>ID</th><th>Название</th><th>SKU</th><th className="text-right">Остаток</th><th className="text-right">Ср. себестоимость</th></tr></thead>
        <tbody>
          {filtered.map(p=><tr key={p.id}><td>{p.id}</td><td>{p.name}</td><td>{p.sku||""}</td><td className="text-right">{p.qty_on_hand}</td><td className="text-right">{p.avg_cost}</td></tr>)}
        </tbody>
      </table>
    </div>
  );
}
