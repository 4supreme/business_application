import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import type { Product } from "../lib/api";

type Row = { product_id: number | string; qty: number | string; price: number | string };

export default function Purchase() {
  // дата по умолчанию — сегодня
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [date, setDate] = useState<string>(today);

  // поставщик
  const [vendor, setVendor] = useState<string>("");

  // товарный справочник (для select)
  const [stock, setStock] = useState<Product[]>([]);

  // строки документа
  const [rows, setRows] = useState<Row[]>([{ product_id: "", qty: "", price: "" }]);

  // сообщения/статус для пользователя
  const [msg, setMsg] = useState<string>("");

  // загрузка товаров
  const loadStock = () => api.stock().then(setStock);
  useEffect(() => { loadStock(); }, []);

  const addRow = () => setRows(r => [...r, { product_id: "", qty: "", price: "" }]);

  const setRow = (i: number, patch: Partial<Row>) =>
    setRows(r => r.map((x, idx) => (idx === i ? { ...x, ...patch } : x)));

  // валидные позиции (числа)
  const items = rows
    .map(r => ({ product_id: Number(r.product_id), qty: Number(r.qty), price: Number(r.price) }))
    .filter(x => x.product_id && x.qty > 0 && x.price >= 0);

  const total = items.reduce((s, x) => s + x.qty * x.price, 0);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* Левая колонка — шапка */}
      <div className="card">
        <h3 className="mb-2">Сведения о поставщике</h3>

        <label className="lbl">Дата документа</label>
        <input
          className="input"
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
        />

        <label className="lbl">Поставщик</label>
        <input
          className="input"
          value={vendor}
          onChange={e => setVendor(e.target.value)}
          placeholder="Например: ТОО Алматы"
        />

        {msg && <div className="mt-3 text-sm text-emerald-400">{msg}</div>}
      </div>

      {/* Правая колонка — позиции */}
      <div className="card">
        <h3 className="mb-2">Позиции товаров</h3>

        {rows.map((r, i) => (
          <div key={i} className="grid grid-cols-3 gap-2 mb-2">
            <select
              className="input"
              value={r.product_id}
              onChange={e => setRow(i, { product_id: e.target.value })}
            >
              <option value="">Наименование товара…</option>
              {stock.map(p => (
                <option key={p.id} value={p.id}>{`#${p.id} — ${p.name}`}</option>
              ))}
            </select>

            <input
              className="input"
              placeholder="Количество"
              value={r.qty}
              onChange={e => setRow(i, { qty: e.target.value })}
              type="number"
              min="0"
              step="any"
            />

            <input
              className="input"
              placeholder="Цена"
              value={r.price}
              onChange={e => setRow(i, { price: e.target.value })}
              type="number"
              min="0"
              step="any"
            />
          </div>
        ))}

        <div className="flex gap-2">
          <button className="btn-line" onClick={addRow}>+ Позиция</button>

          <button
            className="btn"
            onClick={async () => {
              setMsg("");
              if (!vendor.trim()) { setMsg("Укажи поставщика"); return; }
              if (items.length === 0) { setMsg("Добавь хотя бы одну позицию"); return; }

              // черновик → проведение
              const draft = await api.createPurchase({
                date,
                vendor: vendor.trim(),
                items
              });
              const posted = await api.postDoc(draft.id);

              // сброс формы
              setRows([{ product_id: "", qty: "", price: "" }]);
              setMsg(`Проведено: № ${posted.number} (${posted.status})`);
              loadStock();
            }}
          >
            Провести приход
          </button>

          <div className="ml-auto text-sm text-slate-300">
            Итого: <b>{total.toFixed(2)}</b>
          </div>
        </div>
      </div>
    </div>
  );
}