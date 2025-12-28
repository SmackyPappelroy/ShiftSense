const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchWorkspaces(): Promise<string[]> {
  const response = await fetch(`${API_URL}/workspaces`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (!response.ok) {
    throw new Error('Failed to load')
  }
  const data = await response.json()
  return data.map((item: { name: string }) => item.name)
}

export async function fetchFindings(): Promise<string[]> {
  const response = await fetch(`${API_URL}/findings/1`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (!response.ok) {
    throw new Error('Failed to load')
  }
  const data = await response.json()
  return data.map((item: { title: string }) => item.title)
}
