"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { Car, ArrowRight, ArrowLeft, Loader2 } from "lucide-react";

const TOOLS = [
  "Autotuner", "Flex", "KESS", "KTAG", "CMD Flash", "PCM Flash",
  "BitBox", "Magic Motorsport", "FoxFlash", "Dimsport", "Autre",
];

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [vehicle, setVehicle] = useState({
    vehicle_make: "", vehicle_model: "", vehicle_year: "", vehicle_engine: "",
    vehicle_power: "", vehicle_ecu_type: "", vehicle_mileage: "", vehicle_gearbox: "", vehicle_vin: "",
  });
  const [toolUsed, setToolUsed] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, []);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const data = {
        name: projectName,
        ...vehicle,
        vehicle_year: vehicle.vehicle_year ? parseInt(vehicle.vehicle_year) : null,
        vehicle_mileage: vehicle.vehicle_mileage ? parseInt(vehicle.vehicle_mileage) : null,
        tool_used: toolUsed,
      };
      const res = await api.projects.create(data);
      router.push(`/projects/${res.id}`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">Nouveau Projet ECU</h1>
          <p className="text-gray-400 mb-8">Configurez votre projet de calibration</p>

          {/* Progress */}
          <div className="flex items-center gap-2 mb-8">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center gap-2 flex-1">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step >= s ? "bg-blue-500 text-white" : "bg-white/5 text-gray-500"
                }`}>{s}</div>
                {s < 3 && <div className={`flex-1 h-0.5 ${step > s ? "bg-blue-500" : "bg-white/10"}`} />}
              </div>
            ))}
          </div>

          <div className="glass rounded-2xl p-8">
            {step === 1 && (
              <div className="space-y-4 animate-fade-in">
                <h2 className="text-xl font-semibold text-white mb-4">Nom du Projet</h2>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Ex: Golf 7 GTD</label>
                  <input className="input-field" value={projectName}
                    onChange={(e) => setProjectName(e.target.value)} placeholder="Mon projet ECU" />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4 animate-fade-in">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Car className="w-5 h-5 text-blue-400" />
                  Informations Véhicule
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { key: "vehicle_make", label: "Constructeur", placeholder: "Volkswagen" },
                    { key: "vehicle_model", label: "Modèle", placeholder: "Golf 7" },
                    { key: "vehicle_year", label: "Année", placeholder: "2018", type: "number" },
                    { key: "vehicle_engine", label: "Motorisation", placeholder: "2.0 TDI" },
                    { key: "vehicle_power", label: "Puissance", placeholder: "184 ch" },
                    { key: "vehicle_ecu_type", label: "Type ECU", placeholder: "EDC17C64" },
                    { key: "vehicle_mileage", label: "Kilométrage", placeholder: "85000", type: "number" },
                    { key: "vehicle_gearbox", label: "Boîte", placeholder: "DSG6" },
                  ].map((field) => (
                    <div key={field.key}>
                      <label className="block text-sm text-gray-400 mb-1">{field.label}</label>
                      <input className="input-field" type={field.type || "text"}
                        placeholder={field.placeholder}
                        value={(vehicle as any)[field.key]}
                        onChange={(e) => setVehicle({ ...vehicle, [field.key]: e.target.value })} />
                    </div>
                  ))}
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">VIN (optionnel)</label>
                  <input className="input-field" placeholder="17 caractères"
                    value={vehicle.vehicle_vin}
                    onChange={(e) => setVehicle({ ...vehicle, vehicle_vin: e.target.value })} />
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4 animate-fade-in">
                <h2 className="text-xl font-semibold text-white mb-4">Outil de Lecture</h2>
                <div className="grid grid-cols-2 gap-3">
                  {TOOLS.map((tool) => (
                    <button key={tool} onClick={() => setToolUsed(tool)}
                      className={`p-3 rounded-xl border text-sm text-left transition-all ${
                        toolUsed === tool
                          ? "bg-blue-500/10 border-blue-500/40 text-blue-400"
                          : "bg-white/5 border-white/10 text-gray-400 hover:border-white/20"
                      }`}>
                      {tool}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
              {step > 1 ? (
                <button onClick={() => setStep(step - 1)} className="btn-secondary flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" /> Retour
                </button>
              ) : <div />}

              {step < 3 ? (
                <button onClick={() => setStep(step + 1)} className="btn-primary flex items-center gap-2"
                  disabled={step === 1 && !projectName}>
                  Suivant <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button onClick={handleCreate} disabled={loading} className="btn-primary flex items-center gap-2">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  Créer le Projet <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
