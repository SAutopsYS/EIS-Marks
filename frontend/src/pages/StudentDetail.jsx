import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchStudent } from '../api'

function renderMarks(marks) {
  if (marks === null) {
    return <span className="badge-absent">Absent</span>
  }
  return marks
}

function getInitials(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('')
}

function StudentDetail() {
  const { admissionNo } = useParams()
  const [student, setStudent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchStudent(admissionNo)
        if (!cancelled) {
          setStudent(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
          setStudent(null)
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
  }, [admissionNo])

  if (loading) {
    return <div className="status status-loading">Loading student…</div>
  }

  if (error) {
    return (
      <section>
        <div className="status status-error">
          Could not load student. {error}
        </div>
        <Link className="back-link" to="/">
          ← Back to students
        </Link>
      </section>
    )
  }

  if (!student) {
    return null
  }

  return (
    <section>
      <Link className="back-link" to="/">
        ← Back to students
      </Link>

      <div className="profile-card">
        <div className="profile-top">
          <div className="avatar" aria-hidden="true">
            {getInitials(student.name)}
          </div>
          <div>
            <h2 className="page-title">{student.name}</h2>
            <p className="page-subtitle">{student.admission_no}</p>
          </div>
        </div>

        <dl className="details">
          <div>
            <dt>Admission No</dt>
            <dd>{student.admission_no}</dd>
          </div>
          <div>
            <dt>Class</dt>
            <dd>{student.class}</dd>
          </div>
          <div>
            <dt>Section</dt>
            <dd>{student.section}</dd>
          </div>
          <div>
            <dt>Date of Birth</dt>
            <dd>{student.dob}</dd>
          </div>
          <div className="stat-emphasis">
            <dt>Total</dt>
            <dd>{student.total}</dd>
          </div>
          <div className="stat-emphasis">
            <dt>Average</dt>
            <dd>{student.average ?? '—'}</dd>
          </div>
        </dl>
      </div>

      <h3 className="section-title">Subject Marks</h3>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Subject</th>
              <th>Marks</th>
            </tr>
          </thead>
          <tbody>
            {student.marks.map((row) => (
              <tr key={row.subject}>
                <td>{row.subject}</td>
                <td>{renderMarks(row.marks)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export default StudentDetail
