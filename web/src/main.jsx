import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { drivers, formatLap, predictLap, tracks, weather } from "./prediction";
import "./style.css";

const repository = "https://github.com/myctruongg/f1-lap-time";
const features = [
  {
    route: "lap-time",
    navLabel: "Lap Time",
    title: "Lap Time Predictor",
    summary: "Estimate a lap time for a driver, circuit, and weather condition.",
    action: "Open lap predictor",
    Page: LapTimePage,
  },
  {
    route: "win-probability",
    navLabel: "Win / Loss",
    title: "Win / Loss Probability",
    summary: "Explore a driver's chances of winning a race.",
    action: "Coming soon",
    Page: WinProbabilityPage,
  },
];

const defaultSetup = { track: "bahrain", driver: "verstappen", condition: "dry" };

function CircuitMap({ circuit }) {
  const canvas = useRef(null);

  useEffect(() => {
    const context = canvas.current.getContext("2d");
    context.clearRect(0, 0, 600, 400);
    context.save();
    context.scale(2, 2);
    context.lineJoin = "round";
    context.lineCap = "round";
    context.beginPath();
    circuit.outline.forEach(([x, y], index) => {
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.closePath();
    context.lineWidth = 12;
    context.strokeStyle = "#40262b";
    context.stroke();
    context.lineWidth = 4;
    context.strokeStyle = "#ff5056";
    context.stroke();
    context.restore();
  }, [circuit]);

  return (
    <canvas ref={canvas} width="600" height="400" className="mx-auto block h-auto w-full max-w-[390px]"
      role="img" aria-label={`Schematic outline of ${circuit.name}`} />
  );
}

function SelectField({ label, value, options, onChange }) {
  return (
    <label className="block">
      <span className="field-label">{label}</span>
      <span className="select-wrap mt-2 block">
        <select value={value} onChange={(event) => onChange(event.target.value)}
          className="field w-full appearance-none rounded-lg px-4 py-3.5 pr-10">
          {Object.entries(options).map(([key, option]) => (
            <option key={key} value={key}>{option.name}</option>
          ))}
        </select>
      </span>
    </label>
  );
}

function LapTimePage() {
  const [setup, setSetup] = useState(defaultSetup);
  const [result, setResult] = useState(null);
  const circuit = tracks[setup.track];

  function update(key, value) {
    setSetup({ ...setup, [key]: value });
    setResult(null);
  }

  function submit(event) {
    event.preventDefault();
    setResult(predictLap(setup));
  }

  return (
    <main className="mx-auto max-w-6xl px-5 pb-12 pt-10 sm:px-9 sm:pt-14">
      <div className="mb-8 sm:mb-10">
        <h1 className="display text-6xl font-bold leading-[0.92] tracking-tight sm:text-8xl">Lap Time<br className="sm:hidden" /> Predictor<span className="text-[#ff5056]">.</span></h1>
        <p className="mt-4 max-w-xl text-[#b8b9c4]">Choose a circuit, driver, and weather to estimate a lap time.</p>
      </div>

      <div className="grid items-stretch gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={submit} className="panel flex flex-col gap-6 rounded-2xl p-5 sm:p-7">
          <h2 className="display text-3xl font-semibold">Lap setup</h2>
          <SelectField label="Track" options={tracks} value={setup.track} onChange={(value) => update("track", value)} />
          <SelectField label="Driver" options={drivers} value={setup.driver} onChange={(value) => update("driver", value)} />
          <fieldset>
            <legend className="field-label">Weather conditions</legend>
            <div className="mt-2 grid grid-cols-3 gap-2">
              {Object.entries(weather).map(([key, option]) => (
                <label key={key} className="relative cursor-pointer">
                  <input type="radio" name="weather" value={key} checked={setup.condition === key}
                    onChange={() => update("condition", key)} className="peer sr-only" />
                  <span className="weather-option flex flex-col items-center rounded-lg p-2.5 peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-white">
                    <span className="text-xl leading-none" aria-hidden="true">{option.symbol}</span>
                    <span className="mt-1.5 text-sm font-semibold">{option.name}</span>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <button className="mt-auto rounded-lg bg-[#ff5056] px-5 py-3.5 font-bold text-[#160e11] transition-colors hover:bg-[#ff7a7f] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white">
            Calculate lap time
          </button>
        </form>

        <section className="panel overflow-hidden rounded-2xl" aria-label="Circuit and prediction">
          <div className="map-panel px-5 pt-6 sm:px-7">
            <p className="field-label text-[#ff8387]">{circuit.profile}</p>
            <h2 className="display mt-1 text-3xl font-semibold">{circuit.name}</h2>
            <p className="mt-1 text-sm text-[#b8b9c4]">{circuit.location} · {circuit.length.toFixed(3)} km · {circuit.corners} corners</p>
            <CircuitMap circuit={circuit} />
          </div>
          <div className="border-t border-[#35353e] px-5 pb-6 pt-5 sm:px-7" aria-live="polite">
            <h2 className="field-label">Predicted lap time</h2>
            <p className="timer mt-1 font-mono text-5xl font-semibold tracking-tighter sm:text-6xl">
              {result === null ? <span className="text-[#888997]">—:—.———</span> : formatLap(result)}
            </p>
            <p className="mt-2 text-sm text-[#b8b9c4]">
              {result === null ? "Calculate a lap to see its estimated time." :
                `${drivers[setup.driver].name} · ${weather[setup.condition].name} conditions`}
            </p>
          </div>
        </section>
      </div>
      <p className="mt-5 text-sm text-[#a8a9b5]">Illustrative estimates from a demo formula. The telemetry model is still in development.</p>
    </main>
  );
}

function FeaturePreview({ route }) {
  if (route === "lap-time") {
    return <CircuitMap circuit={tracks.bahrain} />;
  }

  return (
    <div className="probability-preview" aria-hidden="true">
      <div className="probability-ring" />
      <div className="probability-lines"><span /><span /><span /></div>
    </div>
  );
}

function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-5 pb-12 pt-12 sm:px-9 sm:pt-17">
      <div className="max-w-3xl">
        <h1 className="display text-6xl font-bold leading-[0.92] tracking-tight sm:text-8xl">
          F1 Predictor<span className="text-[#ff5056]">.</span>
        </h1>
        <p className="mt-5 max-w-xl text-lg leading-7 text-[#b8b9c4]">
          Explore Formula 1 through predictions. See how the circuit, driver, and weather shape a lap-time estimate, with race win probabilities planned next.
        </p>
      </div>

      <section aria-label="Prediction tools" className="mt-8 grid gap-5 sm:mt-10 sm:grid-cols-2">
        {features.map((feature) => (
          <a key={feature.route} href={`#/${feature.route}`}
            className="feature-card panel group flex flex-col overflow-hidden rounded-2xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[#ff7378]">
            <div className="feature-visual map-panel flex h-44 items-center justify-center overflow-hidden sm:h-52">
              <div className="feature-art w-full max-w-[300px]">
                <FeaturePreview route={feature.route} />
              </div>
            </div>
            <div className="flex flex-1 flex-col border-t border-[#35353e] p-5 sm:p-6">
              <h2 className="display text-2xl font-semibold sm:text-3xl">{feature.title}</h2>
              <p className="mt-2 mb-5 text-[#b8b9c4]">{feature.summary}</p>
              <span className={`mt-auto w-fit rounded-lg px-4 py-2 text-sm font-bold ${feature.route === "lap-time" ? "bg-[#ff5056] text-[#160e11] group-hover:bg-[#ff7a7f]" : "border border-[#535463] text-[#dddde4]"}`}>
                {feature.action}
              </span>
            </div>
          </a>
        ))}
      </section>
    </main>
  );
}

function WinProbabilityPage() {
  return (
    <main className="mx-auto max-w-6xl px-5 py-14 sm:px-9">
      <h1 className="display text-5xl font-bold leading-tight sm:text-7xl">Win / Loss Probability</h1>
      <p className="mt-4 text-[#b8b9c4]">Coming soon. This tool will estimate a driver's chance of winning a race.</p>
      <a className="mt-7 inline-block rounded-lg bg-[#ff5056] px-4 py-2.5 font-bold text-[#160e11] hover:bg-[#ff7a7f]" href="#/lap-time">
        Try the lap predictor
      </a>
    </main>
  );
}

function getRoute() {
  const route = window.location.hash.slice(2);
  return features.some((feature) => feature.route === route) ? route : "home";
}

function App() {
  const [route, setRoute] = useState(getRoute);
  const feature = features.find((item) => item.route === route);
  const Page = feature?.Page ?? HomePage;

  useEffect(() => {
    function onNavigate() {
      setRoute(getRoute());
      window.scrollTo(0, 0);
    }
    window.addEventListener("hashchange", onNavigate);
    return () => window.removeEventListener("hashchange", onNavigate);
  }, []);

  useEffect(() => {
    document.title = feature ? `${feature.title} | F1 Predictor` : "F1 Predictor";
  }, [feature]);

  return (
    <>
      <header className="border-b border-[#2a2b33] bg-[#17181d]">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 gap-y-3 px-5 py-4 sm:px-9">
          <a href="#/" className="flex items-center gap-3 text-lg font-bold">
            <span className="flag" aria-hidden="true" /> F1 Predictor
          </a>
          <nav aria-label="Main navigation" className="flex flex-wrap gap-x-5 gap-y-2 text-sm font-semibold">
            <a href="#/" aria-current={route === "home" ? "page" : undefined}>Home</a>
            {features.map((feature) => (
              <a key={feature.route} href={`#/${feature.route}`} aria-current={route === feature.route ? "page" : undefined}>
                {feature.navLabel}
              </a>
            ))}
          </nav>
        </div>
      </header>
      <Page />
      <footer className="border-t border-[#2a2b33] px-5 sm:px-9">
        <div className="mx-auto flex max-w-[1080px] flex-wrap items-center justify-between gap-x-6 gap-y-2 py-5 text-sm text-[#b8b9c4]">
          <p>Built by Javier Herrera Jr and <a className="underline decoration-[#777886] underline-offset-4 hover:text-white" href="https://github.com/myctruongg">@myctruongg</a></p>
          <a className="font-semibold text-[#ff999d] underline-offset-4 hover:underline" href={repository}>Contribute on GitHub</a>
        </div>
      </footer>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
