const toISO = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const addDays = (isoOrDate, n) => {
  const d = typeof isoOrDate === 'string'
    ? new Date(isoOrDate + 'T00:00:00')
    : new Date(isoOrDate)
  d.setDate(d.getDate() + n)
  return d
}

// Always Mon–Sun weekly period
export function getCurrentPeriod() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dayOfWeek = (today.getDay() + 6) % 7 // Mon=0 … Sun=6
  const monday = addDays(today, -dayOfWeek)
  return { start: toISO(monday), end: toISO(addDays(monday, 6)) }
}

export function formatDate(iso) {
  const d = new Date(iso + 'T00:00:00')
  return d.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function formatTime(hhmm) {
  const [h, m] = hhmm.split(':').map(Number)
  const suffix = h >= 12 ? 'pm' : 'am'
  const hour = h % 12 || 12
  return `${hour}:${m.toString().padStart(2, '0')}${suffix}`
}

export function todayISO() {
  return toISO(new Date())
}
