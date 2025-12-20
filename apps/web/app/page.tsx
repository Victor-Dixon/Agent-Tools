export default function HomePage() {
  return (
    <main className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">Family Focus Board</h1>
        <p className="text-slate-300">One board. One timer. One team.</p>
      </header>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-medium">MVP scaffold is live</h2>
        <p className="mt-2 text-sm text-slate-300">
          Next steps: connect to the API, render boards/lists/cards, and bind the shared Focus Room
          timer state to a single source-of-truth.
        </p>
      </section>
    </main>
  );
}

