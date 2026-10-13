import { BrowserRouter, Routes, Route } from 'react-router';
import { MainLayout } from './layout/MainLayout'
import { Dashboard } from './pages/Dashboard'
import { Assets } from './pages/Assets'
import './App.css'
import { Simulation } from './pages/Simulation'
import { Balance } from './pages/Balance'

function App() {


  return (
    <>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/balance" element={<Balance />} />
            <Route path="/simulation" element={<Simulation />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </>
  )
}

export default App
