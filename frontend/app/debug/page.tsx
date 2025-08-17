'use client'

import { useState } from 'react'

export default function DebugPage() {
  const [results, setResults] = useState<any>({})
  const [loading, setLoading] = useState(false)

  const testAPI = async () => {
    setLoading(true)
    const results: any = {}
    
    try {
      console.log('Backend URL:', process.env.NEXT_PUBLIC_BACKEND_URL)
      results.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL
      
      // Test basic health
      const healthResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/`)
      results.health = {
        status: healthResponse.status,
        data: await healthResponse.json()
      }
      
      // Test songs master
      const songsResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/songs/master`)
      const songsData = await songsResponse.json()
      results.songsMaster = {
        status: songsResponse.status,
        count: songsData.length,
        sample: songsData[0]
      }
      
      // Test songs (performances)
      const performancesResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/songs`)
      const performancesData = await performancesResponse.json()
      results.performances = {
        status: performancesResponse.status,
        count: performancesData.length,
        sample: performancesData[0]
      }
      
    } catch (error) {
      results.error = {
        message: error.message,
        stack: error.stack
      }
    }
    
    setResults(results)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl font-bold mb-4">API Debug Page</h1>
      
      <button 
        onClick={testAPI}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded mb-4"
      >
        {loading ? 'Testing...' : 'Test API'}
      </button>
      
      <pre className="bg-gray-800 p-4 rounded overflow-auto">
        {JSON.stringify(results, null, 2)}
      </pre>
    </div>
  )
}