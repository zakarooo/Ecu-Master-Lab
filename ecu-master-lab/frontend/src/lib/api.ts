const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    throw new Error("Non autorisé");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Erreur serveur" }));
    throw new Error(error.detail || "Erreur serveur");
  }

  return res.json();
}

export const api = {
  request,
  auth: {
    register: (data: any) => request("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
    login: (data: any) => request("/api/auth/login", { method: "POST", body: JSON.stringify(data) }),
    me: () => request("/api/auth/me"),
    updateProfile: (data: any) => request("/api/auth/profile", { method: "PUT", body: JSON.stringify(data) }),
    changePassword: (data: any) => request("/api/auth/password", { method: "PUT", body: JSON.stringify(data) }),
    verifyEmail: (token: string) => request("/api/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) }),
    forgotPassword: (email: string) => request("/api/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
    resetPassword: (token: string, new_password: string) => request("/api/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password }) }),
  },
  projects: {
    list: () => request("/api/projects"),
    get: (id: number) => request(`/api/projects/${id}`),
    create: (data: any) => request("/api/projects", { method: "POST", body: JSON.stringify(data) }),
    upload: (id: number, file: File) => {
      const form = new FormData();
      form.append("file", file);
      return request(`/api/projects/${id}/upload`, { method: "POST", body: form });
    },
    setModifications: (id: number, data: any) =>
      request(`/api/projects/${id}/modifications`, { method: "POST", body: JSON.stringify(data) }),
    process: (id: number) => request(`/api/projects/${id}/process`, { method: "POST" }),
    downloadOriginal: (id: number) => `/api/projects/${id}/download-original`,
    downloadVersion: (id: number, versionId: number) => `/api/projects/${id}/download/${versionId}`,
    downloadModified: (id: number) => `/api/projects/${id}/download`,
    analysis: (id: number) => request(`/api/projects/${id}/analysis`),
    versions: (id: number) => request(`/api/projects/${id}/versions`),
  },
  admin: {
    stats: () => request("/api/admin/stats"),
    users: (params?: string) => request(`/api/admin/users${params ? `?${params}` : ""}`),
    projects: (params?: string) => request(`/api/admin/projects${params ? `?${params}` : ""}`),
    updateUser: (id: number, data: any) => request(`/api/admin/users/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteUser: (id: number) => request(`/api/admin/users/${id}`, { method: "DELETE" }),
    auditLogs: (params?: string) => request(`/api/admin/audit-logs${params ? `?${params}` : ""}`),
    deleteProject: (id: number) => request(`/api/admin/projects/${id}`, { method: "DELETE" }),
    transferProject: (id: number, data: any) => request(`/api/admin/projects/${id}/transfer`, { method: "POST", body: JSON.stringify(data) }),
  },
  expert: {
    pendingReview: () => request("/api/expert/projects/pending-review"),
    approve: (id: number) => request(`/api/expert/projects/${id}/approve`, { method: "POST" }),
    reject: (id: number, data: any) => request(`/api/expert/projects/${id}/reject`, { method: "POST", body: JSON.stringify(data) }),
  },
  v2: {
    manufacturers: {
      list: (params?: string) => request(`/api/v2/referentiel/manufacturers${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/referentiel/manufacturers/${id}`),
      create: (data: any) => request("/api/v2/referentiel/manufacturers", { method: "POST", body: JSON.stringify(data) }),
    },
    ecuModels: {
      list: (params?: string) => request(`/api/v2/referentiel/ecu-models${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/referentiel/ecu-models/${id}`),
    },
    processors: {
      list: (params?: string) => request(`/api/v2/referentiel/processors${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/referentiel/processors/${id}`),
    },
    protocols: {
      list: (params?: string) => request(`/api/v2/referentiel/protocols${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/referentiel/protocols/${id}`),
    },
    ecuFiles: {
      list: (params?: string) => request(`/api/v2/analysis/files${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/analysis/files/${id}`),
    },
    analyses: {
      list: (params?: string) => request(`/api/v2/analysis/analyses${params ? `?${params}` : ""}`),
      get: (id: number) => request(`/api/v2/analysis/analyses/${id}`),
      run: (fileId: number) => request(`/api/v2/analysis/analyses/${fileId}/run`, { method: "POST" }),
    },
    upload: (file: File, runAnalysis: boolean = false) => {
      const form = new FormData();
      form.append("file", file);
      form.append("run_analysis", String(runAnalysis));
      return request("/api/v2/analysis/upload", { method: "POST", body: form });
    },
    vehicleBrands: {
      list: (params?: string) => request(`/api/v2/vehicles/brands${params ? `?${params}` : ""}`),
    },
    vehicleModels: {
      list: (params?: string) => request(`/api/v2/vehicles/models${params ? `?${params}` : ""}`),
    },
    memoryLayouts: {
      list: (params?: string) => request(`/api/v2/memory/layouts${params ? `?${params}` : ""}`),
    },
    ecuSignatures: {
      list: (params?: string) => request(`/api/v2/signatures/ecu-signatures${params ? `?${params}` : ""}`),
    },
    mapCategories: {
      list: (params?: string) => request(`/api/v2/maps/categories${params ? `?${params}` : ""}`),
    },
    mapUnits: {
      list: (params?: string) => request(`/api/v2/maps/units${params ? `?${params}` : ""}`),
    },
    maps: {
      list: (params?: string) => request(`/api/v2/maps${params ? `?${params}` : ""}`),
    },
  },
};
