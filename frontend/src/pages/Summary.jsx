import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchSummary } from '../api'

function Summary() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchSummary()
        if (!cancelled) {
          setSummary(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
          setSummary(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return <div className="status status-loading">Loading summary…</div>
  }

  if (error) {
    return (
      <div className="status status-error">
        Could not load summary. {error}
      </div>
    )
  }

  if (!summary) {
    return null
  }

  const { subject_averages: subjectAverages, top_student: topStudent } = summary

  return (
    <section>
      <h2 className="page-title">Class Summary</h2>
      <p className="page-subtitle">
        Subject averages and the top student by total marks.
      </p>

      <h3 className="section-title">Subject Averages</h3>
      <div className="card-grid">
        {Object.entries(subjectAverages).map(([subject, average]) => (
          <div className="card" key={subject}>
            <p className="card-label">{subject}</p>
            <p className="card-value">{average ?? '—'}</p>
          </div>
        ))}
      </div>

      <h3 className="section-title">Top Student</h3>
      {topStudent ? (
        <div className="card card-highlight">
          <p className="card-label">Highest total</p>
          <p className="card-value">
            <Link to={`/students/${topStudent.admission_no}`}>
              {topStudent.name}
            </Link>
          </p>
          <p className="card-meta">
            {topStudent.admission_no} · total {topStudent.total}
          </p>
        </div>
      ) : (
        <div className="empty-state">
          <strong>No students available</strong>
          Import data to see the class summary.
        </div>
      )}
    </section>
  )
}

export default Summary
