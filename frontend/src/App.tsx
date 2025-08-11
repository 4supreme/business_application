import React from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Catalog from "./pages/Catalog";
import Stock from "./pages/Stock";
import Purchase from "./pages/Purchase";
import Sale from "./pages/Sale";
import Cash from "./pages/Cash";
import Reports from "./pages/Reports";
import './index.css';

const Tab = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `px-3 py-2 rounded-full border border-slate-700 ${
        isActive ? "bg-blue-600 text-white" : "bg-[#0f172a] text-slate-200 hover:bg-slate-800"
      }`
    }
  >
    {children}
  </NavLink>
);

export default function App() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Business MVP — Панель</h1>
        <nav className="flex gap-2 flex-wrap">
          <Tab to="/purchase">Закуп</Tab>
          <Tab to="/sale">Продажа</Tab>
          <Tab to="/stock">Склад</Tab>
          <Tab to="/cash">Банк и касса</Tab>
          <Tab to="/reports">Руководство</Tab>
          <Tab to="/catalog">Каталог</Tab>
        </nav>
      </div>

      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/purchase" element={<Purchase />} />
        <Route path="/sale" element={<Sale />} />
        <Route path="/stock" element={<Stock />} />
        <Route path="/cash" element={<Cash />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/catalog" element={<Catalog />} />
      </Routes>
    </div>
  );
}