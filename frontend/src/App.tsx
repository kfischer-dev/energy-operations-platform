import { BrowserRouter, Routes, Route } from 'react-router';
import { MainLayout } from './layout/MainLayout'
import { Dashboard } from './pages/Dashboard'
import { Assets } from './pages/Assets'
import './App.css'
import { Simulation } from './pages/Simulation'
import { Balance } from './pages/Balance'
import { HeaderDesignTest } from './pages/HeaderDesignTest'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/design-test" element={<HeaderDesignTest />} />
        <Route path="*" element={
          <MainLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/assets" element={<Assets />} />
              <Route path="/balance" element={<Balance />} />
              <Route path="/simulation" element={<Simulation />} />
            </Routes>
          </MainLayout>
        } />
      </Routes>
    </BrowserRouter>
  )
}

export default App
