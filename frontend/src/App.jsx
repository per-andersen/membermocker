import React from 'react';
import DataSetPage from './pages/DataSetPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <header className="mb-8 flex flex-col items-center">
          <img src="/assets/dark_theme_logo.png" alt="MemberMocker" className="h-36" />
          <p className="mt-2 text-gray-400 text-center">Generate and manage mock membership data for testing</p>
        </header>
        <main>
          <DataSetPage />
        </main>
      </div>
    </div>
  );
}

export default App;