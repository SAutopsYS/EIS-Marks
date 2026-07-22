import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchStudents } from '../api'

function StudentsList() {
  const [search, setSearch] = useState('')
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchStudents(search)
        if (!cancelled) {
          setStudents(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
          setStudents([])
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
  }, [search])

  return (
    <section>
      <h2 className="page-title">Students</h2>
      <p className="page-subtitle">
        Browse Class 6 students and open a profile for full marks.
      </p>

      <label className="search">
        Search by name
        <span className="search-field">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="e.g. Aditya"
          />
        </span>
      </label>

      {loading && (
        <div className="status status-loading">Loading students…</div>
      )}

      {error && (
        <div className="status status-error">
          Could not load students. {error}
        </div>
      )}

      {!loading && !error && students.length === 0 && (
        <div className="empty-state">
          <strong>No students found</strong>
          Try a different name, or clear the search box.
        </div>
      )}

      {!loading && !error && students.length > 0 && (
        <div className="table-wrap">
          <table className="data-table clickable-rows">
            <thead>
              <tr>
                <th>Admission No</th>
                <th>Name</th>
                <th>Class</th>
                <th>Section</th>
                <th>Average</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.admission_no}>
                  <td>
                    <Link to={`/students/${student.admission_no}`}>
                      {student.admission_no}
                    </Link>
                  </td>
                  <td>
                    <Link to={`/students/${student.admission_no}`}>
                      {student.name}
                    </Link>
                  </td>
                  <td>{student.class}</td>
                  <td>{student.section}</td>
                  <td>
                    <span className="avg-chip">
                      {student.average ?? '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default StudentsList
