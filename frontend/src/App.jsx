import { useState } from 'react'
import './App.css'
import Canvas from './components/canvas1'
import Sidebar from './components/sidebar'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="h-screen w-screen grid" style={{ gridTemplateColumns: '250px 1fr 300px' }}>
      
      {/* Left Sidebar */}
      <aside className="p-4 border-r border-gray-700">
        <Sidebar/>
      </aside>

      {/* Main Canvas */}
      <main className="overflow-auto">
        <div className="flex flex-col h-full w-full border border-gray-400 shadow-xl p-4 rounded-lg bg-white">
          <Canvas/>
        </div>
      </main>

      {/* Right Sidebar */}
      <aside className="p-4 border-l border-gray-700">
        <p>Properties / Settings</p>
      </aside>

    </div>
  )
}

export default App
