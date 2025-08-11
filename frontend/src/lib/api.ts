const API_URL = "http://localhost:8000";

export type Product = {
  id: number;
  name: string;
  sku?: string;
  unit?: string;
  barcode?: string;
  qty: number;
  avg_cost: number;
};

export type DocItem = { product_id: number; qty: number; price: number };
export type Doc = {
  id: number;
  type: "purchase" | "sale";
  number?: string | null;
  date: string;
  partner?: string | null;
  status: "draft" | "posted" | "canceled";
  total: number;
  items: DocItem[];
};

const API = "http://localhost:8000";

async function j<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...init });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export const api = {
  products: (): Promise<Product[]> => j(`${API}/products`),
  createProduct: (x: { name: string; sku?: string | null; unit?: string | null; barcode?: string | null }): Promise<Product> =>
    j(`${API}/products`, { method: "POST", body: JSON.stringify(x) }),
  stock: (): Promise<Product[]> => j(`${API}/stock`),

  // документы
  createPurchase: (x: { date: string; vendor?: string | null; items: DocItem[] }): Promise<Doc> =>
    j(`${API}/purchase`, { method: "POST", body: JSON.stringify({ date: x.date, partner: x.vendor, items: x.items }) }),
  createSale: (x: { client?: string | null; items: DocItem[]; date?: string }): Promise<Doc> =>
    j(`${API}/sale`, { method: "POST", body: JSON.stringify({ date: x.date || new Date().toISOString().slice(0,10), partner: x.client, items: x.items }) }),

  getDoc: (id: number): Promise<Doc> => j(`${API}/docs/${id}`),
  postDoc: (id: number): Promise<Doc> => j(`${API}/docs/${id}/post`, { method: "POST" }),
  unpostDoc: (id: number): Promise<Doc> => j(`${API}/docs/${id}/unpost`, { method: "POST" }),
};