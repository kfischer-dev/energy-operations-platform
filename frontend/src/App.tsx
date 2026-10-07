import './App.css'
import ApiStatus from './components/ApiStatus'
import BalanceSummaryComponent from './components/BalanceSummary'

function App() {


  return (
    <>
      <div className="app-container">
        <h1>Hello, Energy Operations Platform!</h1>
        <p>Frontend connected successfully!</p>
      </div>
      <ApiStatus />
      <BalanceSummaryComponent />
    </>
  )
}

export default App
