import { useEffect, useMemo, useState } from "react";
import { api, Product, VendorRow } from "../lib/api";

type Row = { product_id:number|string; qty:number|string; price:number|string };

export default function Purchase(){
  const today = useMemo(()=>new Date().toISOString().slice(0,10),[]);
  const [date,setDate] = useState(today);
  const [vendor,setVendor] = useState("");
  const [vendorHints,setVendorHints] = useState<string[]>([]);
  const [stock,setStock] = useState<Product[]>([]);
  const [rows,setRows] = useState<Row[]>([{product_id:"", qty:"", price:""}]);
  const [msg,setMsg] = useState("");
  const [history,setHistory] = useState<VendorRow[]>([]);

  useEffect(()=>{ api.stock().then(setStock); api.recentVendors().then(setVendorHints); },[]);
  useEffect(()=>{ if(vendor.trim()) api.vendorHistory(vendor.trim()).then(setHistory).catch(()=>setHistory([])); else setHistory([]); },[vendor]);

  const addRow = ()=> setRows(r=>[...r,{product_id:"",qty:"",price:""}]);
  const setRow = (i:number, patch:Partial<Row>) => setRows(r => r.map((x,idx)=> idx===i? {...x, ...patch}: x));
  const validItems = rows
    .map(r=>({ product_id: Number(r.product_id), qty: Number(r.qty), price: Number(r.price) }))
    .filter(x => x.product_id && x.qty>0 && x.price>=0);
  const total = validItems.reduce((s,x)=> s + x.qty*x.price, 0);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* левая колонка — поставщик, дата */}
      <div className="card">
        <h3 className="text-lg mb-2">Сведения о поставщике</h3>
        <label className="lbl">Дата документа</label>
        <input className="input" type="date" value={date} onChange={e=>setDate(e.target.value)} />
        <label className="lbl">Поставщик (последние 5 или свой)</label>
        <input className="input" list="vendor_list" value={vendor} onChange={e=>setVendor(e.target.value)} placeholder="Например: ТОО Алматы" />
        <datalist id="vendor_list">
          {vendorHints.map(v=><option key={v} value={v} />)}
        </datalist>
        <p className="text-xs text-slate-400 mt-3">Подсказка: сначала создай товары в «Каталог».</p>
      </div>

      {/* правая колонка — товары */}
      <div className="card">
        <h3 className="text-lg mb-2">Позиции товаров</h3>
        {rows.map((r,i)=>(
          <div key={i} className="grid grid-cols-3 gap-2 mb-2">
            <select className="input" value={r.product_id} onChange={e=>setRow(i,{product_id:e.target.value})}>
              <option value="">Наименование товара…</option>
              {stock.map(p=><option key={p.id} value={p.id}>{`#${p.id} — ${p.name}`}</option>)}
            </select>
            <input className="input" placeholder="Количество" value={r.qty} onChange={e=>setRow(i,{qty:e.target.value})} type="number" min="0" step="any" />
            <input className="input" placeholder="Цена" value={r.price} onChange={e=>setRow(i,{price:e.target.value})} type="number" min="0" step="any" />
          </div>
        ))}
        <div className="flex gap-2">
          <button className="btn-line" onClick={addRow}>+ Позиция</button>
          <button className="btn" onClick={async()=>{
            setMsg("");
            if(!vendor.trim()){ setMsg("Укажи поставщика"); return; }
            if(validItems.length===0){ setMsg("Добавь хотя бы одну позицию"); return; }
            await api.purchase({ date, vendor: vendor.trim(), items: validItems });
            setRows([{product_id:"",qty:"",price:""}]);
            setMsg("Приход проведён");
            api.stock().then(setStock);
            api.recentVendors().then(setVendorHints);
            api.vendorHistory(vendor.trim()).then(setHistory);
          }}>Провести приход</button>
          <div className="ml-auto text-sm text-slate-300">Итого: <b>{total.toFixed(2)}</b></div>
        </div>
        {msg && <div className="mt-2 text-sm text-emerald-400">{msg}</div>}
      </div>

      {/* низ — история по поставщику */}
      <div className="md:col-span-2 card">
        <h3 className="text-lg mb-2">История закупок у поставщика: <span className="text-slate-300">{vendor || "—"}</span></h3>
        <table className="table">
          <thead><tr><th>Дата</th><th>Товар</th><th className="text-right">Кол-во</th><th className="text-right">Цена</th><th className="text-right">Сумма</th></tr></thead>
          <tbody>
            {history.map((r,idx)=>{
              const d = new Date(r.date).toISOString().slice(0,10);
              return <tr key={idx}><td>{d}</td><td>{r.product_name}</td>
                <td className="text-right">{r.qty}</td><td className="text-right">{r.price}</td><td className="text-right">{r.total.toFixed(2)}</td></tr>;
            })}
            {history.length===0 && <tr><td colSpan={5} className="text-slate-400">Нет данных — выбери поставщика или ещё не было закупок</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
