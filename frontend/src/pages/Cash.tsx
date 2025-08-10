import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Cash(){
  const today = new Date().toISOString().slice(0,10);
  const [date,setDate]=useState(today); const [account,setAccount]=useState("cash");
  const [amount,setAmount]=useState(""); const [cp,setCp]=useState(""); const [note,setNote]=useState("");
  const [bal,setBal]=useState({cash:0,bank:0,total:0}); const [last,setLast]=useState<any[]>([]); const [msg,setMsg]=useState("");
  const load=async()=>{ setBal(await api.cashBalance()); setLast(await api.cashLast()); };
  useEffect(()=>{ load(); },[]);
  const send=async(direction:"in"|"out")=>{
    if(!Number(amount)) return setMsg("Введите сумму > 0");
    await api.cashCreate({date,account,direction,amount:Number(amount),counterparty:cp||null,note:note||null});
    setMsg("Операция сохранена"); setAmount(""); load();
  };
  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card">
        <h3 className="text-lg mb-2">Поступление / Выплата</h3>
        <div className="grid grid-cols-3 gap-2">
          <div><label className="lbl">Дата</label><input className="input" type="date" value={date} onChange={e=>setDate(e.target.value)} /></div>
          <div><label className="lbl">Счёт</label>
            <select className="input" value={account} onChange={e=>setAccount(e.target.value)}>
              <option value="cash">Касса</option><option value="bank">Банк</option>
            </select>
          </div>
          <div><label className="lbl">Сумма</label><input className="input" type="number" min="0" step="any" value={amount} onChange={e=>setAmount(e.target.value)} /></div>
        </div>
        <label className="lbl mt-2">Контрагент</label><input className="input" value={cp} onChange={e=>setCp(e.target.value)} />
        <label className="lbl mt-2">Назначение</label><input className="input" value={note} onChange={e=>setNote(e.target.value)} />
        <div className="flex gap-2 mt-3">
          <button className="btn-line" onClick={()=>send("in")}>Приход денег</button>
          <button className="btn" onClick={()=>send("out")}>Расход денег</button>
        </div>
        {msg && <div className="mt-2 text-emerald-400 text-sm">{msg}</div>}
      </div>

      <div className="card">
        <h3 className="text-lg mb-2">Баланс</h3>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="card"><div className="text-slate-400 text-sm">Касса</div><div className="text-xl font-bold">{bal.cash.toFixed(2)}</div></div>
          <div className="card"><div className="text-slate-400 text-sm">Банк</div><div className="text-xl font-bold">{bal.bank.toFixed(2)}</div></div>
          <div className="card"><div className="text-slate-400 text-sm">Итого</div><div className="text-xl font-bold">{bal.total.toFixed(2)}</div></div>
        </div>
        <button className="btn-line mt-3" onClick={load}>Обновить</button>
        <h4 className="text-lg mt-4 mb-2">Последние операции</h4>
        <table className="table">
          <thead><tr><th>Дата</th><th>Счёт</th><th>Тип</th><th className="text-right">Сумма</th><th>Контрагент</th><th>Примечание</th></tr></thead>
          <tbody>
            {last.map((r,i)=>(
              <tr key={i}>
                <td>{new Date(r.date).toISOString().slice(0,10)}</td>
                <td>{r.account==="cash"?"Касса":"Банк"}</td>
                <td>{r.direction==="in"?"Приход":"Расход"}</td>
                <td className="text-right">{Number(r.amount).toFixed(2)}</td>
                <td>{r.counterparty||""}</td>
                <td>{r.note||""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
