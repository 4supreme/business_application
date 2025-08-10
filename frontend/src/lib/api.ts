export const API = "http://localhost:8000";

async function req<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(API + url, { headers: { "Content-Type": "application/json" }, ...init });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export type Product = { id:number; name:string; sku?:string; unit?:string; barcode?:string; qty_on_hand:number; avg_cost:number; };
export type VendorRow = { date:string; product_name:string; qty:number; price:number; total:number };

export const api = {
  stock: () => req<Product[]>("/stock/"),
  products: () => req<Product[]>("/products/"),
  createProduct: (body:any) => req<Product>("/products/", { method:"POST", body: JSON.stringify(body) }),

  recentVendors: () => req<string[]>("/vendors/recent"),
  vendorHistory: (vendor:string) => req<VendorRow[]>(`/purchase/vendor-history?vendor=${encodeURIComponent(vendor)}`),
  purchase: (body:any) => req<any>("/purchase/", { method:"POST", body: JSON.stringify(body) }),

  sale: (body:any) => req<any>("/sale/", { method:"POST", body: JSON.stringify(body) }),

  cashCreate: (body:any) => req<any>("/treasury/txn", { method:"POST", body: JSON.stringify(body) }),
  cashBalance: () => req<{cash:number;bank:number;total:number}>("/treasury/balance"),
  cashLast: () => req<any[]>("/treasury/last"),
};
