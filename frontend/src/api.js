const API_BASE = 'http://127.0.0.1:8000/api'

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}

export function fetchStudents(search = '') {
  const trimmed = search.trim()
  const query = trimmed ? `?search=${encodeURIComponent(trimmed)}` : ''
  return request(`/students/${query}`)
}

export function fetchStudent(admissionNo) {
  return request(`/students/${encodeURIComponent(admissionNo)}/`)
}

export function fetchSummary() {
  return request('/summary/')
}
