/** Typed Frontend API Client for FreshCart Backend Services */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Product {
  id: string;
  sku: string;
  name: string;
  slug: string;
  brand: string;
  description?: string;
  category_id: string;
  unit: string;
  base_price: number;
  sale_price: number;
  is_variable_weight: boolean;
  weight_increment: number;
  weight_tolerance_pct: number;
  is_organic: boolean;
  is_vegetarian: boolean;
  rating_average: number;
  rating_count: number;
  primary_image_url?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  level: number;
  subcategories?: Category[];
}

export interface CartResponse {
  cart_id: string;
  vendor_groups: Array<{
    vendor_id?: string;
    vendor_name: string;
    items: Array<{
      id: string;
      product_id: string;
      product_name: string;
      brand: string;
      unit: string;
      unit_price: number;
      quantity: number;
      item_total: number;
      is_variable_weight: boolean;
      image_url?: string;
    }>;
    vendor_subtotal: number;
  }>;
  total_items: number;
  subtotal: number;
  coupon_code?: string;
  discount_amount: number;
  tax_estimate: number;
  delivery_fee_estimate: number;
  grand_total: number;
}

export interface DashboardMetrics {
  gross_merchandise_value: number;
  total_orders_count: number;
  completed_orders_count: number;
  active_customers_count: number;
  active_vendors_count: number;
  average_order_value: number;
  return_rate_percentage: number;
  top_categories: Array<{
    category_id: string;
    category_name: string;
    revenue: number;
    units_sold: number;
  }>;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: "An unexpected error occurred" }));
    throw new Error(err.message || err.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Products & Categories
  getCategories: () => request<Category[]>("/categories/tree"),
  getProducts: (params?: { category_id?: string; is_organic?: boolean; search?: string }) => {
    const q = new URLSearchParams();
    if (params?.category_id) q.set("category_id", params.category_id);
    if (params?.is_organic !== undefined) q.set("is_organic", String(params.is_organic));
    if (params?.search) q.set("q", params.search);
    return request<{ items: Product[]; total: number }>(`/products?${q.toString()}`);
  },
  getProductBySlug: (slug: string) => request<Product>(`/products/slug/${slug}`),

  // Search
  instantSearch: (query: string) => request<{ results: Product[] }>(`/search?q=${encodeURIComponent(query)}`),

  // Cart
  getCart: () => request<CartResponse>("/cart"),
  addToCart: (productId: string, quantity: number, notes?: string) =>
    request<CartResponse>("/cart/items", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity, notes }),
    }),
  updateCartItem: (itemId: string, quantity: number) =>
    request<CartResponse>(`/cart/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),
  removeFromCart: (itemId: string) =>
    request<CartResponse>(`/cart/items/${itemId}`, {
      method: "DELETE",
    }),
  applyCoupon: (code: string) =>
    request<CartResponse>("/cart/apply-coupon", {
      method: "POST",
      body: JSON.stringify({ coupon_code: code }),
    }),

  // Orders & Checkout
  checkout: (payload: { delivery_address_id: string; delivery_slot_id?: string; payment_method: string }) =>
    request<any>("/orders/checkout", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getOrder: (orderId: string) => request<any>(`/orders/${orderId}`),
  getMyOrders: () => request<any[]>("/orders"),

  // Admin KPIs
  getDashboardMetrics: () => request<DashboardMetrics>("/admin/analytics/dashboard"),
  getAuditLogs: () => request<any[]>("/admin/audit-logs"),
};
