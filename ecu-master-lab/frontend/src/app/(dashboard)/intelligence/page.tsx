"use client";

import { useState, useEffect, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ecu-backend-production.up.railway.app";

interface ECUModel {
  name: string;
  map_count: number;
  categories: number;
}

interface SearchResult {
  id: number;
  name: string;
  category: string;
  ecu_model: string;
  offset_hex: string;
  offset_dec: number;
  size_bytes: number;
  unit: string;
  similarity: number;
}

interface QualityReport {
  overall_score: number;
  total_maps: number;
  total_ecus: number;
  total_axes: number;
  findings: Array<{
    category: string;
    severity: string;
    message: string;
    count: number;
  }>;
  score_breakdown: Record<string, number>;
}

interface Statistics {
  total_maps: number;
  total_axes: number;
  total_strings: number;
  total_checksums: number;
  total_segments: number;
  total_ecu_models: number;
  total_categories: number;
  pgvector_available: boolean;
  top_categories: Array<{ name: string; count: number }>;
  top_ecus: Array<{ name: string; count: number }>;
}

export default function IntelligenceDashboard() {
  const [activeTab, setActiveTab] = useState<"overview" | "search" | "quality" | "identify">("overview");
  const [ecus, setEcus] = useState<ECUModel[]>([]);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [quality, setQuality] = useState<QualityReport | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchFilter, setSearchFilter] = useState({ ecu: "", category: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/knowledge/statistics`);
      const data = await res.json();
      if (data.status === "success") {
        setStats(data.statistics);
      }
    } catch (e) {
      setError("Failed to load statistics");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchECUs = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ecu/list`);
      const data = await res.json();
      if (data.status === "success") {
        setEcus(data.ecus);
      }
    } catch (e) {
      setError("Failed to load ECU list");
    }
  }, []);

  const fetchQuality = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/knowledge/quality`);
      const data = await res.json();
      if (data.status === "success") {
        setQuality(data.report);
      }
    } catch (e) {
      setError("Failed to load quality report");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    fetchECUs();
  }, [fetchStats, fetchECUs]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ q: searchQuery, limit: "50" });
      if (searchFilter.ecu) params.set("ecu", searchFilter.ecu);
      if (searchFilter.category) params.set("category", searchFilter.category);

      const res = await fetch(`${API_BASE}/api/knowledge/search?${params}`);
      const data = await res.json();
      if (data.status === "success") {
        setSearchResults(data.results);
      }
    } catch (e) {
      setError("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const getSeverityColor = (severity: string) => {
    if (severity === "critical") return "bg-red-500/20 text-red-400 border-red-500/30";
    if (severity === "warning") return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    return "bg-blue-500/20 text-blue-400 border-blue-500/30";
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-cyan-400">ECU Intelligence Dashboard</h1>
          <p className="text-gray-400 mt-2">Knowledge base overview, search, and analysis</p>
        </header>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6 text-red-400">
            {error}
          </div>
        )}

        <nav className="flex gap-2 mb-6">
          {(["overview", "search", "quality", "identify"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                setError("");
                if (tab === "quality") fetchQuality();
              }}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === tab
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>

        {activeTab === "overview" && (
          <div className="space-y-6">
            {stats && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard label="Total Maps" value={stats.total_maps} color="cyan" />
                  <StatCard label="ECU Models" value={stats.total_ecu_models} color="green" />
                  <StatCard label="Map Axes" value={stats.total_axes} color="purple" />
                  <StatCard label="Categories" value={stats.total_categories} color="yellow" />
                  <StatCard label="Known Strings" value={stats.total_strings} color="blue" />
                  <StatCard label="Checksums" value={stats.total_checksums} color="orange" />
                  <StatCard label="Memory Segments" value={stats.total_segments} color="red" />
                  <StatCard
                    label="pgvector"
                    value={stats.pgvector_available ? "Active" : "Fallback"}
                    color={stats.pgvector_available ? "green" : "yellow"}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h3 className="text-lg font-semibold text-cyan-400 mb-4">Top ECU Models</h3>
                    <div className="space-y-2">
                      {stats.top_ecus?.map((ecu, i) => (
                        <div key={i} className="flex justify-between items-center">
                          <span className="text-gray-300 text-sm">{ecu.name}</span>
                          <span className="text-cyan-400 text-sm font-mono">{ecu.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h3 className="text-lg font-semibold text-cyan-400 mb-4">Top Categories</h3>
                    <div className="space-y-2">
                      {stats.top_categories?.map((cat, i) => (
                        <div key={i} className="flex justify-between items-center">
                          <span className="text-gray-300 text-sm">{cat.name}</span>
                          <span className="text-cyan-400 text-sm font-mono">{cat.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}

            {ecus.length > 0 && (
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold text-cyan-400 mb-4">All ECU Models ({ecus.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {ecus.map((ecu, i) => (
                    <div key={i} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <div className="text-sm font-medium text-white truncate">{ecu.name}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {ecu.map_count} maps · {ecu.categories} categories
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "search" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <h3 className="text-lg font-semibold text-cyan-400 mb-4">Search Knowledge Base</h3>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search maps... (e.g. boost pressure, injection quantity)"
                  className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <input
                  type="text"
                  value={searchFilter.ecu}
                  onChange={(e) => setSearchFilter({ ...searchFilter, ecu: e.target.value })}
                  placeholder="ECU filter"
                  className="w-40 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <input
                  type="text"
                  value={searchFilter.category}
                  onChange={(e) => setSearchFilter({ ...searchFilter, category: e.target.value })}
                  placeholder="Category"
                  className="w-40 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="bg-cyan-500 hover:bg-cyan-600 text-white font-medium px-6 py-2 rounded-lg transition disabled:opacity-50"
                >
                  {loading ? "Searching..." : "Search"}
                </button>
              </div>
            </div>

            {searchResults.length > 0 && (
              <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                <h3 className="text-lg font-semibold text-cyan-400 mb-4">
                  Results ({searchResults.length})
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-2 text-gray-400">Name</th>
                        <th className="text-left py-2 text-gray-400">Category</th>
                        <th className="text-left py-2 text-gray-400">ECU</th>
                        <th className="text-left py-2 text-gray-400">Offset</th>
                        <th className="text-left py-2 text-gray-400">Size</th>
                        <th className="text-left py-2 text-gray-400">Unit</th>
                        <th className="text-left py-2 text-gray-400">Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {searchResults.map((r, i) => (
                        <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50">
                          <td className="py-2 text-white">{r.name}</td>
                          <td className="py-2 text-gray-300">{r.category}</td>
                          <td className="py-2 text-gray-300">{r.ecu_model}</td>
                          <td className="py-2 text-gray-400 font-mono text-xs">{r.offset_hex}</td>
                          <td className="py-2 text-gray-400">{r.size_bytes}B</td>
                          <td className="py-2 text-gray-400">{r.unit || "-"}</td>
                          <td className="py-2">
                            <span className={`font-mono text-xs ${r.similarity > 0.7 ? "text-green-400" : r.similarity > 0.3 ? "text-yellow-400" : "text-gray-500"}`}>
                              {(r.similarity * 100).toFixed(0)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "quality" && (
          <div className="space-y-6">
            {quality ? (
              <>
                <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-cyan-400">Quality Score</h3>
                    <span className={`text-4xl font-bold ${getScoreColor(quality.overall_score)}`}>
                      {quality.overall_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        quality.overall_score >= 80 ? "bg-green-500" :
                        quality.overall_score >= 60 ? "bg-yellow-500" : "bg-red-500"
                      }`}
                      style={{ width: `${quality.overall_score}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard label="Maps" value={quality.total_maps} color="cyan" />
                  <StatCard label="ECUs" value={quality.total_ecus} color="green" />
                  <StatCard label="Axes" value={quality.total_axes} color="purple" />
                  <StatCard label="Findings" value={quality.findings.length} color="yellow" />
                </div>

                {quality.findings.length > 0 && (
                  <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h3 className="text-lg font-semibold text-cyan-400 mb-4">Findings</h3>
                    <div className="space-y-3">
                      {quality.findings.map((f, i) => (
                        <div key={i} className={`border rounded-lg p-3 ${getSeverityColor(f.severity)}`}>
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{f.category}</span>
                            <span className="text-xs">{f.count} issues</span>
                          </div>
                          <p className="text-sm mt-1 opacity-80">{f.message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(quality.score_breakdown).length > 0 && (
                  <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                    <h3 className="text-lg font-semibold text-cyan-400 mb-4">Score Breakdown</h3>
                    <div className="space-y-3">
                      {Object.entries(quality.score_breakdown).map(([key, score], i) => (
                        <div key={i} className="flex items-center gap-3">
                          <span className="w-40 text-sm text-gray-300">{key}</span>
                          <div className="flex-1 bg-gray-800 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${score >= 80 ? "bg-green-500" : score >= 60 ? "bg-yellow-500" : "bg-red-500"}`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                          <span className={`text-sm font-mono ${getScoreColor(score)}`}>{score.toFixed(0)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center text-gray-500 py-12">
                {loading ? "Loading quality report..." : "Click Quality tab to load report"}
              </div>
            )}
          </div>
        )}

        {activeTab === "identify" && (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h3 className="text-lg font-semibold text-cyan-400 mb-4">Upload ECU Binary for Identification</h3>
            <FileUpload />
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  const colorMap: Record<string, string> = {
    cyan: "border-cyan-500/30 text-cyan-400",
    green: "border-green-500/30 text-green-400",
    purple: "border-purple-500/30 text-purple-400",
    yellow: "border-yellow-500/30 text-yellow-400",
    blue: "border-blue-500/30 text-blue-400",
    orange: "border-orange-500/30 text-orange-400",
    red: "border-red-500/30 text-red-400",
  };

  return (
    <div className={`bg-gray-900 rounded-xl p-4 border ${colorMap[color] || colorMap.cyan}`}>
      <div className="text-xs text-gray-400 uppercase tracking-wide">{label}</div>
      <div className={`text-2xl font-bold mt-1 ${colorMap[color]?.split(" ")[1] || "text-cyan-400"}`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
    </div>
  );
}

function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://ecu-backend-production.up.railway.app";

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/ecu/analyze?use_damos=true`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.status === "success") {
        setResult(data.analysis);
      } else {
        setError(data.detail || "Analysis failed");
      }
    } catch (e) {
      setError("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-cyan-500 file:text-white file:cursor-pointer"
        />
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="bg-cyan-500 hover:bg-cyan-600 text-white font-medium px-6 py-2 rounded-lg transition disabled:opacity-50"
        >
          {uploading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {result.ecu_identification && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-cyan-400 font-semibold mb-2">ECU Identification</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-gray-400">Name:</span> <span className="text-white">{result.ecu_identification.name}</span></div>
                <div><span className="text-gray-400">Family:</span> <span className="text-white">{result.ecu_identification.family}</span></div>
                <div><span className="text-gray-400">Confidence:</span> <span className="text-green-400">{result.ecu_identification.confidence}%</span></div>
                <div><span className="text-gray-400">Method:</span> <span className="text-white">{result.ecu_identification.match_method}</span></div>
                <div><span className="text-gray-400">DAMOS:</span> <span className="text-white">{result.ecu_identification.damos_match || "None"}</span></div>
              </div>
            </div>
          )}

          {result.detected_maps && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-cyan-400 font-semibold mb-2">
                Detected Maps ({result.detected_maps.total})
              </h4>
              <div className="text-sm text-gray-300 mb-2">
                Confidence: {result.detected_maps.confidence}% · DAMOS maps: {result.damos_map_count}
              </div>
              {result.detected_maps.maps?.length > 0 && (
                <div className="overflow-x-auto max-h-64 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-1 text-gray-400">Name</th>
                        <th className="text-left py-1 text-gray-400">Category</th>
                        <th className="text-left py-1 text-gray-400">Offset</th>
                        <th className="text-left py-1 text-gray-400">Size</th>
                        <th className="text-left py-1 text-gray-400">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.detected_maps.maps.map((m: any, i: number) => (
                        <tr key={i} className="border-b border-gray-800">
                          <td className="py-1 text-white">{m.name}</td>
                          <td className="py-1 text-gray-300">{m.category}</td>
                          <td className="py-1 text-gray-400 font-mono">{m.offset}</td>
                          <td className="py-1 text-gray-400">{m.size}B</td>
                          <td className="py-1">
                            <span className={`px-1 rounded text-xs ${m.status === "active" ? "bg-green-500/20 text-green-400" : "bg-gray-600 text-gray-400"}`}>
                              {m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {result.recommendations?.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-cyan-400 font-semibold mb-2">Recommendations</h4>
              <ul className="space-y-1 text-sm text-gray-300">
                {result.recommendations.map((r: string, i: number) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
