import { useEffect, useState } from "react";
import { api, Product } from "../lib/api";

type Row = { product_id:number|string; qty:number|string; price:number|string };

export default function Sale(){
  const [client,setClient]=useState("");
  const [stock,setStock]=useState<Product[]>([]);
  const [rows,setRows]=useState<Row[]>([{product_id:"",qty:"",price:""}]);
  const [msg,setMsg]=useState("");
  useEffect(()=>{ api.stock().then(setStock); },[]);
  const setRow=(i:number,p:Partial<Row>)=>setRows(r=>r.map((x,idx)=>idx===i?{...x,...p}:x));
  const addRow=()=>setRows(r=>[...r,{product_id:"",qty:"",price:""}]);
  const items = rows.map(r=>({product_id:Number(r.product_id), qty:Number(r.qty), price:Number(r.price)})).filter(x=>x.product_id && x.qty>0 && x.price>=0);
  const total = items.reduce((s,x)=>s+x.qty*x.price,0);
  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card">
        <h3 className="text-lg mb-2">Продажа</h3>
        <label className="lbl">ID клиента (необязательно)</label>
        <input className="input" value={client} onChange={e=>setClient(e.target.value)} placeholder="например 1" />
      </div>
      <div className="card">
        <h3 className="text-lg mb-2">Позиции</h3>
        {rows.map((r,i)=>(
          <div key={i} className="grid grid-cols-3 gap-2 mb-2">
            <select className="input" value={r.product_id} onChange={e=>setRow(i,{product_id:e.target.value})}>
              <option value="">Товар…</option>
              {stock.map(p=><option key={p.id} value={p.id}>{`#${p.id} — ${p.name}`}</option>)}
            </select>
            <input className="input" placeholder="Кол-во" value={r.qty} onChange={e=>setRow(i,{qty:e.target.value})} type="number" min="0" step="any" />
            <input className="input" placeholder="Цена продажи" value={r.price} onChange={e=>setRow(i,{price:e.target.value})} type="number" min="0" step="any" />
          </div>
        ))}
        <div className="flex gap-2">
          <button className="btn-line" onClick={addRow}>+ Позиция</button>
          <button className="btn" onClick={async()=>{
            if(items.length===0) return setMsg("Добавь позиции");
            await api.sale({ client_id: client?Number(client):null, items });
            setRows([{product_id:"",qty:"",price:""}]); setMsg("Продажа проведена");
            api.stock().then(setStock);
          }}>Провести продажу</button>
          <div className="ml-auto text-sm">Итого: <b>{total.toFixed(2)}</b></div>
        </div>
        {msg && <div className="mt-2 text-emerald-400 text-sm">{msg}</div>}
      </div>
    </div>
  );
}
